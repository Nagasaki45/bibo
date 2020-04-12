import os

import click
import pytest  # type: ignore

from bibo import internals, models


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


def test_match_case():
    assert internals.match_case("hello", "Hello World") == "Hello"
    assert internals.match_case("WORLD", "Hello World") == "World"
    with pytest.raises(ValueError):
        internals.match_case("bibo", "Hello World")


def test_highlight_text():
    s1 = "hello world"
    s2 = "hello {}w{}orld".format(internals._ansi_bold, internals._ansi_unbold)
    assert internals.highlight_text(s1, "w") == s2

    s3 = "hell{}o w{}orld".format(internals._ansi_bold, internals._ansi_unbold)
    assert internals.highlight_text(s2, "o ") == s3


def test_highlight_text_with_color():
    s1 = "hello world"
    s2 = "hello {}w{}orld".format(internals._ansi_bold, internals._ansi_unbold)
    f = lambda s: click.style(s, fg="green")
    assert internals.highlight_text(f(s1), "w") == f(s2)


def test_highlight_match():
    text = "my name is Moshe, 40"
    entry = {"name": "Moshe", "fields": {"age": "40", "address": "London, UK",}}
    match = {"name": ["Mosh"], "fields": {"address": ["London"],}}
    result = models.SearchResult(entry, match)

    text, extra_match_info = internals.highlight_match(text, result)
    assert text == "my name is {}Mosh{}e, 40".format(
        internals._ansi_bold, internals._ansi_unbold
    )
    assert extra_match_info == {
        "address": "{}London{}, UK".format(
            internals._ansi_bold, internals._ansi_unbold
        ),
    }
