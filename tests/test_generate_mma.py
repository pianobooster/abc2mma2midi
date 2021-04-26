import pytest


from generate_mma import GenerateMma
from options import Options
from parse_abc import ParseAbc
from tests.mock_file import MockFile
from user_io import UserIo


@pytest.fixture
def options():
    return Options()


@pytest.fixture
def mock_file():
    return MockFile()


@pytest.fixture
def user_io():
    return UserIo()


@pytest.fixture
def emitter(user_io, options):
    # Note GenerateMma IS the emitter (there may be more emitters in future)
    return GenerateMma(user_io, options)


@pytest.fixture
def parse_abc(emitter, user_io, options, mock_file):
    user_io.set_input_file(mock_file)
    return ParseAbc(emitter, user_io, options)


def mock_content(mock_file, parse_abc, content):
    mock_file.mock_content(content)
    parse_abc.parse_input()


def mock_tune(mock_file, parse_abc, tune):
    content = "X:3\nT: title\nK:D\n" + tune
    mock_content(mock_file, parse_abc, content)


def mock_68_tune(mock_file, parse_abc, tune):
    content = "X:3\nT: title\nM:6/8\nK:D\n" + tune
    mock_content(mock_file, parse_abc, content)


def assert_contains(user_io, text, expected_count=1):
    mma_output = user_io.output_text()
    repeat_count = mma_output.count(text)
    if repeat_count != expected_count:
        assert False, "text '{}' found {} times (expected {} times) in output:\n{}\n"\
            .format(text, repeat_count, expected_count, mma_output)


def assert_has_line(user_io, text, expected_count=1):
    line = text + '\n'
    mma_output = user_io.output_text()

    repeat_count = mma_output.count(line)
    if repeat_count != expected_count:
        assert False, "line '{}' found {} times (expected {} times) in output:\n{}\n"\
            .format(text, repeat_count, expected_count, mma_output)


def assert_does_not_contain(user_io, text):
    mma_output = user_io.output_text()
    if text in mma_output:
        assert False, "text '{}' FOUND in MMA output:\n{}\n".format(text, mma_output)


def test_mma_structure(mock_file, parse_abc, user_io):
    mock_content(mock_file, parse_abc, """
X:3
T: title
K:D
|"D"d8|
""")
    assert not user_io.has_errors()
    assert_has_line(user_io, "// created by abc2mma2midi")
    assert_has_line(user_io, "MidiTName title")
    assert_has_line(user_io, "Time 4")
    assert_has_line(user_io, "TimeSig 4/4")
    assert_has_line(user_io, "KeySig D")
    assert_has_line(user_io, "Tempo 150")
    assert_contains(user_io, "midiInc")
    assert_has_line(user_io, "1   D")
    assert_does_not_contain(user_io, "Repeat")
    assert_contains(user_io, "Groove", 2)


def test_mma_structure_6_8(mock_file, parse_abc, user_io):
    mock_68_tune(mock_file, parse_abc, '|"D"d2d f2f|')
    assert not user_io.has_errors()
    assert_has_line(user_io, "Time 6 Tabs=1,4")
    assert_has_line(user_io, "TimeSig 6/8")
    assert_has_line(user_io, "1   D")


def test_option_repeat_whole_piece(mock_file, parse_abc, user_io, options):
    options.repeat_whole_piece = 2

    mock_tune(mock_file, parse_abc, '|"D"d4 g2f2|')
    assert not user_io.has_errors()
    assert_has_line(user_io, "Repeat", 1)
    assert_has_line(user_io, "RepeatEnd", 1)


def test_abc_repeat(mock_file, parse_abc, user_io, options):
    options.repeat_whole_piece = 0

    mock_tune(mock_file, parse_abc, '|:"D"d4 g2f2:|')
    assert not user_io.has_errors()
    assert_has_line(user_io, "Repeat", 1)
    assert_has_line(user_io, "RepeatEnd", 1)


def test_abc_repeat_with_missing_repeat_start(mock_file, parse_abc, user_io, options):
    options.repeat_whole_piece = 0

    mock_tune(mock_file, parse_abc, '|"D"d4 g2f2:|')
    assert not user_io.has_errors()
    assert_has_line(user_io, "Repeat", 1)
    assert_has_line(user_io, "RepeatEnd", 1)


def test_option_repeat_whole_piece_and_abc_repeat(mock_file, parse_abc, user_io, options):
    options.repeat_whole_piece = 2

    mock_tune(mock_file, parse_abc, '|"D"d4 g2f2:|')
    assert not user_io.has_errors()
    assert_has_line(user_io, "Repeat", 2)
    assert_has_line(user_io, "RepeatEnd", 2)


def test_invalid_short_bar(mock_file, parse_abc, user_io):
    mock_tune(mock_file, parse_abc, '|"D"d4 f2|')
    assert not user_io.has_errors()


def test_invalid_short_bar_length_68(mock_file, parse_abc, user_io):
    mock_68_tune(mock_file, parse_abc, '|"D"d2d ff|')
    assert not user_io.has_errors()


def test_invalid_long_bar(mock_file, parse_abc, user_io):
    mock_tune(mock_file, parse_abc, '|"C"c4 f4||"D"d4 f4f2|')
    assert user_io.has_errors()
    assert_contains(user_io, "Bar length of 960 is too long, it should be 768")


