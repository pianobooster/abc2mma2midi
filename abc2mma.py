#!/usr/bin/python3

import os
import sys

from generate_mma import GenerateMma
from options import Options
from parse_abc import ParseAbc
from user_io import UserIo


def execute_command(cmd):
    print(cmd)
    if os.system(cmd) != 0:
        sys.exit("Error in: " + cmd)


def rm_file(file_name):
    if os.path.isfile(file_name):
        os.remove(file_name)


def make_dir(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def patch_midi_cvs(file_name, mma_stretch):

    csv_in = open(file_name + ".tmp", 'r')
    csv_out = open(file_name + "-fixed.tmp", 'w')
    convert_tempo = False
    if not mma_stretch:
        mma_stretch = 200.0
    while True:
        csv_line: str = csv_in.readline()
        if not csv_line:
            break
        fields = csv_line.split(',')
        midi_event = fields[2].strip()
        if midi_event == 'Header':
            if '192' in fields[5]:
                convert_tempo = True

                new_ppqn=str(int(round((192*mma_stretch)/100)))
                print(f"PATCHING MMA MIDI FILE: New ppqn {new_ppqn}\n")

                csv_line = csv_line.replace('192', new_ppqn)
        elif midi_event == 'Tempo' and convert_tempo:
            temp_str = fields[3].strip()
            tempo =  int(round((int(temp_str) * mma_stretch) / 100))
            csv_line = csv_line.replace(temp_str, str(tempo))
            print(f"PATCHING MMA MIDI FILE: old MIDI tempo {temp_str} new MIDI tempo {tempo} \n")
        csv_out.write(csv_line)

    csv_in.close()
    csv_out.close()


def patch_mma_midi_output(file_name, options):
    execute_command(f"midicsv \"{file_name}\" \"{file_name}.tmp\"")
    patch_midi_cvs(file_name, options.mma_stretch)

    if options.mma_debug:
        execute_command(f"csvmidi \"{file_name}-fixed.tmp\" \"{file_name}-patched.mid\"")
    else:
        execute_command(f"csvmidi \"{file_name}-fixed.tmp\" \"{file_name}\"")
    rm_file(f'{file_name}-fixed.tmp')
    rm_file(f'{file_name}.tmp')


def create_temp_file(std_in, file_name):

    output = open(file_name, 'w')
    while True:
        line: str = std_in.readline()
        if not line:
            break
        output.write(line)

    output.close()


def get_script_path():
    return os.path.dirname(os.path.realpath(__file__))


class Abc2Mma:

    def __init__(self, options):
        self.options = options

        self.user_io = UserIo()
        emitter = GenerateMma(self.user_io, self.options)
        self.parse_abc = ParseAbc(emitter, self.user_io, self.options)

    def run_abc_mma(self):
        if not self.options._output_filename:
            self.options.outputDir("output") # TODO decide whether this is valid

        if self.options.abc_file_name == '-':
            self.options.abc_file_name = 'temp-abc-file.abc'
            create_temp_file(sys.stdin, self.options.abc_file_name)

        input_file = open(self.options.abc_file_name, encoding="latin-1")
        self.user_io.set_input_file(input_file)

        if not self.parse_abc.build_tune():
            return

        output_file = open(self.options.mma_filename(), 'w')
        self.user_io.set_output_file(output_file)

        self.parse_abc.process_tune()

        tune_id = self.parse_abc.abc_tune_id
        output_file.close()

        # Note abc2midi -BF makes the output play out of time when loaded into a notation program
        execute_command(f"abc2midi  \"{self.options.abc_file_name}\" {tune_id} -o \"{self.options.midi_solo_filename()}\" -RS" ) # ZZ -CS was -RS)
        mma_path = self.options.mma_path
        if mma_path:
            if not os.path.exists(mma_path):
                sys.exit(f"Error mma not found on the path `{mma_path}`")
        else:
            mma_path = 'mma'

        mma_inc_path = os.environ.get('MMA_INCPATH')
        if not mma_inc_path:
            mma_inc_path = f"{get_script_path()}/abc-mma-lib/"

        if not os.path.exists(mma_inc_path):
            sys.exit(f"Error MMA_INCPATH `{mma_inc_path}` does not exist")

        # todo decide about this -II   skip permissions test for plugins (Dangerous!)
        execute_command(f"MMA_INCPATH={mma_inc_path} {mma_path}  -II \"{self.options.mma_filename()}\" -f \"{self.options.midi_filename()}\"")

        if self.parse_abc.time_sig_bottom == 8 and self.options.patch_mma:
            patch_mma_midi_output(self.options.midi_filename(), self.options)

    def pass_args(self, argv):
        for arg in argv:
            print(f"arg '{arg}'")
        self.options.pass_arguments(argv)
        self.run_abc_mma()


if __name__ == "__main__":
    options = Options()
    main = Abc2Mma(options)
    main.pass_args(sys.argv[1:])

