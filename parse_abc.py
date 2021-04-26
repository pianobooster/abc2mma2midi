import music
from abc_buffer import AbcBuffer, AbcFormatError

KeyModeLookUp = {
    # Mixolydian (Major)
    'g#mix': 'C#', 'c#mix': 'F#', 'f#mix': 'B', 'bmix': 'E', 'emix': 'A',
    'amix': 'D', 'dmix': 'G', 'gmix': 'C', 'cmix': 'F', 'fmix': 'Bb',
    'bbmix': 'Eb', 'ebmix': 'Ab', 'abmix': 'Db', 'dbmix': 'Gb', 'gbmix': 'Cb',

    # Dorian (Minor)
    'd#dor': 'A#m', 'g#dor': 'D#m', 'c#dor': 'G#m', 'f#dor': 'C#m', 'bdor': 'F#m',
    'edor': 'Bm', 'ador': 'Em', 'ddor': 'Am', 'gdor': 'Dm', 'cdor': 'Gm',
    'fdor': 'Cm', 'bbdor': 'Fm', 'ebdor': 'Bbm', 'abdor': 'Ebm', 'dbdor': 'Abm',

    # Phrygian (minor)
    'e#phr': 'A#m', 'a#phr': 'D#m', 'd#phr': 'G#m', 'g#phr': 'C#m', 'c#phr': 'F#m',
    'f#phr': 'Bm', 'bphr': 'Em', 'ephr': 'Am', 'aphr': 'Dm', 'dphr': 'Gm',
    'gphr': 'Cm', 'cphr': 'Fm', 'fphr': 'Bbm', 'bbphr': 'Ebm', 'ebphr': 'Abm',

    # Lydian (Major)
    'f#lyd': 'C#', 'blyd': 'F#', 'elyd': 'B', 'alyd': 'E', 'dlyd': 'A',
    'glyd': 'D', 'clyd': 'G', 'flyd': 'C', 'bblyd': 'F', 'eblyd': 'Bb',
    'ablyd': 'Eb', 'dblyd': 'Ab', 'gblyd': 'Db', 'cblyd': 'Gb', 'fblyd': 'Cb',

    # Locrian
    'b#loc': 'C#', 'e#loc': 'F#', 'a#loc': 'B', 'd#loc': 'E', 'g#loc': 'A',
    'c#loc': 'D', 'f#loc': 'G', 'bloc': 'C', 'eloc': 'F', 'aloc': 'Bb',
    'dloc': 'Eb', 'gloc': 'Ab', 'cloc': 'Db', 'floc': 'Gb', 'bbloc': 'Cb'
}


