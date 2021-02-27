import pathlib
from argparse import ArgumentParser


# TODO see https://stackoverflow.com/questions/2627002/whats-the-pythonic-way-to-use-getters-and-setters
class Options:

    def __init__(self):
        # Only set here to prevent python warnings
        self.grooves_string = None

        # Variables not created by argparse go here
        self.abc_tune_id = None
        #self.mma_path = "/home/louis/Tools/mma-bin-20.12/mma.py"

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
        self._parser.add_argument('abc_tune_title',  metavar='<tune-title>',
                            help='The title of the tune that will be used to generate the musical accompaniment.')
        self._parser.add_argument('-r', '--repeat', action='store_const', const=2, default=1, dest='repeat_whole_piece',
                            help='Repeat the whole piece twice'  )
        self._parser.add_argument('-a', '--alternative', action='store_const', const="altGroove", dest='alternative_groove',
                            help='Use alternative Grooves'  )
        self._parser.add_argument('-o', '--output', dest='mma_output_filename', metavar='FILE', type=pathlib.Path,
                            help='Write mma output to FILE')
        self._parser.add_argument('--mma-path', metavar='MMA-PATH', type=pathlib.Path,
                            help='Sets the MMA-PATH to the mma executable (mma.py)')
        # self._parser.add_argument('-t', '--tempo', metavar='STRETCH', type=int,
        #                     help='Sets the tempo (default 140)')
        self._parser.add_argument('-v', '--verbose',
                            action='store_true', dest='verbose', default=False,
                            help="Display more info on the output")
        self._parser.add_argument( '--patch-mma', dest='patch_mma', action='store_true', default=False,
                            help='Patch the MIDI file to fix and MMA issue.')
        self._parser.add_argument('-g', '--grooves', dest='grooves_string', metavar='GROOVES',
                            help='A comma separated list of GROOVES to use')
        self._parser.add_argument('--mma-stretch', metavar='STRETCH', type=float,
                            help='Sets the mma STRETCH variable (set 100 to disable)')
        self._parser.add_argument('--mma-debug', action='store_true', default=False,
                            help='Changes the behaviour to help debug MMA')


    def pass_arguments(self, argv):
        self._parser.parse_args(argv, self)

    def get_grooves(self):
        if not self.grooves_string:
            return None

        groove_list = self.grooves_string.split(',')
        return [x.strip(' ') for x in groove_list]

