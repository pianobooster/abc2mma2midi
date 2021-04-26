import pytest


from generate_mma import GenerateMma
from options import Options
from parse_abc import ParseAbc
from tests.mock_file import MockFile
from user_io import UserIo


@pytest.fixture
def options():
    return Options()


@pytest.fixture
def mock_file():
    return MockFile()


@pytest.fixture
def user_io():
    return UserIo()


@pytest.fixture
def emitter(user_io, options):
    options.repeat_whole_piece = 2
    # Note GenerateMma IS the emitter (there may be more emitters in future)
    return GenerateMma(user_io, options)


@pytest.fixture
def parse_abc(emitter, user_io, options,  mock_file):
    user_io.set_input_file(mock_file)
    return ParseAbc(emitter, user_io, options)

abc_bang_up = """
X:2044
T:Bang Upp
R:Jig
C:Trad.
O:England, Norfolk
Z:Paul Hardy's Session Tunebook 2017 (see www.paulhardy.net). Creative Commons cc by-nc-sa licenced.
M:6/8
L:1/8
Q:3/8=120
K:D
A|"D"d2d f2f|a2a f2d|"G"g2e "D"f2d|"A"cde ABc|"D"d2d f2f|a2a f2d|"G"g2e "D"f2d|"A7"cBA "D"d2:|
|:A|"D"F2A "A"E2A|"D"F2A d2c|"G"B2d "D"A2d|"Em"G2e "A7"cBA|"D"F2A "A"E2A|"D"F2A d2c|"G"Bcd "A7"ABc|"D"d3-d2:|
|:A|"D"f2e d2c|"G"B2A G2F|G2A B2e|"A7"dcB A2A|"D"f2e d2c|"G"B2A G2F|G2B "A7"A2F|GFE "D"D2:|

"""

abc_bang_up_patched = """
X:2044
T:Bang Upp
R:Jig
C:Trad.
O:England, Norfolk
Z:Paul Hardy's Session Tunebook 2017 (see www.paulhardy.net). Creative Commons cc by-nc-sa licenced.
M:6/8
L:1/8
Q:3/8=120
K:D
|:   A|"D"d2d f2f|a2a f2d|"G"g2e "D"f2d|"A"cde ABc|"D"d2d f2f|a2a f2d|"G"g2e "D"f2d|"A7"cBA "D"d2:|
|:A|"D"F2A "A"E2A|"D"F2A d2c|"G"B2d "D"A2d|"Em"G2e "A7"cBA|"D"F2A "A"E2A|"D"F2A d2c|"G"Bcd "A7"ABc|"D"d3-d2:|
|:A|"D"f2e d2c|"G"B2A G2F|G2A B2e|"A7"dcB A2A|"D"f2e d2c|"G"B2A G2F|G2B "A7"A2F|GFE "D"D2:|


"""


def test_abc2mma(mock_file, parse_abc):
    mock_file.mock_content(abc_bang_up)
    parse_abc.parse_input()


def test_abc2mma_patched(mock_file, parse_abc):
    mock_file.mock_content(abc_bang_up_patched)
    parse_abc.parse_input()

