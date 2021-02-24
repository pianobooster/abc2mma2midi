
# TODO see https://stackoverflow.com/questions/2627002/whats-the-pythonic-way-to-use-getters-and-setters
class Options:

    def __init__(self):
        self.repeat_whole_piece = 1
        self.abc_file_name = ''
        self.abc_tune_title = ''
        self.abc_tune_id = -1
        self.alternative_groove = None
        self.patch_mma = False

    def pass_arguments(self, argv):
        from argparse import ArgumentParser

        parser = ArgumentParser(prog='abc2mma',
                                usage="%(prog)s [options] <abc-source-file> <tune-title>"
                                      "\nFor more help type: %(prog)s --help",
                                description='creates a Musical MIDI Accompaniment(MMA) from ABC notation tunes.')
        parser.add_argument('abc_file_name', metavar='<abc-source-file>',
                            help='The file name of the ABC tunes')
        parser.add_argument('abc_tune_title',  metavar='<tune-title>',
                            help='the title of the tune that will be used to generate the musical accompaniment.')
        parser.add_argument('-r', '--repeat', action='store_const', const=2, default=1, dest='repeat_whole_piece',
                            help='Repeat the whole piece twice'  )
        parser.add_argument('-a', '--alternative', action='store_const', const="altGroove", dest='alternative_groove',
                            help='Use alternative Grooves'  )
        parser.add_argument( '--patch-mma', dest='patch_mma', action='store_true', default=False,
                            help='Patch the MIDI file to fix and MMA issue.')
        parser.add_argument('-o', '--output', dest='mma_filename', metavar='FILE',
                            help='write mma output to FILE')
        parser.add_argument('-v', '--verbose',
                            action='store_true', dest='verbose', default=False,
                            help="Display more info on the output")

        args = parser.parse_args(argv[1:])
        args.abc_tune_id = -1
        print(args)
        print(vars(args))
        # print( 'ZZ  abc_file_name @@@@ ' + args.abc_file_name)
        # print( 'ZZ  tune-name  @@@@ ' + args.abc_tune_title)
        # print( 'ZZ  repeat_piece  @@@@ ' + str(args.repeat_whole_piece) )
        # print( 'ZZ  patch-mma  @@@@ ' + str(args.patch_mma) )
        self.abc_file_name = args.abc_file_name
        self.abc_tune_title = args.abc_tune_title
        self.repeat_whole_piece = args.repeat_whole_piece
        self.alternative_groove = args.alternative_groove
        self.patch_mma = args.patch_mma
