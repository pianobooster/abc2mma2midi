import options
from music import Barline, PPQN

from collections import namedtuple

Grooves68Standard = ['68Swing1', '68Swing2Sus','68Swing1Plus', '68Swing2SusPlus']
#Grooves68Standard = ['68BanjoStrum', '68BanjoStrum','68GuitarStrum', '68BanjoStrum']

USE_GROOVE_PREFIX = "Groove "
GroovesStandard = ['GuitarBallad', 'GuitarBalladSus', 'GuitarBallad1', 'GuitarBallad1Sus']
#GroovesStandard = ['CountrySwing', 'CountrySwingSus', 'CountrySwing1', 'CountrySwing1Sus', 'CountrySwing2', 'CountrySwing2Sus']
#GroovesStandard = ['Folk', 'FolkWalk', 'FolkArticulated', 'FolkSus', 'FolkArticulatedSus', 'FolkArticulatedSus']
#GroovesStandard = ['First', 'SecondTry', 'First', 'SecondSustain' ]
#GroovesStandard = ['SecondTry', 'SecondTry', 'SecondTry', 'SecondSustain' ]
#GroovesStandard = ['FolkRock', 'FolkRockSus', 'FolkRockPlus', 'FolkRockSusPlus', 'FolkArticulatedSus', 'FolkArticulatedSus']
#GroovesStandard = ['FolkRock', 'FolkRockSus', 'FolkRockPlus', 'FolkRockSusPlus', 'FolkArticulatedSus', 'FolkArticulatedSus']
#GroovesStandard = ['FolkBallad', 'FolkBalladPlus', 'FolkBallad1', 'FolkBallad1Sus', 'FolkBallad1Plus', 'FolkBallad1SusPlus']
# GroovesStandard = ['Polka', 'PolkaSus', 'PolkaArp', 'PolkaSusArp', 'Polka1', 'Polka1Sus']
#USE_GROOVE_PREFIX = ""
#GroovesStandard = ['Plectrum-Strum @StrumPattern duxuduxu', 'Plectrum-Strum @StrumPattern d-du-udu', 'Plectrum-Strum @StrumPattern dm.um.d.u.de.ue.d.u', 'Plectrum-Strum @StrumPattern 64.53.42.31.42.31.42.35' ]
#GroovesStandard = ['Plectrum-Strum @StrumPattern d---d--u;-ud-dudu', 'Plectrum-Strum @StrumPattern dm.um.d.u.de.ue.d.u', 'Plectrum-Strum @StrumPattern dm.um.dm.um.dm.um.dm.um', 'Plectrum-Strum @StrumPattern 12345654' ]


USE_TEMPO = 140 # 140 #ZZ 150 160
USE_SOLO_VOLUME = 80  # 80 60
USE_SOLO_VOICE = 'Flute' # Flute Clarinet Piano1
USE_METRONOME = False
USE_MASTER_VOLUME = 'mf'

Grooves34Standard = ['GuitarStrum2', 'CountryWaltz1Sus', 'GuitarStrum2', 'CountryWaltz1Sus']

FIRST_HEADER = f"""
Begin Solo-Left
    Voice {USE_SOLO_VOICE} // Flute Clarinet Piano1
    Channel 4
End

Volume {USE_MASTER_VOLUME} 

Include BoosterLib

Drum-Metronome Tone Sticks
Drum-Metronome Sequence {{1 0 30 * 4}}
"""


VoiceStandard = '''
// Walk Voice AcousticBass
// Chord Voice Piano1
Chord-Sus Voice Strings 
Chord-Sus Volume pp 
// Arpeggio Voice JazzGuitar
'''
Voice68Standard = '''
// Walk Voice AcousticBass
// Chord Voice Piano1
Chord-Sus Voice Strings //Strings
Chord-Sus Volume ppp 
// Arpeggio Voice JazzGuitar
'''
BarChords = namedtuple('BarChords', 'bar_no chords error_messages')


