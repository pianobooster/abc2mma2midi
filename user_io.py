
class UserIo:

    def __init__(self):
        self.input_file = None
        self.output_file = None
        self.lines_available = False
        self.output_lines = []
        self.errors_messages = []
        self.line_counter = 0

    def set_input_file(self, input_file):
        self.input_file = input_file
        self.lines_available = True
        self.line_counter = 0

    def set_output_file(self, output_file):
        self.output_file = output_file

    def read_line(self):
        line = self.input_file.readline()
        if not line:
            self.lines_available = False
            return ""

        self.line_counter += 1
        return line

    def error(self, message):
        if not self.output_lines:
            print("\n")
        if self.output_file:
            self.output_file.write("// ABC2MMA ERROR: " + message + '\n')
        error_text = "ERROR: " + message
        print(error_text)
        self.output_lines.append(error_text)
        self.errors_messages.append(error_text)

    def info(self, message):
         print(message)

    def lines_available(self):
        return self.lines_available

    def out_print(self, message=""):
        if self.output_file:
            self.output_file.write(message + '\n')
        else:
            if not self.output_lines:
                print("\n")
            print(message)
            self.output_lines.append(message)

    def has_errors(self):
        return len(self.errors_messages) > 0

    def output_text(self):
        return "\n".join(self.output_lines)