def test_invalid_long_bar_length_68(mock_file, parse_abc, user_io):
    mock_68_tune(mock_file, parse_abc, '|"C"d2d ffg ||"D"d2d ffg a|')
    assert user_io.has_errors()
    assert_contains(user_io, "Bar length of 672 is too long, it should be 576")


def test_mid_68_bar_chord_change(mock_file, parse_abc, user_io):
    mock_68_tune(mock_file, parse_abc, '|d2d "D"f2f|')
    assert not user_io.has_errors()
    assert_has_line(user_io, "1   / D")


def test_off_beat_68_chord_change(mock_file, parse_abc, user_io):
    mock_68_tune(mock_file, parse_abc, '|d2"Am"d f2f|')
    assert user_io.has_errors()
    assert_contains(user_io, "The chord 'Am' is off the beat (192 ticks")


def test_lead_in_bar(mock_file, parse_abc, user_io):
    mock_tune(mock_file, parse_abc, 'A2|"Dm"B8|')
    assert_has_line(user_io, 'BEATADJUST -1.0')
    assert_has_line(user_io, 'BEATADJUST 1.0')
    assert_contains(user_io, 'This tune has a lead in bar of 192 ticks')
    assert_has_line(user_io, "1   Dm")


def test_lead_in_bar_6_8(mock_file, parse_abc, user_io):
    mock_68_tune(mock_file, parse_abc, 'abc|"Dm"c3 d3|')
    assert_has_line(user_io, 'BEATADJUST -3.0')
    assert_has_line(user_io, 'BEATADJUST 3.0')
    assert_contains(user_io, '288 ticks')
    assert_has_line(user_io, "1   Dm")


def test_lead_in_bar_with_a_repeat_start_bar6_8(mock_file, parse_abc, user_io):
    mock_68_tune(mock_file, parse_abc, '|:a|"Dm"c3 d3|')
    assert_has_line(user_io, 'BEATADJUST -1.0')
    assert_has_line(user_io, 'BEATADJUST 1.0')
    assert_contains(user_io, '96 ticks')
    assert_has_line(user_io, "1   Dm")


def test_four_chords_in_one_bar(mock_file, parse_abc, user_io):
    mock_tune(mock_file, parse_abc, '|"A"a2"B"b2"C"c2"D"d2|')
    assert_has_line(user_io, "1   A B C D")


def test_four_chords_in_one_bar_with_leadin(mock_file, parse_abc, user_io):
    mock_tune(mock_file, parse_abc, 'ef|"A"a2"B"b2"C"c2"D"d2|')
    assert_has_line(user_io, "1   A B C D")


def test_chords_on_beats_2_and_4(mock_file, parse_abc, user_io):
    mock_tune(mock_file, parse_abc, 'a|a2"B"b2c2"D"d2|')
    assert_has_line(user_io, "1   / B / D")


def test_chords_on_beats_1_and_3(mock_file, parse_abc, user_io):
    mock_tune(mock_file, parse_abc, 'a|"A"a2b2"C"c2d2|')
    assert_has_line(user_io, "1   A / C")


def test_missing_first_bar_line_with_chords(mock_file, parse_abc, user_io):
    mock_tune(mock_file, parse_abc, '"A"a2b2"C"c2d2|')
    assert_has_line(user_io, "1   A / C")


def test_extra_barlines_in_one_bar_are_ignored(mock_file, parse_abc, user_io):
    mock_tune(mock_file, parse_abc, '||"A"a2"B"b2"C"c2|"D"d2|')
    assert_has_line(user_io, "1   A B C D")


def test_two_repeats_in_6_8(mock_file, parse_abc, user_io):
    mock_68_tune(mock_file, parse_abc, '|: "B"b6 | "C"c6 :|\n|: "E"e6|"F"f6:|')
    assert not user_io.has_errors()
    assert_has_line(user_io, "1   B")
    assert_has_line(user_io, "2   C")
    assert_has_line(user_io, "3   E")
    assert_has_line(user_io, "4   F")
    assert_has_line(user_io, "Repeat", 2)
    assert_has_line(user_io, "RepeatEnd", 2)
    assert_contains(user_io, "Groove", 5)


def test_repeats_with_lead_in_6_8(mock_file, parse_abc, user_io):
    mock_68_tune(mock_file, parse_abc, 'a |: "B"b6 | "C"c6 :|\n|: "E"e6|"F"f6:|')
    assert not user_io.has_errors()
    assert_has_line(user_io, "1   B")
    assert_has_line(user_io, "2   C")
    assert_has_line(user_io, "3   E")
    assert_has_line(user_io, "4   F")
    assert_has_line(user_io, "Repeat", 2)
    assert_has_line(user_io, "RepeatEnd", 2)
    assert_contains(user_io, "Groove",  5)


def test_offset_repeats_with_lead_in_6_8(mock_file, parse_abc, user_io):
    mock_68_tune(mock_file, parse_abc, 'a | "B"b6 | "C"c5 :|\n|: d |"E"e6|"F"f5:|')
    assert not user_io.has_errors()
    assert_has_line(user_io, "1   B")
    assert_has_line(user_io, "2   C")
    assert_has_line(user_io, "3   E")
    assert_has_line(user_io, "4   F")


