import pytest

from abc_buffer import AbcBuffer, AbcFormatError
from music import Barline


def test_pitch_and_rests():
    buff = AbcBuffer("A^B^^C=D_EF,G,,ab'c''zZx")
    assert buff.is_pitch_rest()
    assert buff.pop_pitch_rest() == 'A'
    assert buff.is_pitch_rest()
    assert buff.pop_pitch_rest() == '^B'
    assert buff.pop_pitch_rest() == '^^C'
    assert buff.is_pitch_rest()
    assert buff.pop_pitch_rest() == '=D'
    assert buff.is_pitch_rest()
    assert buff.pop_pitch_rest() == '_E'
    assert buff.pop_pitch_rest() == 'F,'
    assert buff.pop_pitch_rest() == 'G,,'
    assert buff.is_pitch_rest()
    assert buff.pop_pitch_rest() == 'a'
    assert buff.pop_pitch_rest() == "b'"
    assert buff.pop_pitch_rest() == "c''"


def test_not_pitch():
    assert not AbcBuffer("H").is_pitch_rest()
    assert not AbcBuffer("h").is_pitch_rest()


def test_pitch_errors():
    buff = AbcBuffer("^^^B===CD'e,^zZ,")
    assert buff.is_pitch_rest()
    with pytest.raises(AbcFormatError):
        AbcBuffer("^^^B").pop_pitch_rest()
    with pytest.raises(AbcFormatError):
        AbcBuffer("===C").pop_pitch_rest()
    #buff = AbcBuffer(D'e,^zZ,")


def test_order_of_abc_constructs():
    buff = AbcBuffer('"Am7" D2"')
    assert buff.pop_chord_symbol() == 'Am7'
    assert not buff.is_chord_symbol()
    with pytest.raises(AbcFormatError):
        buff.pop_pitch_rest()


def test_source_as_list():
    buff = AbcBuffer(["A"])
    assert buff.is_pitch_rest()
    assert buff.pop_pitch_rest() == 'A'


def assert_duration(test_abc_note, expected_top, expected_bottom):
    buff = AbcBuffer(test_abc_note)
    buff.pop_pitch_rest()
    actual_top, actual_bottom = buff.pop_duration()
    assert actual_top == expected_top
    assert actual_bottom == expected_bottom


def test_note_durations():
    #AbcBuffer("AB1C2D/E1/F/3G1/3")

    assert_duration("a", 1, 1)
    assert_duration("a1", 1, 1)
    assert_duration("a2", 2, 1)
    assert_duration("a/", 1, 2)
    assert_duration("a1/", 1, 2)
    assert_duration("a1/2", 1, 2)
    assert_duration("a/3", 1, 3)
    assert_duration("a1/3", 1, 3)
    assert_duration("^a'1/3", 1, 3)
    #assert_duration("a2/", 1, 1) # this edge case does not work


def assert_bar_line(test_abc_data, expected_barline):
    buff = AbcBuffer(test_abc_data)
    assert buff.is_barline()
    actual_barline = buff.pop_barline()
    assert actual_barline == expected_barline


def test_bar_lines():
    assert_bar_line("|", Barline.Standard)   # bar line
    assert_bar_line("|a", Barline.Standard)   # bar line
    assert_bar_line("|]", Barline.Standard)  # thin-thick double bar line
    assert_bar_line("||", Barline.Standard)  # thin-thin double bar line
    assert_bar_line("[|", Barline.Standard)  # thick-thin double bar line
    assert_bar_line("|:", Barline.RepeatStart)  # start of repeated section
    assert_bar_line(":|", Barline.RepeatEnd)  # end of repeated section
    buff = AbcBuffer("::")
    assert buff.is_barline()
    barline = buff.pop_barline()
    assert barline == Barline.RepeatEnd
    assert buff.is_barline()
    barline = buff.pop_barline()
    assert barline == Barline.RepeatStart

    assert not AbcBuffer(":a").is_barline()
    assert not AbcBuffer("[b").is_barline()


def test_ignore_abc_data():
    assert AbcBuffer(" ").is_ignore_abc()
    assert AbcBuffer("\t").is_ignore_abc()
    assert AbcBuffer("\n").is_ignore_abc()
    buff = AbcBuffer(" \t\n A")
    assert buff.is_ignore_abc()
    buff.skip_ignore_abc()
    assert not buff.is_ignore_abc()
    assert buff.pop_pitch_rest() == 'A'


def test_chord_symbols():
    buff = AbcBuffer('"Am7"D2."')

    assert buff.pop_chord_symbol() == 'Am7'
    assert not buff.is_chord_symbol()
    assert buff.pop_pitch_rest() == 'D'
