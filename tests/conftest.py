import shutil

import click.testing 
import pytest

from bibo import pybibs


@pytest.fixture()
def database(tmpdir):
    with open('tests/test.bib') as f:
        bib_content = f.read()
    bib_content = bib_content.replace('TMPDIR_PLACEHOLDER', str(tmpdir))
    destination = str(tmpdir / 'test.bib')
    with open(destination, 'w') as f:
        f.write(bib_content)
    return destination


@pytest.fixture()
def example_pdf(tmpdir):
    source = 'tests/example.pdf'
    shutil.copy(source, str(tmpdir))
    return str(tmpdir / 'example.pdf')


@pytest.fixture()
def runner():
    return click.testing.CliRunner()


@pytest.fixture()
def data(database):
    return pybibs.read_file(database)
