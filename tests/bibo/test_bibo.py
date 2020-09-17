import filecmp
import os
from unittest import mock

import click
import requests

from bibo import bibo
import pybibs

TO_ADD = """
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
""".strip()


def test_list_non_existing(runner, database):
    result = runner.invoke(bibo.cli, ["--database", database, "list", "agnon"])
    assert result.exit_code == 0
    assert result.output == ""


def test_list_author(runner, database):
    result = runner.invoke(bibo.cli, ["--database", database, "list", "tolkien"])
    assert result.exit_code == 0
    assert "The Hobbit" in result.output
    assert "Foundation" not in result.output


def test_list_multiple_matches(runner, database):
    result = runner.invoke(bibo.cli, ["--database", database, "list", "book"])
    assert result.exit_code == 0
    assert "The Hobbit" in result.output
    assert "Foundation" in result.output


def test_list_with_multiple_search_terms(runner, database):
    args = ["--database", database, "list", "book", "year:1937"]
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert "The Hobbit" in result.output
    assert "The lord of the rings" not in result.output


def test_list_with_search_by_field(runner, database):
    args = ["--database", database, "list", "type:trilogy"]
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert "The Hobbit" not in result.output
    assert "The lord of the rings" in result.output


def test_list_with_no_arguments_to_get_everything(runner, database):
    args = ["--database", database, "list"]
    result = runner.invoke(bibo.cli, args)
    for entry in pybibs.read_file(database):
        if entry["type"] not in ["string", "comment", "preamble"]:
            assert entry["key"] in result.output


def test_list_with_format_pattern(runner, database):
    args = ["--database", database, "list", "hobbit", "--format", "$year"]
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert result.output.strip() == "1937"


def test_list_shows_only_bib_entries(runner, database):
    args = ["--database", database, "list"]
    result = runner.invoke(bibo.cli, args)
    for non_bib_type in ["string", "comment", "preamble"]:
        assert non_bib_type not in result.output


def test_list_extra_match_info(runner, database):
    args = ["--database", database, "list", "lotr.com"]
    result = runner.invoke(bibo.cli, args)
    assert "matched by" in result.output
    assert "url: " in result.output


def test_open(runner, database):
    with mock.patch("click.launch") as launch_mock:
        args = ["--database", database, "open", "tolkien1937"]
        result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert launch_mock.call_count == 1


def test_open_no_file_field(runner, database):
    with mock.patch("click.launch") as launch_mock:
        result = runner.invoke(bibo.cli, ["--database", database, "open", "asimov"])
    assert result.exit_code == 1
    assert "No file" in result.output


def test_open_no_entry(runner, database):
    with mock.patch("click.launch") as launch_mock:
        result = runner.invoke(bibo.cli, ["--database", database, "open", "agnon"])
    assert result.exit_code == 1
    assert "No entries" in result.output


def test_open_url(runner, database):
    with mock.patch("click.launch") as launch_mock:
        result = runner.invoke(
            bibo.cli, ["--database", database, "open", "lord of the rings"]
        )
    assert result.exit_code == 0
    assert launch_mock.call_count == 1
    launch_mock.assert_called_once_with("https://lotr.com")


def test_open_doi(runner, database):
    with mock.patch("click.launch") as launch_mock:
        result = runner.invoke(bibo.cli, ["--database", database, "open", "duncan"])
    assert result.exit_code == 0
    assert launch_mock.call_count == 1
    launch_mock.assert_called_once_with("https://doi.org/10.1016/0022-1031(74)90070-5")


def test_add(runner, database):
    result = runner.invoke(bibo.cli, ["--database", database, "list", "haidt"])
    assert result.output == ""

    with mock.patch("click.edit") as edit_mock:
        edit_mock.return_value = TO_ADD
        result = runner.invoke(bibo.cli, ["--database", database, "add"])
    assert result.exit_code == 0
    assert result.output == ""

    result = runner.invoke(bibo.cli, ["--database", database, "list", "haidt"])
    assert "The emotional dog" in result.output


