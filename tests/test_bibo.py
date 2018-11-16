import click

from bibo import bibo


def test_list_non_existing(runner, database):
    result = runner.invoke(bibo.cli, ['--database', database, 'list', 'agnon'])
    assert result.exit_code == 0
    assert result.output == ''


def test_list_author(runner, database):
    result = runner.invoke(bibo.cli, ['--database', database, 'list', 'tolkien'])
    assert result.exit_code == 0
    assert 'The Hobbit' in result.output
    assert 'Foundation' not in result.output


def test_list_multiple_matches(runner, database):
    result = runner.invoke(bibo.cli, ['--database', database, 'list', 'book'])
    assert result.exit_code == 0
    assert 'The Hobbit' in result.output
    assert 'Foundation' in result.output
