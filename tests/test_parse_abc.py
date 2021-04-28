from unittest.mock import MagicMock, call

import pytest

from abc_buffer import AbcFormatError
from music import Barline
from options import Options
from parse_abc import ParseAbc
from tests.mock_file import MockFile
from tests.test_options import helper_set_options
from user_io import UserIo

abc_header_text = """
X:3
T: title
M:6/8
K:Em
A
"""

multi_tune_file = '''
X: 1
T: T1
K:Am
A

X:2
T:T2
K:Bm
B

X:3
T:T3
K:Cm
C

'''


@pytest.fixture
def options():
    return Options()


@pytest.fixture
def mock_file():
    return MockFile()


@pytest.fixture
def emitter():
    return MagicMock()


@pytest.fixture
def user_io():
    return UserIo()


@pytest.fixture
def parse_abc(emitter, user_io, options, mock_file):
    user_io.set_input_file(mock_file)
    return ParseAbc(emitter, user_io, options)


def mock_tune_body(mock_file, parse_abc, tune_body):
    mock_file.mock_content("X:123\nT: title\nK:G\n" + tune_body)
    parse_abc.parse_input()


def test_tune_header(mock_file, parse_abc, emitter):
    mock_file.mock_content(abc_header_text)
    parse_abc.parse_input()
    emitter.tune_start.assert_called_once_with(3)
    emitter.tune_title.assert_called_once_with("title")
    emitter.tune_time_sig.assert_called_once_with(6,8)

    emitter.tune_key_sig.assert_called_once_with("Em")


def test_no_tune_match(options, mock_file, parse_abc, emitter, user_io):
    mock_file.mock_content("X:1\nT:One Title\nK:G\nA")
    helper_set_options(options, ['','xOne'])
    parse_abc.parse_input()
    emitter.tune_start.assert_not_called()
    emitter.tune_title.assert_not_called()
    assert user_io.has_errors()


def test_partial_tune_match(options, mock_file, parse_abc, emitter):
    mock_file.mock_content('X:1\nT:ONE Title\nK:G\nA')
    helper_set_options(options, ['','ONE'])
    parse_abc.parse_input()
    emitter.tune_start.assert_called()
    emitter.tune_title.assert_called_once_with('ONE Title')


def test_ignore_lines_in_header(options, mock_file, parse_abc, emitter):
    mock_file.mock_content('X:1\n%%MIDI transpose 0\nQ:1/4 =120\nT:ONE Title\nK:G\nA')
    helper_set_options(options, ['','ONE Title'])
    parse_abc.parse_input()
    emitter.tune_start.assert_called()
    emitter.tune_title.assert_called_once_with('ONE Title')

def test_first_tune_is_used_if_no_tune_title(options, mock_file, parse_abc, emitter):
    mock_file.mock_content('X:1\nT:ONE Title\nK:G\nA')
    helper_set_options(options, ['',])
    parse_abc.parse_input()
    emitter.tune_start.assert_called()
    emitter.tune_title.assert_called_once_with('ONE Title')


def test_two_tiles_tune_match(options, mock_file, parse_abc, emitter):
    mock_file.mock_content('X:1\nT:ONE Title\nT:TWO Title\nK:G\nA')
    helper_set_options(options, ['','ONE'])
    parse_abc.parse_input()
    emitter.tune_start.assert_called()
    emitter.tune_title.assert_called_once_with('ONE Title')


def test_two_tiles_tune_match2(options, mock_file, parse_abc, emitter):
    mock_file.mock_content('X:1\nT:ONE Title\nT:TWO Title\nK:G\nA')
    helper_set_options(options, ['', 'TWO'])
    parse_abc.parse_input()
    emitter.tune_start.assert_called()
    emitter.tune_title.assert_called_once_with('TWO Title')


def test_tune_key_sig_using_abc_modes(mock_file, parse_abc, emitter):
    mock_file.mock_content("X:1\nT:t\nK:Dmix\nA")
    parse_abc.parse_input()
    emitter.tune_key_sig.assert_called_once_with("G")


def test_tune_key_sig_using_abc_modes_DDor(mock_file, parse_abc, emitter):
    mock_file.mock_content("X:1\nT:t\nK:Ddor\nA")
    parse_abc.parse_input()
    emitter.tune_key_sig.assert_called_once_with("Am")


def test_missing_tune_body(mock_file, parse_abc, emitter, user_io):
    user_io.error = MagicMock()
    mock_file.mock_content("X:3\nT:t\nK:Em\n")
    parse_abc.parse_input()
    user_io.error.assert_called()


def test_bad_id_header(mock_file, parse_abc, emitter, user_io):
    user_io.error = MagicMock()
    mock_file.mock_content("X: INVALID\nT: title\nK:G\n")
    parse_abc.parse_input()
    user_io.error.assert_called()
    emitter.tune_title.assert_not_called()


