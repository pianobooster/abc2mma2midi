
class AutoChord:

    def __init__(self, user_io, options, emitter):
        self._io = user_io
        self._options = options
        self._emitter = emitter

    def key_sig(self, key_sig ):
        pass

    def time_sig(self, top, bottom ):
        pass

    def midi_note(self, note, duration):
        major_chord_number_lookup = ['I', '?', 'V', '?', 'I', 'IV', '?', 'V', '?', 'IV', '?', 'V']

        # Runs 0 to 11 including all the semitones
        scale = note % 12
        chord_number = major_chord_number_lookup[scale]
        key_c_major_lookup = {'I':'C',  'IV':'F',  'V':'G', '?':'??'}
        chord_name = key_c_major_lookup[chord_number]

        self._emitter.chord_symbol(chord_name)
