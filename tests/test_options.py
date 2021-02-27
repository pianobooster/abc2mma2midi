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


def command_line(options, commands):
    options.pass_arguments(commands)


def test_default_options(options):
    command_line(options,['', ''])
    assert options.abc_file_name == ''
    assert options.abc_tune_title == ''
    assert options.repeat_whole_piece == 1
    assert options.alternative_groove is None
    assert options.abc_tune_id is None
    assert options.patch_mma is False
    assert options.mma_stretch is None
    assert options.mma_path is None
    assert options.mma_output_filename is None
    assert options.mma_debug is False


def test_command_line_options(options):
    command_line(options,['--patch-mma', '--mma-stretch=200' , '--mma-path=/my/path/mma.py',
                          '--output', 'my-tune.mma', '--alternative', '--repeat','files/abc_test_tunes.abc', 'Bang Upp'])
    assert options.abc_file_name == 'files/abc_test_tunes.abc'
    assert options.abc_tune_title == 'Bang Upp'
    assert options.repeat_whole_piece == 2
    assert options.alternative_groove == 'altGroove'
    assert options.abc_tune_id is None
    assert options.patch_mma is True
    assert not options.grooves_string
    assert not options.get_grooves()
    assert isinstance(options.mma_stretch, float)
    assert options.mma_stretch == 200
    assert isinstance(options.mma_path, pathlib.Path)
    assert str(options.mma_path) == '/my/path/mma.py'
    assert isinstance(options.mma_output_filename, pathlib.Path)
    assert str(options.mma_output_filename) == 'my-tune.mma'


def test_groove_list(options):
    command_line(options,[ '', '', '--grooves', 'G1, G2,,G4'])
    assert options.grooves_string == 'G1, G2,,G4'
    assert options.get_grooves() == ['G1', 'G2','','G4']


def test_single_groove(options):
    command_line(options,[ '', '', '--grooves', 'OneGroove'])
    assert options.grooves_string == 'OneGroove'
    assert options.get_grooves() == ['OneGroove']
