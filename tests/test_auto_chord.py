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
    auto_chord.note('C', 192)
    emitter.chord_symbol.assert_called_once_with('C')


def test_c_maj_chord(auto_chord, emitter):
    auto_chord.note('C', 192)
    auto_chord.note('E', 192)
    auto_chord.note('G', 192)

    emitter.chord_symbol.assert_has_calls([call('C'), call('C'), call('Gm')])
