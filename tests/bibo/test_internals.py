import os
import shutil

import click
import pytest

from bibo import internals


def test_destination_heuristic(data, tmpdir):
    assert internals.destination_heuristic(data) == tmpdir


def test_destination_heuristic_empty(data):
    for entry in data:
        if 'file' in entry.get('fields', []):
            del entry['fields']['file']
    with pytest.raises(click.ClickException, match='.*no paths in the database') as e:
        internals.destination_heuristic(data)


def test_destination_heuristic_multiple_equaly_valid_paths(data):
    for i, entry in enumerate(data):
        if 'fields' in entry:
            entry['fields']['file'] = '/fake/path{}/file'.format(i)
    with pytest.raises(click.ClickException, match='.*there are multiple equally valid paths in the database') as e:
        internals.destination_heuristic(data)


def test_set_file_with_destination(data, example_pdf, tmpdir):
    entry = data[0]
    destination = tmpdir / 'somewhere_else'
    os.mkdir(str(destination))
    internals.set_file(data, entry, example_pdf, str(destination))
    assert os.path.exists(str(destination / entry['key'] + '.pdf'))

def test_set_file_exists_already(data, example_pdf, tmpdir):
    entry = data[0]
    # Create an existing pdf, specified by user as relative path
    ext = os.path.splitext(example_pdf)[1]
    dest = tmpdir / 'subdir'
    os.mkdir(dest.strpath)
    existing_pdf = shutil.copyfile(example_pdf, dest.join(entry['key'] + ext))
    relative_file = os.path.join('subdir', os.path.basename(existing_pdf))
    with tmpdir.as_cwd():
        try:
            internals.set_file(data, entry, relative_file, dest.strpath)
        except shutil.SameFileError as e:
            pytest.fail('Raised {}'.format(repr(e)))

def test_get_database():
    args = ['whatever', '--database', 'test.bib', 'whatever']
    assert internals.get_database(args) == 'test.bib'


def test_format_entry(data):
    entry = data[0]
    assert internals.format_entry(entry, '$year') == '1937'
    assert internals.format_entry(entry, '$year: $title') == '1937: The Hobbit'