def test_finding_a_tune(mock_file, parse_abc, emitter, options):
    mock_file.mock_content(multi_tune_file)
    options.tune_search_name = "T2"
    parse_abc.parse_input()

    emitter.tune_start.assert_called_once_with(2)
    emitter.tune_title.assert_called_once_with("T2")


def test_notes_lengths_for_default_l(mock_file, parse_abc, emitter):
    mock_file.mock_content('X:1\nT:t\nK:G\n ab/C2d3e/2f/3g1/3z/4')
    parse_abc.parse_input()

    calls = [
        call("a", 96),
        call("b", 48),
        call("C", 192),
        call("d", 288),
        call("e", 48),
        call("f", 32),
        call("g", 32),
        call("z", 24)
    ]
    emitter.note.assert_has_calls(calls)


def test_notes_lengths_for_l_1_4(mock_file, parse_abc, emitter):

    mock_file.mock_content('X:1\nT:t\nL:1/4\nK:G\n ab/C2d3e/2f/3g1/3z/4')
    parse_abc.parse_input()

    calls = [
        call("a", 192),
        call("b", 96),
        call("C", 384),
        call("d", 576),
        call("e", 96),
        call("f", 64),
        call("g", 64),
        call("z", 48)
    ]
    emitter.note.assert_has_calls(calls)


def test_complete_tune(mock_file, parse_abc, emitter):
    mock_file.mock_content("""
X:3
T: title
K:Em
C|:"Gm7"d
F
""")
    parse_abc.parse_input()

    emitter.note.assert_has_calls([call("C", 96), call("d", 96), call("F", 96)])
    emitter.barline.assert_called_once_with(Barline.RepeatStart)
    emitter.chord_symbol.assert_called_once_with("Gm7")


def test_parse_tune_body(parse_abc, emitter):
    parse_abc._body = ['C|:"Gm7"d', 'F']
    parse_abc.process_body()

    emitter.note.assert_has_calls([call("C", 96), call("d", 96), call("F", 96)])
    emitter.barline.assert_called_once_with(Barline.RepeatStart)
    emitter.chord_symbol.assert_called_once_with("Gm7")


def test_valid_order_of_constructs_for_abc_note(parse_abc, emitter):
    parse_abc._body = [' | "Gm7"^d\'2']; parse_abc.process_body()

    emitter.note.assert_called_once_with("^d'", 192)
    emitter.barline.assert_called_once_with(Barline.Standard)
    emitter.chord_symbol.assert_called_once_with("Gm7")


def test_chord_in_wrong_place(parse_abc, emitter):
    with pytest.raises(AssertionError, match=r"unexpected element '|'"):
        parse_abc._body = ['"Gm7"|d2']; parse_abc.process_body()

    emitter.chord_symbol.assert_called_once_with("Gm7")
    emitter.note.assert_not_called()
    emitter.barline.assert_not_called()


def test_space_in_wrong_place(parse_abc, emitter):
    with pytest.raises(AbcFormatError, match=r"Badly formatted note"):
        parse_abc._body = ['|"Gm7"^ d2']; parse_abc.process_body()

    emitter.barline.assert_called_once_with(Barline.Standard)
    emitter.chord_symbol.assert_called_once_with('Gm7')
    emitter.note.assert_not_called()


def test_space_after_chord_is_ignored(parse_abc, emitter):
    parse_abc._body = ['|"Gm7" d2']; parse_abc.process_body()
    emitter.barline.assert_called_once_with(Barline.Standard)
    emitter.chord_symbol.assert_called_once_with('Gm7')
    emitter.note.assert_called_once_with('d', 192)


def test_duration_in_wrong_place(parse_abc, emitter):
    with pytest.raises(AssertionError, match=r"unexpected element '2'"):
        parse_abc._body = ['|"Gm7"2d']; parse_abc.process_body()

    emitter.barline.assert_called_once_with(Barline.Standard)
    emitter.chord_symbol.assert_called_once_with("Gm7")
    emitter.note.assert_not_called()


def test_triplets(parse_abc, emitter):
    parse_abc._body = ['"G"(3cBG A2']; parse_abc.process_body()

    emitter.chord_symbol.assert_called_once_with("G")
    emitter.note.assert_has_calls([call("c", 64), call("B", 64), call("G", 64), call("A", 192)])


def test_ignored_body_field_lines(parse_abc, emitter):
    parse_abc._body = ['%%MIDI control 7 96','A','K:Am',"I:rubbish",'%%MIDI control 7 96', 'B']; parse_abc.process_body()

    emitter.note.assert_has_calls([call("A", 96), call("B", 96)])
