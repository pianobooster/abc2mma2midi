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
    execute_command(f"midicsv \"{file_name}.mid\" \"{file_name}.tmp\"")
    patch_midi_cvs(file_name, options.mma_stretch)

    if options.mma_debug:
        execute_command(f"csvmidi \"{file_name}-fixed.tmp\" \"{file_name}-patched.mid\"")
    else:
        execute_command(f"csvmidi \"{file_name}-fixed.tmp\" \"{file_name}.mid\"")
    rm_file(f'{file_name}-fixed.tmp')
    rm_file(f'{file_name}.tmp')


class Abc2Mma:

    def __init__(self, options):
        self.options = options

        self.user_io = UserIo()
        emitter = GenerateMma(self.user_io, self.options)
        self.parse_abc = ParseAbc(emitter, self.user_io, self.options)

    def open_file(self):
        output_dir = "output/"
        output_mma_dir = output_dir + "mma/"  # todo add these as proper options
        output_midi_dir = output_dir + "midi/"
        make_dir(output_mma_dir)
        make_dir(output_midi_dir)

        input_file = open(self.options.abc_file_name, encoding="latin-1")
        self.user_io.set_input_file(input_file)
        tune_file_name = self.options.abc_tune_title.replace(' ', '').replace('\t', '')
        if self.options.mma_output_filename:
            mma_output_filename = str(self.options.mma_output_filename)
        else:
            mma_output_filename = tune_file_name

        output_file = open(output_mma_dir + mma_output_filename + ".mma", 'w')
        self.user_io.set_output_file(output_file)

        self.parse_abc.parse_input()

        tune_id = self.parse_abc.abc_tune_id
        output_file.close()
        execute_command("abc2midi \"{0}\" {1} -o \"{2}-solo.mid\" -RS"
                        .format(self.options.abc_file_name, tune_id, output_mma_dir+mma_output_filename))
        mma_path =  self.options.mma_path
        if not mma_path:
            mma_path = 'mma'
        # todo validate mma_path exists
        execute_command("cd \"{0}\";{1}  \"{2}.mma\" -f \"{3}.mid\""
                        .format(output_mma_dir, mma_path, mma_output_filename, "../midi/" + mma_output_filename))

        if self.parse_abc.time_sig_bottom == 8 and self.options.patch_mma:
            patch_mma_midi_output(output_midi_dir + mma_output_filename, self.options)

    def pass_args(self, argv):
        self.options.pass_arguments(argv)
        self.open_file()

        # if len(argv) >= 2:
        #     self.options.abc_file_name = argv[1]
        #     self.options.abc_tune_title = argv[2]
        #     self.options.repeat_whole_piece = 2
        #     self.open_file()
        # else:
        #     print("usage abc2mma <abc-source-file> <tune-title>")


if __name__ == "__main__":
    options = Options()
    main = Abc2Mma(options)
    main.pass_args(sys.argv[1:])

