import re

# NOTE: from the regex manual "the following chars need escaping [ ] - and ^ only if first"
from music import Barline

# Order of constructs for abc note: <grace notes>, <chord symbols>, <annotations>/<decorations> , <accidentals>, <note>, <octave>, <note length>
# i.e. ~^c'3 or even "Gm7"v.=G,2.
ACCIDENTAL = re.compile('[_=^]')
PITCH_OR_REST_NAME = re.compile('[a-gA-GzZx]')
PITCH_OR_REST = re.compile("[_=^a-gA-GzZx,']")
PITCH_OR_REST_START = re.compile("[_=^a-gA-GzZx]")
OCTAVE = re.compile("[,']")
IGNORE_TUNE_BODY_FIELD_LINES = re.compile("[IKLMmNPQRrsTUVWw]:")
DIGIT = re.compile('[0-9]')
BAR_LINE = re.compile('[|:\\[\\]]')
IGNORE_ABC_START = re.compile('[- \t><.]') # todo remove the '-' '<' '>' these are ties and broken rhythm
NOT_IMPLEMENTED_IGNORE = re.compile('[-]') # todo write code for this '-' is a tie
NOT_IMPLEMENTED_ERROR_START = re.compile('[-]')  # todo write code for this


class AbcFormatError(Exception):

    def __init__(self, message, line_pos):
        self.message = message
        self.line_pos = line_pos


class AbcBuffer:

    def __init__(self, source):
        self.line_pos = 0
        self.next_is_repeat_start = False
        if not source:
            raise AbcFormatError("Empty abc Body", self.line_pos)

        if isinstance( source, list):
            source = "\n" + "\n".join(source)
        self.buffer = list(source)

    def match(self, patten, start=0, end=1):
        if len(self.buffer) >= end:
            text = ''.join(self.buffer[start:end])

            if isinstance(patten, re.Pattern):
                result = patten.match(text)
            else:
                result = re.match('['+ patten + ']', text)
            if result is not None:
                return True

        return False

    def has_more_data(self):
        return len(self.buffer) > 0

    def pop_char(self):
        if len(self.buffer) == 0:
            raise EOFError()
        c = self.buffer.pop(0)
        self.line_pos +=1
        return c

    def pop_pitch_rest(self):
        accidental_count = 0
        pitch = ""
        while self.match(ACCIDENTAL) and accidental_count < 2:
            pitch += self.pop_char()
            accidental_count += 1
        if self.match(PITCH_OR_REST_NAME):
            pitch += self.pop_char()
        else:
            raise AbcFormatError("Badly formatted note", self.line_pos)
        while self.match(OCTAVE):
            pitch += self.pop_char()

        return pitch

    def pop_duration(self):
        top = 1
        bottom = 1
        s = ""
        if self.match(DIGIT):
            while self.match(DIGIT):
                s += self.pop_char()
            top = int(s)
        if self.match('/'):
            s += self.pop_char()
            bottom = 2
        s = ""
        if self.match(DIGIT):
            while self.match(DIGIT):
                s += self.pop_char()
            bottom = int(s)

        return top , bottom

    def is_pitch_rest(self):
        return self.has_more_data() and self.match(PITCH_OR_REST_START)

    def is_barline(self):
        if self.next_is_repeat_start:
            return True

        if self.has_more_data() and self.match(BAR_LINE):
            if len(self.buffer) >=2:
                a = self.buffer[0]
                if a == '|':
                    return True
                b = self.buffer[1]
                if a == '[' and b == '|' or a == ':' and (b == '|' or b == ':'):
                    return True
            else:
                return True
        return False

    def pop_barline(self):
        if self.next_is_repeat_start:
            self.next_is_repeat_start = False
            return Barline.RepeatStart

        bl = ""
        if self.match(BAR_LINE):
            bl += self.pop_char()
        if self.match(BAR_LINE):
            bl += self.pop_char()

        if bl == "|" or  bl == "|]" or  bl == "||" or  bl == "[|":
            return Barline.Standard
        elif  bl == "|:":
            return Barline.RepeatStart
        elif  bl == ":|":
            return Barline.RepeatEnd
        elif  bl == "::":
            self.next_is_repeat_start = True;
            return Barline.RepeatEnd

    def is_ignore_abc(self):
        return self.has_more_data() and self.match(IGNORE_ABC_START)

    def skip_ignore_abc(self):
        while self.is_ignore_abc():
            self.pop_char()

    def is_chord_symbol(self):
        return self.has_more_data() and self.buffer[0] == '"'

    def pop_chord_symbol(self):
        if self.buffer[0] == '"':
            chord = ""
            self.pop_char()
            while True:
                c = self.pop_char()
                if c == '"':
                    break
                chord += c
            return chord
        else:
            assert False, "is_chord_symbol() should be called first"

    def is_tuplet(self):
        if len(self.buffer) >= 2 and self.buffer[0] == '(' and '1' <= self.buffer[1] <= '9':
            return True
        return False

    def pop_tuplet_no(self):
        if self.pop_char() == '(':
            return int(self.pop_char())
        else:
            raise AbcFormatError("Badly formatted tuplet", self.line_pos)

    def is_new_line(self):
        return self.has_more_data() and self.buffer[0] == '\n'

    def is_ignore_body_field_line(self):
        if len(self.buffer) >= 3 and self.buffer[0] == '\n':
            if self.match('%%', 1, 3):
                return True
            return self.match(IGNORE_TUNE_BODY_FIELD_LINES, 1, 3)

    def skip_ignored_body_field_lines(self):
        while self.is_ignore_body_field_line():
            self.pop_char()
            while self.has_more_data() and self.buffer[0] != '\n':
                self.pop_char()