def test_add_with_file(runner, database, example_pdf, tmpdir):
    with mock.patch("click.edit") as edit_mock:
        edit_mock.return_value = TO_ADD
        args = ["--database", database, "add", "--file", example_pdf]
        result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert result.output.startswith("Copying ")
    expected_pdf = str(tmpdir / "haidt2001emotional.pdf")
    assert os.path.isfile(expected_pdf)
    assert filecmp.cmp(example_pdf, expected_pdf)

    result = runner.invoke(bibo.cli, ["--database", database, "list", "haidt"])
    assert "The emotional dog" in result.output


def test_add_file_with_destination(runner, database, example_pdf, tmpdir):
    destination = tmpdir / "destination"
    os.mkdir(str(destination))
    with mock.patch("click.edit") as edit_mock:
        edit_mock.return_value = TO_ADD
        args = [
            "--database",
            database,
            "add",
            "--file",
            example_pdf,
            "--destination",
            str(destination),
        ]
        result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert os.path.isfile(str(destination / "haidt2001emotional.pdf"))


def test_add_file_no_copy(runner, database):
    # Note that this is the actual test pdf. Not the temp copy!
    filepath = "tests/bibo/example.pdf"

    with mock.patch("click.edit") as edit_mock:
        edit_mock.return_value = TO_ADD
        args = ["--database", database, "add", "--file", filepath, "--no-copy"]
        result = runner.invoke(bibo.cli, args)

    with open(database) as f:
        data = pybibs.read_string(f.read())
    for item in data:
        if item.get("key") == "haidt2001emotional":
            assert item["fields"]["file"] == os.path.abspath(filepath)
            break
    else:
        raise AssertionError("Item not found")


def test_add_without_saving(runner, database):
    with mock.patch("click.edit") as edit_mock:
        edit_mock.return_value = None
        args = ["--database", database, "add"]
        result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 1
    assert "editor exited" in result.output.lower()


def test_add_doi(runner, database):
    class MockResponse:
        status_code = 200
        text = "@article{webdoi, title={Just got it from the web}}"

    with mock.patch("requests.get") as get_mock, mock.patch("click.edit") as edit_mock:
        get_mock.return_value = MockResponse()
        edit_mock.return_value = get_mock.return_value.text
        args = ["--database", database, "add", "--doi", "my-doi-123"]
        result = runner.invoke(bibo.cli, args)
        get_mock.assert_called_once()
    assert result.exit_code == 0

    result = runner.invoke(bibo.cli, ["--database", database, "list", "webdoi"])
    assert "Just got it from the web" in result.output


def test_remove(runner, database):
    args = ["--database", database, "remove", "asimov1951foundation"]
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert result.output == ""

    with open(database) as f:
        assert "asimov" not in f.read()


def test_remove_field(runner, database):
    args = ["--database", database, "remove", "tolkien1937hobit", "file"]
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert result.output == ""

    with open(database) as f:
        assert "hobbit.pdf" not in f.read()


def test_edit_type(runner, database):
    args = ["--database", database, "edit", "asimov1951foundation", "type=comics"]
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert result.output == ""

    with open(database) as f:
        assert "@comics{asimov" in f.read()


def test_edit_key(runner, database):
    args = ["--database", database, "edit", "asimov1951foundation", "key=asimov_rules"]
    result = runner.invoke(bibo.cli, args)
    assert result.output == ""
    assert result.exit_code == 0

    with open(database) as f:
        assert "@book{asimov_rules" in f.read()


def test_edit_key_duplicate(runner, database):
    args = [
        "--database",
        database,
        "edit",
        "asimov1951foundation",
        "key=tolkien1937hobit",
    ]
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 1
    assert "duplicate" in result.output.lower()


