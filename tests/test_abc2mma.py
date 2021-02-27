import os

import pytest

from abc2mma import Abc2Mma
from options import Options


@pytest.fixture
def options():
    return Options()


@pytest.fixture
def abc2mma(options):
    return Abc2Mma(options)


def make_dir(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def command_line(abc2mma, commands):
    abc2mma.pass_args(commands)


def test_tbd(options, abc2mma):
    options.abc_file_name = 'files/abc_test_tunes.abc'
    options.repeat_whole_piece = 2
    options.abc_tune_title = 'Bang Upp'
    #options.abc_tune_title = 'Banish Misfortune'

    abc2mma.open_file()


def test_command_line(options, abc2mma):
    options.repeat_whole_piece = 2
    command_line(abc2mma,['files/abc_test_tunes.abc', 'Bang Upp'])

# python3 ../abc2mma 'files/pgh_session_tunebook.abc' 'Blaydon Races'
# python3 ../abc2mma 'files/pgh_session_tunebook.abc' 'Blarney Pilgrim'



def test_unicode_encoding():
    ## todo remove encoding='latin-1'
    # X:2053
    # T:Bourrées Carrées de La Châtre
    pass
