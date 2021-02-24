class MockFile:

    def __init__(self):
        self.file_content = []
        self.idx = 0

    def mock_content(self, text):
        self.file_content = text.splitlines()

    def readline(self):
        if self.idx >= len(self.file_content) :
            return ""

        line = self.file_content[self.idx] + "\n"
        self.idx += 1
        return line
