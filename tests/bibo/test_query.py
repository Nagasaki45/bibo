import click
import pytest  # type: ignore

from bibo import models, query
import pybibs


def test_search_a_key_with_colon():
    data = pybibs.read_string(
        """
        @article{Gurion:2019,
        }
        """
    )
    results = list(query.search(data, ["Gurion:"]))
    assert len(results) == 1


def test_search_single_term():
    data = pybibs.read_string(
        """
        @book{tolkien1937hobit,
            year = {1937},
            title = {The Hobbit},
            author = {Tolkien, John R. R.},
        }

        @book{asimov1951foundation,
            year = {1951},
            title = {Foundation},
            author = {Asimov, Izaac}
        }
        """
    )
    results = list(query.search(data, ["asimov"]))
    assert len(results) == 1
    assert results[0].entry["fields"]["title"] == "Foundation"


def test_search_multiple_search_terms():
    data = pybibs.read_string(
        """
        @book{tolkien1937hobit,
            year = {1937},
            title = {The Hobbit},
            author = {Tolkien, John R. R.},
        }

        @trilogy{tolkien1954lord,
            title={The Lord of the Rings},
            author={Tolkien, John Ronald Reuel},
            year={1954},
        }
        """
    )
    results = list(query.search(data, ["tolkien", "hobbit"]))
    assert len(results) == 1
    assert results[0].entry["fields"]["title"] == "The Hobbit"


def test_search_specific_field():
    data = pybibs.read_string(
        """
        @book{tolkien1937hobit,
            year = {1937},
            title = {The Hobbit},
            author = {Tolkien, John R. R.},
        }

        @trilogy{tolkien1954lord,
            title={The Lord of the Rings},
            author={Tolkien, John Ronald Reuel},
            year={1954},
            publisher={Best books since 1937},
        }
        """
    )
    results = list(query.search(data, ["year:1937"]))
    assert len(results) == 1
    assert results[0].entry["fields"]["title"] == "The Hobbit"


def test_search_specific_field_with_capital_letter():
    """Issue #27"""
    data = pybibs.read_string(
        """
        @book{asimov1951foundation,
            year = {1951},
            title = {Foundation},
            author = {Asimov, Izaac}
        }
        """
    )
    results = list(query.search(data, ["author:asimov"]))
    assert len(results) == 1
    assert results[0].entry["fields"]["title"] == "Foundation"


def test_search_multiple_terms_are_anded():
    data = pybibs.read_string(
        """
        @book{tolkien1937hobit,
            year = {1937},
            title = {The Hobbit},
            author = {Tolkien, John R. R.},
        }

        @trilogy{tolkien1954lord,
            title={The Lord of the Rings},
            author={Tolkien, John Ronald Reuel},
            year={1954},
        }

        @book{asimov1951foundation,
            year = {1951},
            title = {Foundation},
            author = {Asimov, Izaac}
        }
        """
    )
    results = list(query.search(data, ["tolkien", "type:book"]))
    assert len(results) == 1
    assert results[0].entry["fields"]["title"] == "The Hobbit"


def test_search_with_capitalized_search_term():
    """Issue #28"""
    data = pybibs.read_string(
        """
        @book{asimov1951foundation,
            year = {1951},
            title = {Foundation},
            author = {Asimov, Izaac}
        }
        """
    )
    results = list(query.search(data, ["ASIMOV"]))
    assert len(results) == 1
    assert results[0].entry["fields"]["title"] == "Foundation"


def test_search_or_get_key_with_many_colons():
    """Issue #66"""
    data = pybibs.read_string(
        """
        @article{key:with:many:colons,
            title = {Key with many colons},
        }

        @book{tolkien1937hobit,
            year = {1937},
            title = {The Hobbit},
            author = {Tolkien, John R. R.},
        }
        """
    )
    results = list(query.search(data, "key:with:many:colons"))
    assert len(results) == 1

    search_result = query.get(data, "key:with:many:colons")
    assert search_result.entry["fields"]["title"] == "Key with many colons"


def test_open_multiple_entries_one_exact_match():
    data = pybibs.read_string(
        """
        @article{abc,
            title = {Partial key of abcd},
        }

        @article{abcd,
            title = {A key that contains a shorter key},
        }
        """
    )
    with pytest.raises(click.ClickException):
        query.get(data, ["ab"])
    query.get(data, ["abc"])


def test_search_match_details():
    data = pybibs.read_string(
        """
        @book{tolkien1937hobit,
            year = {1937},
            title = {The Hobbit},
            author = {Tolkien, John R. R.},
        }
        """
    )
    results = list(query.search(data, ["tolkien", "hobbit"]))
    assert "tolkien" in results[0].match["key"]
    assert ("author", set(["Tolkien"])) in results[0].match["fields"].items()
    assert ("title", set(["Hobbit"])) in results[0].match["fields"].items()


def test_match():
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
    assert query._match(entry, "Tolkien") == {
        "key": {"tolkien"},
        "fields": {"author": set(["Tolkien"])},
    }
    assert query._match(entry, "article") == {}
    assert query._match(entry, "book") == {"type": set(["book"])}
    assert query._match(entry, "hobbit") == {"fields": {"title": set(["Hobbit"])}}
    assert query._match(entry, "year:193") == {"fields": {"year": set(["193"])}}
    assert query._match(entry, "year:1937") == {"fields": {"year": set(["1937"])}}

    # Issue 68: A match with field only, no key should return empty set,
    # not a set with empty string. It breaks the highlighting
    assert query._match(entry, "year:") == {"fields": {"year": set()}}


def test_update_result():
    entry = {
        "a": "1234",
        "props": {"b": "ABCD"},
    }
    r1 = models.SearchResult(entry, {})
    assert query._update_result(r1, {}) == None

    r2 = query._update_result(r1, {"a": set(["1"])})
    assert "a" in r2.match
    assert r2.match["a"] == set(["1"])

    r3 = query._update_result(r2, {"props": {"b": set(["ABC"])}})
    assert r3.match["props"]["b"] == set(["ABC"])

    r4 = query._update_result(r3, {"props": {"b": set(["D"])}})
    assert r4.match["props"]["b"] == {"ABC", "D"}


def test_nested_update():
    d = {"x": {"y": set("z")}}
    u = {"x": {"y": set("t")}}
    assert query._nested_update(d, u) == {"x": {"y": {"z", "t"}}}

    d = {}
    u = {"x": set("X")}
    assert query._nested_update(d, u) == {"x": set("X")}