class GenerateMma:

    def __init__(self, user_io, options):
        self.io = user_io
        self.options = options
        self.part_counter = 0  # Zero for the A part, 1 for the B part etc
        self.delayed_errors = []

        # todo These are only required to prevent ide warnings
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

    def tune_time_sig(self, top, bottom):
        self.time_sig_top = top
        self.time_sig_bottom = bottom
        self.bar_length = top * 4 * PPQN // bottom

    def tune_key_sig(self, key_sig):
        time_str = str(self.time_sig_top)
        if self.time_sig_top == 6:
            time_str += " Tabs=1,4" # ZZ TBD decided what we should do here.
        self.io.out_print("Time " + time_str)
        self.io.out_print("TimeSig " + str(self.time_sig_top) + '/' + str(self.time_sig_bottom))
        if key_sig.endswith('m'):
            key_sig = key_sig.replace('m', ' Min')
        self.io.out_print("KeySig " + key_sig)
        stretch = self.options.mma_stretch
        tempo = USE_TEMPO
        if not stretch and self.time_sig_bottom == 8:
            stretch = 200
        if stretch:
            tempo = (tempo * stretch) // 100

        self.io.out_print(f"Tempo {tempo}")

    def output_custom_macro(self):
        self.io.out_print("MSet CustomSettings")
        self.io.out_print("// Uncomment the lines below to change the voices used in all grooves")
        if self.is_compound_time_sig():
            self.io.out_print(Voice68Standard)
        else:
            self.io.out_print(VoiceStandard)
        self.io.out_print("MSetEnd\n")

    def output_count_in(self):
        if USE_METRONOME:
            if self.is_compound_time_sig():
                metronome = 'Metronome68' # ZZ needs a rewrite
            elif self.is_time_sig(3, 4):
                metronome = 'Metronome3'
            else:
                metronome = "Metronome4"
            self.io.out_print(f'Groove {metronome}')
        else:
            self.output_groove(0)

        self.io.out_print("Volume pp")

        if self.options.mma_debug:
            self.io.out_print("z\n")
        else:
            self.io.out_print("z!\nz\nz\n")
        self.io.out_print(f"Volume {USE_MASTER_VOLUME}")

    def output_pre_music(self):
        if self._pre_music_required:
            self._pre_music_required = False
            self.io.out_print(FIRST_HEADER)
            self.output_custom_macro()

            self.output_count_in()

            if self.options.repeat_whole_piece > 1:
                self.io.out_print("Repeat")

            if USE_SOLO_VOLUME > 0:
                midi_include = f"midiInc file={self.options.midi_solo_filename()} Solo-Left=1 Volume={USE_SOLO_VOLUME}"

                stretch = self.options.mma_stretch
                if not stretch and self.time_sig_bottom == 8:
                    stretch = 200
                if stretch and stretch != 100:
                    midi_include += " STRETCH="+ str(stretch)
                if self.lead_in_bar_length:
                    self.io.out_print(f"// This tune has a lead in bar of {self.lead_in_bar_length} ticks")
                    beat_adjust = self.lead_in_bar_length / PPQN
                    if stretch:
                        beat_adjust *= stretch / 100
                    self.io.out_print(f"BEATADJUST {-beat_adjust}")
                self.io.out_print(midi_include)
                if self.lead_in_bar_length:
                    self.io.out_print(f"BEATADJUST {beat_adjust}")

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

    def is_time_sig(self, top, bottom):
        return self.time_sig_top == top and self.time_sig_bottom == bottom

    def output_groove(self, repeat_counter):
        groove_list = self.options.get_grooves()

        if not groove_list:

            if self.is_compound_time_sig():
                groove_list = Grooves68Standard
            elif self.is_time_sig(3,4):
                groove_list = Grooves34Standard
            else:
                groove_list = GroovesStandard

        groove_idx = self.part_counter * 2 + repeat_counter
        for idx, val in enumerate(groove_list):
            if idx <= groove_idx:
                groove_name = val

        # todo make the grove optional
        self.io.out_print(USE_GROOVE_PREFIX + groove_name)
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
            self.delayed_errors.append(f"Bar length of {self.bar_ticks} is too long, it should be {self.bar_length}")

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
                f"The chord '{chord_name}' is off the beat ({self.bar_ticks} ticks from the bar line)")

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
