from unittest.mock import MagicMock, call

import pytest

from auto_chord import AutoChord
from options import Options
from user_io import UserIo


@pytest.fixture
def options():
    return Options()


@pytest.fixture
def user_io():
    return UserIo()


@pytest.fixture
def emitter():
    return MagicMock()


@pytest.fixture
def auto_chord(user_io, options, emitter):
    return AutoChord(user_io, options, emitter)


def test_middle_c(auto_chord, emitter):
    auto_chord.midi_note(60, 192)
    emitter.chord_symbol.assert_called_once_with('C')


def test_c_maj_chord(auto_chord, emitter):
    auto_chord.midi_note(60, 192) # C
    auto_chord.midi_note(64, 192) # E
    auto_chord.midi_note(67, 192) # G

    emitter.chord_symbol.assert_has_calls([call('C'), call('C'), call('G')])

    ## more test to be written

    # C Major scale
    # C -> 1 (Cmaj)
    # D -> 5 (Gmaj)
    # E -> 1 (Cmaj)
    # F -> 4 (Fmaj)
    # G -> 5 (Gmaj)
    # A -> 4 (Fmaj)
    # B -> 5 (Gmaj)

    # D major scale
    # D -> 1 (Dmaj)
    # E -> 5 (Amaj)
    # F# -> 1 (Dmaj)
    # G -> 4 (Gmaj)
    # A -> 5 (Amaj)
    # B -> 4 (Gmaj)
    # C# -> 5 (Amaj)
