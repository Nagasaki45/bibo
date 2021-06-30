import os

import click
import pytest  # type: ignore

from bibo import internals, models
import pybibs


def test_destination_heuristic(tmpdir):
    data = pybibs.read_string(
        """
        @article{a,
            file = {~/some/path/a.pdf},
        }

        @article{b,
            file = {~/some/path/b.pdf},
        }
        """
    )
    assert internals.destination_heuristic(data) == "~/some/path"


def test_destination_heuristic_empty():
    data = pybibs.read_string(
        """
        @article{a,
        }
        """
    )
    with pytest.raises(click.ClickException, match=".*no paths in the database") as e:
        internals.destination_heuristic(data)


def test_destination_heuristic_multiple_equaly_valid_paths():
    data = pybibs.read_string(
        """
        @article{a,
            file = {~/some/path/a.pdf},
        }

        @article{b,
            file = {~/other/path/b.pdf},
        }
        """
    )
    with pytest.raises(
        click.ClickException,
        match=".*there are multiple equally valid paths in the database",
    ) as e:
        print(internals.destination_heuristic(data))


def test_set_file_with_destination(example_pdf, tmpdir):
    data = pybibs.read_string(
        """
        @book{tolkien1937hobit,
            year = {1937},
            title = {The Hobbit},
            author = {Tolkien, John R. R.},
        }
        """
    )
    entry = data[0]
    destination = tmpdir / "somewhere_else"
    os.mkdir(str(destination))
    internals.set_file(data, entry, example_pdf, str(destination))
    assert os.path.exists(str(destination / entry["key"] + ".pdf"))


def test_set_file_exists_already(tmpdir):
    data = pybibs.read_string(
        """
        @book{key,
            title=title,
        }
        """
    )
    entry = data[0]
    existing_file = tmpdir / "key.txt"
    existing_file.write("content")
    with pytest.raises(click.ClickException, match=".* already exists"):
        internals.set_file(data, entry, existing_file.strpath, tmpdir)


def test_format_entry():
    data = pybibs.read_string(
        """
        @book{tolkien1937hobit,
            year = {1937},
            title = {The Hobbit},
            author = {Tolkien, John R. R.},
        }
        """
    )
    entry = data[0]
    assert internals.format_entry(entry, "$year") == "1937"
    assert internals.format_entry(entry, "$year: $title") == "1937: The Hobbit"


def test_highlight_text():
    s1 = "hello world"
    s2 = "hello {}orld".format(internals.bold("w"))
    assert internals.highlight_text(s1, "w") == s2

    s3 = "hell{}orld".format(internals.bold("o w"))
    assert internals.highlight_text(s2, "o ") == s3


def test_highlight_text_with_color():
    s1 = "hello world"
    s2 = "hello {}orld".format(internals.bold("w"))
    f = lambda s: click.style(s, fg="green")
    assert internals.highlight_text(f(s1), "w") == f(s2)


def test_highlight_match():
    text = "my name is Moshe, 40"
    entry = {
        "name": "Moshe",
        "fields": {
            "age": "40",
            "address": "London, UK",
        },
    }
    match = {
        "name": ["Mosh"],
        "fields": {
            "address": ["London"],
        },
    }
    result = models.SearchResult(entry, match)

    text, extra_match_info = internals.highlight_match(text, result)
    assert text == "my name is {}e, 40".format(internals.bold("Mosh"))
    assert extra_match_info == {"address": "{}, UK".format(internals.bold("London"))}


def test_highlight_match_case_insensitive():
    # Testing issue #69
    text = "Turn-taking"
    entry = {"fields": {"title": "Turn-Taking"}}
    match = {"fields": {"title": set(["Turn-Taking"])}}
    result = models.SearchResult(entry, match)

    text, extra_match_info = internals.highlight_match(text, result)
    assert text == internals.bold("Turn-taking")
    assert extra_match_info == {}


def test_highlight_text_escapes_ansi():
    # Testing issue #78
    text = click.style("Green text", fg="green")
    assert "3" in text  # because it's part of the ANSI code for green
    assert internals.highlight_text(text, "3") == text

    assert "m" in text  # because it's part of the ANSI code for green
    assert internals.highlight_text(text, "m") == text
