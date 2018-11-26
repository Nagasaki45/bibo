import shutil

import click.testing 
import pytest


@pytest.fixture()
def database(tmpdir):
    with open('tests/test.bib') as f:
        bib_content = f.read()
    bib_content = bib_content.replace('TMPDIR_PLACEHOLDER', str(tmpdir))
    destination = tmpdir / 'test.bib'
    with open(destination, 'w') as f:
        f.write(bib_content)
    return destination


@pytest.fixture()
def example_pdf(tmpdir):
    source = 'tests/example.pdf'
    shutil.copy(source, tmpdir)
    return tmpdir / 'example.pdf'


@pytest.fixture()
def runner():
    return click.testing.CliRunner()
