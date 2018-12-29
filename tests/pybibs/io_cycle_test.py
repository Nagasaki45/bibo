import os

import pybibs


def test_read_then_write_produces_the_same_result(database):
    bib1 = pybibs.read_file(database)
    out1 = pybibs.write_string(bib1)
    bib2 = pybibs.read_string(out1)
    out2 = pybibs.write_string(bib2)
    assert out1 == out2
