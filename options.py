import pathlib
from argparse import ArgumentParser


class Options:

    def __init__(self):
        # Only set here to prevent python warnings
        self.grooves_string = None

        # Variables not created by argparse go here
        self.abc_tune_id = None
        # self.mma_path = "/home/louis/Tools/mma-bin-20.12/mma.py"
        self._output_filename = None
        self._abc_tune_title = None

        self._outputDir = None

        self.init_arg_parse()

        # see test_default_options() for the full list of variables created by this call
        self.pass_arguments(['', ''])

    def init_arg_parse(self):
        self._parser = ArgumentParser(prog='abc2mma',
                                      usage="%(prog)s [options] <abc-source-file> <tune-title>"
                                            "\nFor more help type: %(prog)s --help",
                                      description='creates a Musical MIDI Accompaniment(MMA) from ABC notation tunes.')

        self._parser.add_argument('abc_file_name', metavar='<abc-source-file>',
                                  help='The file name of the ABC tunes')
        self._parser.add_argument('tune_search_name',  nargs='?', metavar='<tune-title>', default=None,
                                  help='The title of the tune that will be used to generate the musical accompaniment.')
        self._parser.add_argument('-r', '--repeat', action='store_const', const=2, default=1, dest='repeat_whole_piece',
                                  help='Repeat the whole piece twice')
        self._parser.add_argument('-a', '--alternative', action='store_const', const="altGroove",
                                  dest='alternative_groove',
                                  help='Use alternative Grooves')
        self._parser.add_argument('-o', '--output', dest='_output_filename', metavar='FILE', type=pathlib.Path,
                                  help='Write mma output to FILE ??') # ZZ this specifies the midi or mma file names
        self._parser.add_argument('--mma-path', metavar='MMA-PATH', type=pathlib.Path,
                                  help='Sets the MMA-PATH to the mma executable (mma.py)')
        # self._parser.add_argument('-t', '--tempo', metavar='STRETCH', type=int,
        #                     help='Sets the tempo (default 140)')
        self._parser.add_argument('-v', '--verbose',
                                  action='store_true', dest='verbose', default=False,
                                  help="Display more info on the output")
        self._parser.add_argument('-g', '--grooves', dest='grooves_string', metavar='GROOVES',
                                  help='A comma separated list of GROOVES to use')
        self._parser.add_argument('--mma-stretch', metavar='STRETCH', type=float,
                                  help='Sets the mma STRETCH variable (set 100 to disable)')
        self._parser.add_argument('--mma-debug', action='store_true', default=False,
                                  help='Changes the behaviour to help debug MMA')
        self._parser.add_argument('--patch-mma', action='store_true', default=False,
                                  help='Patch the MIDI file to fix and MMA issue.')
        self._parser.add_argument('--mma-fix', action='store_true', default=False,
                                  help='Changes the behaviour MMA')

        self._parser.add_argument('-BF', action='store_true', default=False,
                                  help='Barfly mode: invokes a stress model if possible (abc2midi)')
        #self._parser.add_argument('-EA', action='store_true', default=False,
        self._parser.add_argument('-EA', action='store_const', const=2, default=1, dest='repeat_whole_piece',
                                  help='Easy ABC mode? (abc2midi)')
        self._parser.add_argument('-TT', dest='abc2midi_tune_to', metavar='frequency',
                                  help='tune to A =  <frequency> (abc2midi)')
        self._parser.add_argument('-TT 440', dest='xabc2midi_tune_to', action='store_true', default=False,
                                  help='xtune to A =  <frequency> (abc2midi)')

    def pass_arguments(self, argv):
        self._parser.parse_args(argv, self)

    def get_grooves(self):
        if not self.grooves_string:
            return None

        groove_list = self.grooves_string.split(',')
        return [x.strip(' ') for x in groove_list]

    def get_filename_stem(self):
        if self._output_filename:
            filename = self._output_filename
            suffix = self._output_filename.suffix.lower()
            if suffix == '.midi' or suffix == '.mid' or suffix == '.mma':
                filename = self._output_filename.with_suffix("")
        else:
            filename = "NONE"
        return str(filename)

    def midi_filename(self):
        filename = self._output_filename
        assert filename
        suffix = self._output_filename.suffix.lower()
        if suffix == '.midi' or suffix == '.mid':
            filename = self._output_filename
        else:
            filename = self.get_filename_stem() + ".mid"

        if self._outputDir:
            filename = self._outputDir + '/midi/' + filename # TODO decide about creating this dir
        return str(filename)

    def midi_solo_filename(self):
        filename = self.get_filename_stem() + "-solo.mid"
        if self._outputDir:
            filename = self._outputDir + '/mma/' + filename  # TODO decide about creating this dir
        return str(filename)

    def mma_filename(self):
        filename = self.get_filename_stem() + ".mma"
        if self._outputDir:
            filename = self._outputDir + '/mma/' + filename
        return str(filename)

    def mma_parent(self):
        return str(self.self._output_filename.parent())

    def abc_tune_title(self, name):
        self._abc_tune_title = name
        if not self._output_filename:
            self._output_filename = pathlib.PosixPath(name.replace(' ', '').replace('\t', ''))

    def outputDir(self, outputDir):
        self._outputDir = outputDir
