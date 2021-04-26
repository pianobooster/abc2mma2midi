import os

import pytest

from abc2mma import Abc2Mma
from options import Options
from tests.test_options import helper_set_options


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


# todo remove this option or do it a better way
def make_output_dirs():
    make_dir('output/midi/')
    make_dir('output/mma/')


def test_tbd(options, abc2mma):
    make_output_dirs()
    #command_line(abc2mma,['files/abc_test_tunes.abc', 'XBang Upp', '-r'])
    # command_line(abc2mma,['files/abc_test_tunes.abc', 'Banish Misfortune', '-r'])
    #command_line(abc2mma,['files/abc_test_tunes.abc', 'Oyster Girl, The', '-r'])
    command_line(abc2mma,['files/abc_test_tunes.abc', 'Twinkle, Twinkle Little Star', '-r'])

def test_Twinkle_GuitarBallad(options, abc2mma):
    make_output_dirs()
    command_line(abc2mma, ['files/abc_test_tunes.abc', 'Twinkle, Twinkle Little Star', '-r',
                               '-o', 'output/midi/Twinkle-GuitarBallad',
                               '--grooves=GuitarBallad,GuitarBalladSus,GuitarBallad1,GuitarBallad1Sus'])

    abc2mma.run_abc_mma()

def test_Twinkle_FolkBallad(options, abc2mma):
    make_output_dirs()
    command_line(abc2mma, ['files/abc_test_tunes.abc', 'Twinkle, Twinkle Little Star', '-r',
                               '-o', 'output/midi/Twinkle-FolkBallad',
                               '--grooves=FolkBallad,FolkBalladPlus,FolkBallad1,FolkBallad1Sus,FolkBallad1Plus,FolkBallad1SusPlus'])

    abc2mma.run_abc_mma()

def test_command_line(options, abc2mma):
    make_output_dirs()
    command_line(abc2mma,['files/abc_test_tunes.abc', 'Bang Up', '-r',  '--patch-mma' ])

# python3 ../abc2mma 'files/pgh_session_tunebook.abc' 'Blaydon Races'
# python3 ../abc2mma 'files/pgh_session_tunebook.abc' 'Blarney Pilgrim'

def test_unicode_encoding():
    ## todo remove encoding='latin-1'
    # X:2053
    # T:Bourrées Carrées de La Châtre
    pass


def test_easy_abc2midi_emulation(options, abc2mma):
    ## - -o /home/louis/.EasyABC/cache/temp5f227043-343a-45b2-a097-e1fb4499319f.midi -BF -TT 440 -EA
    helper_set_options(options, ['-', '-o', '/home/louis/.EasyABC/cache/temp5f227043-343a-45b2-a097-e1fb4499319f.midi',
                                 '-BF', '-TT', '440', '-EA'])
    #abc2mma.run_abc_mma()

def test_easy_abc2midi_emulation2(options, abc2mma):
    ## - -o /home/louis/.EasyABC/cache/temp5f227043-343a-45b2-a097-e1fb4499319f.midi -BF -TT 440 -EA
    helper_set_options(options, ['files/easy_abc_test_tune.abc', '-o', 'output/easy_abc_test_tune.midi',
                                 '-BF', '-TT', '440', '-EA'])
    abc2mma.run_abc_mma()