class ParseAbc:

    def __init__(self, emitter, user_io, options):
        self.emit = emitter
        self.io = user_io
        self.options = options
        self.unit_length_top = 1
        self.unit_length_bottom = 8
        self.tune_search_name = ""
        self.abc_tune_id = None
        self.time_sig_bottom = 4
        self._tuple_scaling = 1.0
        self._tuple_counter = 0

        self._header = []
        self._body = []

    def reset(self):
        self.__init__(self.emit, self.io, self.options)

    def parse_input(self):
        if self.build_tune():
            self.process_tune()

    def process_tune(self):
       if self.process_header():
            self.process_body()

    def build_tune(self):
        while self.io.lines_available:
            line = self.io.read_line()
            if not line:
                break

            if line.startswith('X:'):
                header = []
                body = []
                header.append(line)
                while self.io.lines_available:
                    line = self.io.read_line()
                    if not line or line.isspace():
                        self.io.error("Unexpected end of Tune")
                        break
                    header.append(line)

                    if line.startswith('K:'):
                        while self.io.lines_available:
                            line = self.io.read_line()
                            if not line or line.isspace():
                                break
                            body.append(line)
                        if self.find_matching_tune(header):
                            if body:
                                self._header = header
                                self._body = body
                                return True
                            else:
                                self.io.error("The Abc Tune has a missing body")
                        break
        self.io.error(f"The Abc Tune '{self.options.tune_search_name}' is not found")
        return False

    def process_header(self):
        for line in self._header:
            if len(line) >= 2 and line[1] == ':':
                field = line[0]
                text = line[2:].strip()

                if field == 'X':
                    if text.isdigit():
                        tune_id = int(text)
                        self.emit.tune_start(tune_id)
                    else:
                        self.io.error(f"The X: field '{field}' is not an a valid tune id")
                        return False

                elif field == 'T':
                    if tune_id:
                        if self.is_matching_tune(text):
                            self.tune_search_name = text
                            self.abc_tune_id = tune_id
                            self.emit.tune_title(text)
                elif field == 'L':
                    if '/' in text:
                        top, bottom = text.split('/')
                        self.unit_length_top = int(top)
                        self.unit_length_bottom = int(bottom)
                elif field == 'M':
                    if '/' in text:
                        top, bottom = text.split('/')
                        self.emit.tune_time_sig(int(top), int(bottom))
                        self.time_sig_bottom = int(bottom)
                    else:
                        raise AbcFormatError("Bad time signature", -1)  # todo fix the line number

                elif field == 'K':
                    mode_key = text.lower()
                    if mode_key in KeyModeLookUp:
                        text = KeyModeLookUp[mode_key]
                    self.emit.tune_key_sig(text)
        return True

    # Order of constructs for abc note: <grace notes>, <chord symbols>, <annotations>/<decorations> , <accidentals>, <note>, <octave>, <note length>
    # i.e. ~^c'3 or even "Gm7"v.=G,2.
    def process_body(self):
        buff = AbcBuffer(self._body)
        while buff.has_more_data():

            buff.skip_ignore_abc()

            if buff.is_new_line():
                buff.skip_ignored_body_field_lines()
                buff.pop_char() # we don't need the new line char
                continue

            if buff.is_barline():
                self.emit.barline(buff.pop_barline())
                continue

            #  start of abc note construct
            if buff.is_chord_symbol():
                self.emit.chord_symbol(buff.pop_chord_symbol())
                buff.skip_ignore_abc() # todo change to skip spaces

            if buff.is_tuplet():
                self.process_tuplet(buff.pop_tuplet_no())
            if buff.is_pitch_rest():
                note = buff.pop_pitch_rest()
                top, bottom = buff.pop_duration()
                self.emit.note(note, self.calc_note_duration(top, bottom))
            elif buff.has_more_data():
                assert False, f"unexpected element '{buff.pop_char()}'"

        self.emit.tune_end()

    def calc_note_duration(self, dur_top, dur_bottom):
        duration = (music.PPQN * dur_top * 4 * self.unit_length_top) // (dur_bottom * self.unit_length_bottom)
        if self._tuple_counter > 0:
            self._tuple_counter -= 1
            duration = int(duration * self._tuple_scaling)

        return duration

    def find_matching_tune(self, header):
        if not self.options.tune_search_name:
            return True

        for line in header:
            if len(line) >= 2 and line[1] == ':':
                field = line[0]
                text = line[2:].strip()

                if field == 'X':
                    if text.isdigit():
                        if self.options.abc_tune_id == int(text):
                            return True
                elif field == 'T':
                    if self.is_matching_tune(text):
                        self.tune_search_name = text
                        self.options.abc_tune_title(text)
                        self.io.info(f"ABC2MMA Converting ABC tune '{text}'")
                        return True
                elif field == 'K':
                    break
        return False

    def is_matching_tune(self, text):
        if self.options.tune_search_name is None:
            # returning True means we use the first tune detected
            return True
        return self.options.tune_search_name in text

    def process_tuplet(self, tuplet_no):
        if tuplet_no == 3:
            self._tuple_scaling = 2 / 3
            self._tuple_counter = 3
        else:
            assert False, f"tuplet is ({tuplet_no} is not implemented"
