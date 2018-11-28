import pytest

from bibo import query


def test_search_single_term(data):
    results = list(query.search(data, ['asimov']))
    assert len(results) == 1
    assert results[0]['fields']['title'] == 'Foundation'


def test_search_multiple_search_terms(data):
    results = list(query.search(data, ['tolkien', 'hobbit']))
    assert len(results) == 1
    assert results[0]['fields']['title'] == 'The Hobbit'


def test_search_specific_field(data):
    results = list(query.search(data, ['year:1937']))
    assert len(results) == 1
    assert results[0]['fields']['title'] == 'The Hobbit'


def test_search_invalid_search_term(data):
    with pytest.raises(Exception) as e:
        list(query.search(data, 'a:b:c'))
    assert 'Invalid search term' in str(e)
