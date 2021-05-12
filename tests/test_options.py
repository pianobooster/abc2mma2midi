import os
import pathlib

import pytest

from options import Options


@pytest.fixture
def options():
    return Options()


def make_dir(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def helper_set_options(options, commands):
    options.pass_arguments(commands)


def test_default_options(options):
    helper_set_options(options,['', ''])
    assert options.abc_file_name == ''
    assert options.tune_search_name == ''
    assert options.repeat_whole_piece == 1
    assert options.alternative_groove is None
    assert options.abc_tune_id is None
    assert options.patch_mma is False
    assert options.mma_stretch is None
    assert options.mma_path is None
    assert options._output_filename is None
    assert options.mma_debug is False


def test_command_line_options(options):
    helper_set_options(options,['--patch-mma', '--mma-stretch=200' , '--mma-path=/my/path/mma.py',
                          '--output', 'my-tune.mma', '--alternative', '--repeat','files/abc_test_tunes.abc', 'Bang Upp'])
    assert options.abc_file_name == 'files/abc_test_tunes.abc'
    assert options.tune_search_name == 'Bang Upp'
    assert options.repeat_whole_piece == 2
    assert options.alternative_groove == 'altGroove'
    assert options.abc_tune_id is None
    assert options.patch_mma is True
    assert not options.grooves_string
    assert not options.get_grooves()
    assert isinstance(options.mma_stretch, float)
    assert options.mma_stretch == 200
    assert isinstance(options.mma_path, pathlib.Path)

    if os.name == 'nt':  # Windows
        assert str(options.mma_path) == '\\my\\path\\mma.py'
    else:
        assert str(options.mma_path) == '/my/path/mma.py'

    assert options.midi_filename() == 'my-tune.mid'
    assert options.midi_solo_filename() == 'my-tune-solo.mid'
    assert options.mma_filename() == 'my-tune.mma'


def test_groove_list(options):
    helper_set_options(options,[ '', '', '--grooves', 'G1, G2,,G4'])
    assert options.grooves_string == 'G1, G2,,G4'
    assert options.get_grooves() == ['G1', 'G2','','G4']


def test_single_groove(options):
    helper_set_options(options,[ '', '', '--grooves', 'OneGroove'])
    assert options.grooves_string == 'OneGroove'
    assert options.get_grooves() == ['OneGroove']


def test_easy_abc2midi_emulation(options):
    helper_set_options(options, ['-', '-o', '/a/b/c/file-name',
                                 '-BF', '-TT', '440', '-EA'])
    assert options.abc_file_name == '-'
    assert options.tune_search_name is None


def test_output_file_name(options):
    helper_set_options(options, ['-', '-o', '/a/b/c/file-name'])
    if os.name == 'nt':  # Windows
        path_name = '\\a\\b\\c\\'
    else:
        path_name = '/a/b/c/'

    assert options.midi_filename() == f'{path_name}file-name.mid'
    assert options.midi_solo_filename() == f'{path_name}file-name-solo.mid'
    assert options.mma_filename() == f'{path_name}file-name.mma'

    helper_set_options(options, ['-', '-o', '/a/b/c/file-name.midi'])
    assert options.midi_filename() == f'{path_name}file-name.midi'
    assert options.midi_solo_filename() == f'{path_name}file-name-solo.mid'
    assert options.mma_filename() == f'{path_name}file-name.mma'
