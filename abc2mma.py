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


def patch_midi_cvs(file_name):

    csv_in = open(file_name + ".tmp", 'r')
    csv_out = open(file_name + "-fixed.tmp", 'w')
    convert_tempo = False
    while True:
        csv_line: str = csv_in.readline()
        if not csv_line:
            break
        fields = csv_line.split(',')
        midi_event = fields[2].strip()
        if midi_event == 'Header':
            if '192' in fields[5]:
                convert_tempo = True
                csv_line = csv_line.replace('192', '384')
        elif midi_event == 'Tempo' and convert_tempo:
            temp_str = fields[3].strip()
            tempo = int(temp_str) *2
            #print("SVG BUG FIX: replacing '{0}' with '{1}'".format(old_text, new_text))
            csv_line = csv_line.replace(temp_str, str(tempo))
        csv_out.write(csv_line)

    csv_in.close()
    csv_out.close()


def patch_mma_midi_output(file_name):
    execute_command("midicsv \"{0}.mid\" \"{0}.tmp\"".format(file_name))
    patch_midi_cvs(file_name)
    execute_command("csvmidi \"{0}-fixed.tmp\" \"{0}.mid\"".format(file_name))
    rm_file('{0}-fixed.tmp'.format(file_name))
    rm_file('{0}.tmp'.format(file_name))


class Abc2Mma:

    def __init__(self, options):
        self.options = options

        self.user_io = UserIo()
        emitter = GenerateMma(self.user_io, self.options)
        self.parse_abc = ParseAbc(emitter, self.user_io, self.options)

    def open_file(self):
        make_dir('build/mma')
        make_dir('build/midi')
        output_dir = "build/"
        output_mma_dir = output_dir + "mma/"
        output_midi_dir = "build/midi/"

        input_file = open(self.options.abc_file_name, encoding="latin-1")
        self.user_io.set_input_file(input_file)
        tune_file_name = self.options.abc_tune_title.replace(' ', '').replace('\t', '')
        output_file = open(output_mma_dir + tune_file_name + ".mma", 'w')
        self.user_io.set_output_file(output_file)

        self.parse_abc.parse_input()
        #ZZ TBD tune_file_name = self.parse_abc.abc_tune_title.replace(' ', '').replace('\t', '')
        # abc2midi  files/pgh_session_tunebook.abc 2044  -o build/BangUpp-solo.mid

        tune_id = self.parse_abc.abc_tune_id
        output_file.close()
        execute_command("abc2midi \"{0}\" {1} -o \"{2}-solo.mid\" -RS".format(self.options.abc_file_name, tune_id, output_mma_dir+tune_file_name))
        execute_command("cd \"{0}\";mma  \"{1}.mma\" -f \"{2}.mid\"".format(output_mma_dir, tune_file_name, "../midi/" + tune_file_name))

        if self.parse_abc.time_sig_bottom == 8 and self.options.patch_mma:
            patch_mma_midi_output(output_midi_dir + tune_file_name)

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
    main.pass_args(sys.argv)

