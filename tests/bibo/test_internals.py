import os

import click
import pytest

from bibo import internals


def test_destination_heuristic(data, tmpdir):
    assert internals.destination_heuristic(data) == tmpdir


def test_destination_heuristic_empty(data):
    for entry in data:
        if 'file' in entry['fields']:
            del entry['fields']['file']
    with pytest.raises(click.ClickException) as e:
        internals.destination_heuristic(data)
    assert 'no paths in the database' in str(e)


def test_destination_heuristic_multiple_equaly_valid_paths(data):
    for i, entry in enumerate(data):
        entry['fields']['file'] = '/fake/path{}/file'.format(i)
    with pytest.raises(click.ClickException) as e:
        internals.destination_heuristic(data)
    assert 'multiple equally valid' in str(e)


def test_set_file_with_destination(data, example_pdf, tmpdir):
    entry = data[0]
    destination = tmpdir / 'somewhere_else'
    os.mkdir(str(destination))
    internals.set_file(data, entry, example_pdf, str(destination))
    assert os.path.exists(str(destination / entry['key'] + '.pdf'))


def test_get_database():
    args = ['whatever', '--database', 'test.bib', 'whatever']
    assert internals.get_database(args) == 'test.bib'


def test_format_entry(data):
    entry = data[0]
    assert internals.format_entry(entry, '$year') == '1937'
    assert internals.format_entry(entry, '$year: $title') == '1937: The Hobbit'
