import pytest

from bibo import internals


def test_destination_heuristic(data, tmpdir):
    assert internals.destination_heuristic(data) == tmpdir


def test_destination_heuristic_empty(data):
    for entry in data:
        if 'file' in entry['fields']:
            del entry['fields']['file']
    with pytest.raises(Exception) as e:
        internals.destination_heuristic(data)
    assert 'no paths in the database' in str(e)


def test_destination_heuristic_multiple_equaly_valid_paths(data):
    for i, entry in enumerate(data):
        entry['fields']['file'] = '/fake/path{}/file'.format(i)
    with pytest.raises(Exception) as e:
        internals.destination_heuristic(data)
    assert 'multiple equally valid' in str(e)
