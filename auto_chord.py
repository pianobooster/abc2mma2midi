
class AutoChord:

    def __init__(self, user_io, options, emitter):
        self._io = user_io
        self._options = options
        self._emitter = emitter


    def midi_note(self, note, duration):
        scale = note % 12
        if scale == 7:
            self._emitter.chord_symbol("G")
        else:
            self._emitter.chord_symbol("C")