def test_edit_file(runner, database, example_pdf, tmpdir):
    args = [
        "--database",
        database,
        "edit",
        "asimov1951foundation",
        "--file",
        example_pdf,
    ]
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert result.output.startswith("Copying ")

    with open(database) as f:
        assert "asimov1951foundation.pdf" in f.read()

    expected_pdf = str(tmpdir / "example.pdf")
    assert os.path.isfile(expected_pdf)
    assert filecmp.cmp(example_pdf, expected_pdf)


def test_edit_field_with_value(runner, database):
    args = ["--database", database, "edit", "asimov1951foundation", "title=I, robot"]
    result = runner.invoke(bibo.cli, args)

    with open(database) as f:
        assert "title = {I, robot}" in f.read()


def test_edit_field_no_value(runner, database):
    args = ["--database", database, "edit", "asimov1951foundation", "title"]
    with mock.patch("click.edit") as edit_mock:
        edit_mock.return_value = "THE HOBBIT!"
        result = runner.invoke(bibo.cli, args)

    with open(database) as f:
        assert "title = {THE HOBBIT!}" in f.read()


def test_edit_field_without_saving(runner, database):
    args = ["--database", database, "edit", "asimov1951foundation", "title"]
    with mock.patch("click.edit") as edit_mock:
        edit_mock.return_value = None
        result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 1
    assert "editor exited" in result.output.lower()


def test_edit_multiple_fields(runner, database):
    args = [
        "--database",
        database,
        "edit",
        "asimov1951foundation",
        "title=I, robot",
        "year=1950",
    ]
    result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0

    with open(database) as f:
        data = pybibs.read_string(f.read())
        entry = bibo.query.get(data, "asimov").entry
        assert entry["fields"]["title"] == "I, robot"
        assert entry["fields"]["year"] == "1950"


def test_add_to_empty_database(runner, tmpdir):
    database = str(tmpdir / "new.bib")
    with mock.patch("click.edit") as edit_mock:
        edit_mock.return_value = TO_ADD
        args = ["--database", database, "add"]
        result = runner.invoke(bibo.cli, args)
    assert result.exit_code == 0
    assert result.output == ""

    with open(database) as f:
        assert "The emotional dog" in f.read()


@mock.patch("subprocess.Popen")
def test_list_missing_bibtex(popen_mock, runner, database):
    popen_mock.side_effect = OSError()
    result = runner.invoke(bibo.cli, ["--database", database, "list"])
    assert result.exit_code == 0
    assert "Using a fallback citation" in result.output
    assert "verbose" not in result.output


@mock.patch("subprocess.Popen")
def test_list_failing_bibtex(popen_mock, runner, database):
    p = mock.Mock()
    p.wait.return_value = 1
    popen_mock.return_value = p
    result = runner.invoke(bibo.cli, ["--database", database, "list"])
    assert result.exit_code == 0
    assert "Using a fallback citation" in result.output
    assert "verbose" in result.output


def test_add_duplicate_key(runner, database):
    # Use pybibs to get the first entry in the DB to re-add
    args = ["--database", database, "list", "--raw"]
    result = runner.invoke(bibo.cli, args)
    data = pybibs.read_string(result.output)
    to_add = pybibs.write_string([data[0]])

    with mock.patch("click.edit") as edit_mock:
        edit_mock.return_value = to_add
        result = runner.invoke(bibo.cli, ["--database", database, "add"])
    assert result.exit_code == 1
    assert "duplicate" in result.output.lower()


def test_bibtex_error_with_relative_path(runner):
    """Issue #32."""
    # This is the same DB as usual, but using relative path
    database = os.path.join("tests", "bibo", "test.bib")
    result = runner.invoke(bibo.cli, ["--database", database, "list"])
    assert "bibtex failed" not in result.output


def test_remove_one_entry_at_a_time(runner, database):
    result = runner.invoke(bibo.cli, ["--database", database, "remove"])
    assert result.exit_code != 0
    result = runner.invoke(bibo.cli, ["--database", database, "remove", "tolkien"])
    assert result.exit_code != 0
    result = runner.invoke(
        bibo.cli, ["--database", database, "remove", "tolkien1937hobit"]
    )
    assert result.exit_code == 0
