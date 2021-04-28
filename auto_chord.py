
class AutoChord:

    def __init__(self, user_io, options, emitter):
        self._io = user_io
        self._options = options
        self._emitter = emitter


    def note(self, note, duration):
        if note == 'G':
            self._emitter.chord_symbol("Gm")
        else:
            self._emitter.chord_symbol("C")
