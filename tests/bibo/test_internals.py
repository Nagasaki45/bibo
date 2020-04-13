import os

import click
import pytest  # type: ignore

from bibo import internals


def test_destination_heuristic(data, tmpdir):
    assert internals.destination_heuristic(data) == tmpdir


def test_destination_heuristic_empty(data):
    for entry in data:
        if "file" in entry.get("fields", []):
            del entry["fields"]["file"]
    with pytest.raises(click.ClickException, match=".*no paths in the database") as e:
        internals.destination_heuristic(data)


def test_destination_heuristic_multiple_equaly_valid_paths(data):
    for i, entry in enumerate(data):
        if "fields" in entry:
            entry["fields"]["file"] = "/fake/path{}/file".format(i)
    with pytest.raises(
        click.ClickException,
        match=".*there are multiple equally valid paths in the database",
    ) as e:
        internals.destination_heuristic(data)


def test_set_file_with_destination(data, example_pdf, tmpdir):
    entry = data[0]
    destination = tmpdir / "somewhere_else"
    os.mkdir(str(destination))
    internals.set_file(data, entry, example_pdf, str(destination))
    assert os.path.exists(str(destination / entry["key"] + ".pdf"))


def test_get_database():
    args = ["whatever", "--database", "test.bib", "whatever"]
    assert internals.get_database(args) == "test.bib"


def test_format_entry(data):
    entry = data[0]
    assert internals.format_entry(entry, "$year") == "1937"
    assert internals.format_entry(entry, "$year: $title") == "1937: The Hobbit"


def test_complete_path(tmpdir):
    # Create dummy files and a sub-dir with file
    ps = []
    for i in range(10):
        name = "even" if i % 2 else "odd"
        p = tmpdir / "journal{}_{}.txt".format(name, i)
        p.write(i)
        ps.append(p)
    n_top_level_journals = len(ps)
    subp = tmpdir.mkdir("subdir").join("subjournal.txt")
    subp.write("findme")
    assert len(tmpdir.listdir()) == 1 + n_top_level_journals

    incomplete = lambda paths: os.path.join(tmpdir.strpath, *paths)

    # Check all matches incl subdir
    matches = internals.complete_path(None, None, incomplete([""]))
    assert len(matches) == 1 + n_top_level_journals
    # Check match pattern
    ms_even = internals.complete_path(None, None, incomplete(["journaleven"]))
    assert len(ms_even) == n_top_level_journals // 2
    # Check subdir match
    ms_subdir = internals.complete_path(None, None, incomplete(["subdir", ""]))
    assert len(ms_subdir) == 1
    # Check for completion help string as basename
    assert ms_subdir[0] == (subp.strpath, subp.basename)
