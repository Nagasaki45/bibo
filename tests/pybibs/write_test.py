import pybibs


def test_write_string(raw, parsed):
    assert pybibs.write_string(parsed) == raw
