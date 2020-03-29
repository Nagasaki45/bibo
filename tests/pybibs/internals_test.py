from pybibs import _internals


def test_split_entries(raw):
    raw_entries = list(_internals.split_entries(raw))
    assert len(raw_entries) == 2


def test_parse_raw_key_values(raw_entry_key_values):
    gen = _internals.parse_raw_key_values(raw_entry_key_values)
    key, val = next(gen)
    assert key == "author"
    assert val == "Israel, Moshe"
    key, val = next(gen)
    assert key == "title"
    assert val == "Some title"


def test_parse_value():
    assert _internals.parse_value(' "Israel, Moshe",\n') == "Israel, Moshe"
    assert _internals.parse_value(" 2008\n") == "2008"
