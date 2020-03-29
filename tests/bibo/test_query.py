import click
import pytest

from bibo import query


def test_search_a_key_with_colon(data):
    results = list(query.search(data, ["Gurion:"]))
    assert len(results) == 1


def test_search_single_term(data):
    results = list(query.search(data, ["asimov"]))
    assert len(results) == 1
    assert results[0]["fields"]["title"] == "Foundation"


def test_search_multiple_search_terms(data):
    results = list(query.search(data, ["tolkien", "hobbit"]))
    assert len(results) == 1
    assert results[0]["fields"]["title"] == "The Hobbit"


def test_search_specific_field(data):
    results = list(query.search(data, ["year:1937"]))
    assert len(results) == 1
    assert results[0]["fields"]["title"] == "The Hobbit"


def test_search_specific_field_with_capital_letter(data):
    """Issue #27"""
    results = list(query.search(data, ["author:asimov"]))
    assert len(results) == 1
    assert results[0]["fields"]["title"] == "Foundation"


def test_search_multiple_terms_are_anded(data):
    results = list(query.search(data, ["tolkien", "type:book"]))
    assert len(results) == 1
    assert results[0]["fields"]["title"] == "The Hobbit"


def test_search_invalid_search_term(data):
    with pytest.raises(Exception, match="Invalid search term") as e:
        list(query.search(data, "a:b:c"))


def test_search_with_capitalized_search_term(data):
    """Issue #28"""
    results = list(query.search(data, ["ASIMOV"]))
    assert len(results) == 1
    assert results[0]["fields"]["title"] == "Foundation"


def test_open_multiple_entries_one_exact_match(data):
    with pytest.raises(click.ClickException):
        query.get(data, ["ab"])
    query.get(data, ["abc"])
