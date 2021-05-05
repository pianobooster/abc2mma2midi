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

def input_notes(auto_chord, note_list):
    note_lookup = {'C':60, 'C#':61,'D':62,'D#':63,'E':64,'F':65,'F#':66,'G':67,'G#':68,'A':69,'A#':70,'Bb':70,'B':71}
    duration = 192
    for note in note_list.split():
        m_note= note_lookup[note]
        print(f' note {note} midi value {m_note}')
        auto_chord.midi_note(m_note, duration)


def validate_chords(emitter, chord_list):
    calls = []
    for chord in chord_list.split():
        calls.append(call(chord))

    emitter.chord_symbol.assert_has_calls(calls)


def test_middle_c(auto_chord, emitter):
    auto_chord.midi_note(60, 192)
    emitter.chord_symbol.assert_called_once_with('C')


def test_c_maj_chord(auto_chord, emitter):
    input_notes(auto_chord, "C E G")
    validate_chords(emitter, "C C G")


def test_c_maj_scale(auto_chord, emitter):
    auto_chord.key_sig("C")
    auto_chord.time_sig(4,4)
    input_notes(auto_chord, "C D E G F G A B")
    validate_chords(emitter, "C G C F G F G")


def test_d_maj_scale(auto_chord, emitter):
    auto_chord.key_sig("D")
    input_notes(auto_chord, "D E G F# G A B C#")
    validate_chords(emitter, "D A D G A G A")

# Key sig C I - IV - V chords	C - F - G
# Key sig F I - IV - V chords   F - Bb - C

def test_f_maj_scale(auto_chord, emitter):
    auto_chord.key_sig("C")
    auto_chord.time_sig(4,4)
    input_notes(auto_chord, "F A Bb C D E F G")
    validate_chords(emitter, "F C F Bb C Bb C")
