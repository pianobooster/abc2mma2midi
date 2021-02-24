import options
from music import Barline, PPQN

from collections import namedtuple

Grooves68Standard = {'GROOVE_A_1': '68Swing1', 'GROOVE_A_2': '68Swing2Sus',
                     'GROOVE_B_1': '68Swing1Plus', 'GROOVE_B_2': '68Swing2SusPlus'}

GroovesStandard = {'GROOVE_A_1': 'GuitarBallad', 'GROOVE_A_2': 'GuitarBalladSus',
                     'GROOVE_B_1': 'GuitarBallad1', 'GROOVE_B_2': 'GuitarBallad1Sus'}

FIRST_HEADER = """
Begin Solo-Left
    Voice Clarinet // Flute Clarinet
    Channel 4
End

Volume f    
"""

VoiceStandard = '''
// Walk Voice AcousticBass
// Chord Voice Piano1
// Chord-Sus Voice Strings
// Arpeggio Voice JazzGuitar
'''
Voice68Standard = '''
// Walk Voice AcousticBass
// Chord Voice Piano1
Chord-Sus Voice Strings
// Arpeggio Voice JazzGuitar
'''
BarChords = namedtuple('BarChords', 'bar_no chords error_messages')


class GenerateMma:

    def __init__(self, user_io, options):
        self.io = user_io
        self.options = options
        self.time_sig_top = 4
        self.time_sig_bottom = 4
        self.bar_no = 1
        self.bar_ticks = 0  # in PPQN
        self.saved_bars = []
        self.current_chords = []
        self.find_lead_in_bar = True
        self.lead_in_bar_length = 0
        self.bar_length = 4 * PPQN
        self.early_barlines = []
        self.inside_repeat_marks = False
        self._pre_music_required = True

        self.part_counter = 0  # Zero for the A part, 1 for the B part etc
        self.delayed_errors = []
        self.tune_file_name = ''
        self._reset()

    def _reset(self):
        self.time_sig_top = 4
        self.time_sig_bottom = 4
        self.bar_no = 1
        self.bar_ticks = 0  # in PPQN
        self.saved_bars = []
        self.current_chords = []
        self.find_lead_in_bar = True
        self.lead_in_bar_length = 0
        self.bar_length = 4 * PPQN
        self.early_barlines = []
        self.inside_repeat_marks = False
        self._pre_music_required = True
        self.inside_repeat_marks = False
        self._pre_music_required = True

    def tune_start(self, tune_id):
        self.io.out_print("// created by abc2mma")

    def tune_end(self):
        # if the last bar last barline was not a full bar then we need to call this
        self.barline(Barline.TheEnd)

        if self.options.repeat_whole_piece > 1:
            self.io.out_print("RepeatEnd")
        self.io.out_print()
        self._reset()

    def tune_title(self, tune_name):
        self.io.out_print("MidiTName " + tune_name)
        self.tune_file_name = tune_name.replace(' ', '').replace('\t', '')

    def tune_time_sig(self, top, bottom):
        self.time_sig_top = top
        self.time_sig_bottom = bottom
        self.bar_length = top * 4 * PPQN // bottom

    def tune_key_sig(self, key_sig):
        time_str = str(self.time_sig_top)
        if self.time_sig_top == 6:
            time_str += " Tabs=1,4"
        self.io.out_print("Time " + time_str)
        self.io.out_print("TimeSig " + str(self.time_sig_top) + '/' + str(self.time_sig_bottom))
        if key_sig.endswith('m'):
            key_sig = key_sig.replace('m', ' Min')
        self.io.out_print("KeySig " + key_sig)
        if self.time_sig_bottom == 8:
            self.io.out_print("Tempo " + '300')
        else:
            self.io.out_print("Tempo " + '150')

    def output_custom_macro(self):
        self.io.out_print("MSet CustomSettings")
        self.io.out_print("// Uncomment the lines below to change the voices used in all grooves")
        if self.is_compound_time_sig():
            self.io.out_print(Voice68Standard)
        else:
            self.io.out_print(VoiceStandard)
        self.io.out_print("MSetEnd\n")

    def output_count_in(self):
        self.output_groove(0)
        # self.io.out_print('Groove Metronome6') // ZZ
        self.io.out_print("z!\nz\nz\n")
        pass

    def output_pre_music(self):
        if self._pre_music_required:
            self._pre_music_required = False
            self.io.out_print(FIRST_HEADER)
            self.output_custom_macro()

            self.output_count_in()

            if self.options.repeat_whole_piece > 1:
                self.io.out_print("Repeat")

            midi_include = "midiInc file={}-solo.mid Solo-Left=1 Volume=90 ".format(self.tune_file_name)

            if self.time_sig_bottom == 8:
                midi_include += " STRETCH=200"

            if self.lead_in_bar_length:
                self.io.out_print("// This tune has a lead in bar of {} ticks".format(self.lead_in_bar_length))
                beat_adjust = self.lead_in_bar_length / PPQN
                if self.is_compound_time_sig():
                    beat_adjust *= 2
                # midi_include += " START={}".format(self.lead_in_bar_length * self.time_sig_bottom // (PPQN * 2))
                self.io.out_print("BEATADJUST {}".format(-beat_adjust))
            self.io.out_print(midi_include)
            if self.lead_in_bar_length:
                self.io.out_print("BEATADJUST {}".format(beat_adjust))

            self.io.out_print()
            self.output_groove(0)

    def output_repeat_bars(self, barline):
        if barline == Barline.RepeatStart:
            self.output_saved_bars(False)
            if self.part_counter > 0:
                self.io.out_print()
                self.output_groove(0)
            self.io.out_print("Repeat")
            self.inside_repeat_marks = True
        elif barline == Barline.RepeatEnd:
            self.output_saved_bars(True)
            self.output_groove(1)
            self.io.out_print("RepeatEnd")
            self.inside_repeat_marks = False
            self.part_counter += 1
        elif barline == Barline.RepeatEnding:
            self.output_saved_bars(True)
            self.io.out_print("ZZ RepeatEnding")
            self.inside_repeat_marks = False
        elif barline == Barline.TheEnd:
            self.output_saved_bars(False)

    # compound time signature (6/8, 9/8, 12/8)
    def is_compound_time_sig(self):
        return self.time_sig_top % 3 == 0 and self.time_sig_bottom == 8

    def output_groove(self, repeat_counter):
        groove = GroovesStandard

        if self.is_compound_time_sig():
            groove = Grooves68Standard
        if self.part_counter == 0:
            if repeat_counter == 0:
                groove_name =  groove['GROOVE_A_1']
            else:
                groove_name =  groove['GROOVE_A_2']
        else:
            if repeat_counter == 0:
                groove_name =  groove['GROOVE_B_1']
            else:
                groove_name =  groove['GROOVE_B_2']

        self.io.out_print("Groove " + groove_name)
        self.io.out_print("$CustomSettings")

    def barline(self, barline):

        # Detect a lead in bar (the first bar with a reduced bar length).
        if self.find_lead_in_bar and self.bar_ticks < self.bar_length:
            if self.bar_ticks:
                self.find_lead_in_bar = False
                self.lead_in_bar_length = self.bar_ticks
                self.bar_ticks = 0
            return

        self.output_pre_music()
        self.find_lead_in_bar = False

        # ignore early bar lines, but save them in case they are repeat bars
        if barline != Barline.TheEnd and 0 < self.bar_ticks < self.bar_length:
            self.early_barlines.append(barline)
            return

        if self.bar_ticks > self.bar_length:
            self.delayed_errors.append("Bar length of {} is too long, it should be {}"
                                       .format(self.bar_ticks, self.bar_length))

        # Don't output anything if there have been no ticks between this and the previous bar
        if self.bar_ticks > 0:
            self.saved_bars.append(BarChords(self.bar_no, self.current_chords, self.delayed_errors))
            self.bar_no += 1
            self.delayed_errors = []
            self.bar_ticks -= self.bar_ticks
            self.current_chords = []

        # Always process the barline
        for e_barline in self.early_barlines:
            self.output_repeat_bars(e_barline)
        self.early_barlines.clear()
        self.output_repeat_bars(barline)

    def chord_symbol(self, chord_name):
        beat_length = self.bar_length // self.time_sig_top
        if self.time_sig_bottom == 8 and self.time_sig_top in (6, 9, 12):
            beat_length *= 3

        if self.bar_ticks % beat_length == 0:
            beat_pos = self.bar_ticks // beat_length

            idx = len(self.current_chords)
            while idx < beat_pos:
                self.current_chords.append('/')
                idx += 1

            self.current_chords.append(chord_name)

        else:
            self.delayed_errors.append(
                "The chord '{}' is off the beat ({} ticks from the bar line)".format(chord_name, self.bar_ticks))

    def note(self, note, duration):
        self.bar_ticks += duration

    def output_saved_bars(self, repeat_start):

        if self.saved_bars:
            if repeat_start and not self.inside_repeat_marks:
                self.io.out_print("Repeat")

            for bar in self.saved_bars:
                for message in bar.error_messages:
                    self.io.error(message)

                if not bar.chords:
                    bar.chords.append("/")
                self.io.out_print("{:<2}  {}".format(bar.bar_no, ' '.join(bar.chords)))

        self.saved_bars.clear()
