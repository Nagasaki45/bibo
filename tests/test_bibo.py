import filecmp
import os
from unittest import mock

import click

from bibo import bibo

TO_ADD = '''
@article{haidt2001emotional,
  title={The emotional dog and its rational tail: a social intuitionist approach to moral judgment.},
  author={Haidt, Jonathan},
  journal={Psychological review},
  volume={108},
  number={4},
  pages={814},
  year={2001},
  publisher={American Psychological Association}
}
'''.strip()


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


def test_open(runner, database):
    with mock.patch('bibo.bibo.open_file') as open_file_mock:
        result = runner.invoke(bibo.cli, ['--database', database, 'open', 'tolkien'])
    assert result.exit_code == 0
    assert open_file_mock.call_count == 1


def test_open_no_file_field(runner, database):
    with mock.patch('bibo.bibo.open_file') as open_file_mock:
        result = runner.invoke(bibo.cli, ['--database', database, 'open', 'asimov'])
    assert result.exit_code == 1
    assert 'No file' in result.output


def test_open_no_entry(runner, database):
    with mock.patch('bibo.bibo.open_file') as open_file_mock:
        result = runner.invoke(bibo.cli, ['--database', database, 'open', 'agnon'])
    assert result.exit_code == 1
    assert 'No entries' in result.output


def test_add(runner, database):
    result = runner.invoke(bibo.cli, ['--database', database, 'list', 'haidt'])
    assert result.output == ''

    with mock.patch('click.edit') as edit_mock:
        edit_mock.return_value = TO_ADD
        result = runner.invoke(bibo.cli, ['--database', database, 'add'])
    assert result.exit_code == 0
    assert result.output == ''

    result = runner.invoke(bibo.cli, ['--database', database, 'list', 'haidt'])
    assert 'The emotional dog' in result.output


def test_add_with_file(runner, database, example_pdf, tmpdir):
    with mock.patch('click.edit') as edit_mock:
        edit_mock.return_value = TO_ADD
        args = ['--database', database, 'add', '--pdf', example_pdf]
        result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert result.output == ''
    expected_pdf = tmpdir / 'example.pdf'
    assert os.path.isfile(expected_pdf)
    assert filecmp.cmp(example_pdf, expected_pdf)

    result = runner.invoke(bibo.cli, ['--database', database, 'list', 'haidt'])
    assert 'The emotional dog' in result.output


def test_remove(runner, database):
    args = ['--database', database, 'remove', 'asimov']
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert result.output == ''

    with open(database) as f:
        assert 'asimov' not in f.read()

def test_remove_entry_with_field(runner, database, tmpdir):
    with mock.patch('os.remove') as remove_mock:
        args = ['--database', database, 'remove', 'tolkien']
        result = runner.invoke(bibo.cli, args)
    remove_mock.assert_called_once_with(tmpdir / 'hobbit.pdf')
    assert result.exit_code == 0

def test_remove_field(runner, database, tmpdir):
    args = ['--database', database, 'remove', '--field', 'file', 'tolkien']
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert result.output == ''

    with open(database) as f:
        assert 'hobbit.pdf' not in f.read()
