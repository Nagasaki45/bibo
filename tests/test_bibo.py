import filecmp
import os
try:
    from unittest import mock
except ImportError:
    import mock

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


def test_list_with_multiple_search_terms(runner, database):
    args = ['--database', database, 'list', 'book', 'year:1937']
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert 'The Hobbit' in result.output
    assert 'The Lord of the Rings' not in result.output


def test_list_with_search_by_field(runner, database):
    args = ['--database', database, 'list', 'type:trilogy']
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert 'The Hobbit' not in result.output
    assert 'The Lord of the Rings' in result.output


def test_list_with_no_arguments_to_get_everything(runner, database, data):
    args = ['--database', database, 'list']
    result = runner.invoke(bibo.cli, args)
    for entry in data:
        assert entry['key'] in result.output


def test_open(runner, database):
    with mock.patch('bibo.internals.open_file') as open_file_mock:
        args = ['--database', database, 'open', 'tolkien1937']
        result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert open_file_mock.call_count == 1


def test_open_no_file_field(runner, database):
    with mock.patch('bibo.internals.open_file') as open_file_mock:
        result = runner.invoke(bibo.cli, ['--database', database, 'open', 'asimov'])
    assert result.exit_code == 1
    assert 'No file' in result.output


def test_open_no_entry(runner, database):
    with mock.patch('bibo.internals.open_file') as open_file_mock:
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
        args = ['--database', database, 'add', '--file', example_pdf]
        result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert result.output == ''
    expected_pdf = str(tmpdir / 'haidt2001emotional.pdf')
    assert os.path.isfile(expected_pdf)
    assert filecmp.cmp(example_pdf, expected_pdf)

    result = runner.invoke(bibo.cli, ['--database', database, 'list', 'haidt'])
    assert 'The emotional dog' in result.output


def test_add_file_with_destination(runner, database, example_pdf, tmpdir):
    destination = tmpdir / 'destination'
    os.mkdir(str(destination))
    with mock.patch('click.edit') as edit_mock:
        edit_mock.return_value = TO_ADD
        args = ['--database', database, 'add', '--file', example_pdf,
                '--destination', str(destination)]
        result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert os.path.isfile(str(destination / 'haidt2001emotional.pdf'))


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


def test_remove_field(runner, database):
    args = ['--database', database, 'remove', '--field', 'file', 'tolkien1937']
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert result.output == ''

    with open(database) as f:
        assert 'hobbit.pdf' not in f.read()


def test_edit_type(runner, database):
    args = ['--database', database, 'edit', '--type', 'comics', 'asimov']
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert result.output == ''

    with open(database) as f:
        assert '@comics{asimov' in f.read()


def test_edit_key(runner, database):
    args = ['--database', database, 'edit', '--key', 'asimov_rules', 'asimov']
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert result.output == ''

    with open(database) as f:
        assert '@book{asimov_rules' in f.read()


def test_edit_file(runner, database, example_pdf, tmpdir):
    args = ['--database', database, 'edit', '--file', example_pdf, 'asimov']
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert result.output == ''

    with open(database) as f:
        assert 'asimov1951foundation.pdf' in f.read()

    expected_pdf = str(tmpdir / 'example.pdf')
    assert os.path.isfile(expected_pdf)
    assert filecmp.cmp(example_pdf, expected_pdf)


def test_edit_field(runner, database):
    args = ['--database', database, 'edit', '--field', 'title', 'asimov']
    with mock.patch('click.edit') as edit_mock:
        edit_mock.return_value = 'THE HOBBIT!'
        result = runner.invoke(bibo.cli, args)

    with open(database) as f:
        assert 'title = {THE HOBBIT!}' in f.read()


def test_add_to_empty_database(runner, tmpdir):
    database = str(tmpdir / 'new.bib')
    with mock.patch('click.edit') as edit_mock:
        edit_mock.return_value = TO_ADD
        args = ['--database', database, 'add']
        result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert result.output == ''

    with open(database) as f:
        assert 'The emotional dog' in f.read()
