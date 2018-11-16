import shutil

import click.testing 
import pytest


@pytest.fixture()
def database(tmpdir):
    source = 'tests/test.bib'
    shutil.copy(source, tmpdir)
    return tmpdir / 'test.bib' 


@pytest.fixture()
def runner():
    return click.testing.CliRunner()
