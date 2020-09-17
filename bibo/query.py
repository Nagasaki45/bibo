import collections
import collections.abc
import itertools
import re
import typing

import click

from . import internals, models


def search(data, search_terms: typing.Iterable[str]):
    if isinstance(search_terms, str):
        search_terms = [search_terms]
    search_terms = iter(search_terms)
    results = (models.SearchResult(e, {}) for e in internals.bib_entries(data))
    return _recursive_search(results, search_terms)


def _recursive_search(results, search_terms):
    try:
        search_term = next(search_terms)
        # Calculate match with search term and update results
        results = (_update_result(r, _match(r.entry, search_term)) for r in results)
        # Drop Nones with empty match
        results = (r for r in results if r)
        return _recursive_search(results, search_terms)
    except StopIteration:
        return results


def _match(entry, search_term: str):
    """
    Return a similar structure to an entry (nested dict) with matching strings
    as values.
    """
    # The match to populate
    d: typing.Dict[str, typing.Any] = {}

    # For cases where the entire search term is a key (e.g. best:author)
    _match_field("key", entry["key"], search_term, lambda: d)

    search_field, search_value = _parse_search_term(search_term)

    if search_field in ["key", "type"]:
        _match_field(search_field, entry[search_field], search_value, lambda: d)
    elif search_field in entry["fields"]:
        if search_value:
            _match_field(
                search_field,
                entry["fields"][search_field],
                search_value,
                lambda: d.setdefault("fields", {}),
            )
        # Allow query by field with no value (e.g. bibo list readdate:)
        else:
            d.setdefault("fields", {}).setdefault(search_field, set())
    elif search_field is None:
        for part in ["key", "type"]:
            _match_field(part, entry[part], search_value, lambda: d)
        for field, value in entry.get("fields", {}).items():
            _match_field(field, value, search_value, lambda: d.setdefault("fields", {}))
    return d


def _match_field(
    field: str,
    value: str,
    search_value: str,
    get_dict: typing.Callable[[], dict],
) -> None:
    """
    Try to match a field/value to a search_value. If there are
    matches, `get_dict` is called to get the dictionary to put the results
    in, usually the `match`, or `match["fields"]`.
    """
    matches = set(re.findall(search_value, value, re.IGNORECASE))
    matches.discard("")
    if matches:
        get_dict().setdefault(field, set()).update(matches)


def _update_result(result, new_match):
    if not new_match:
        return None
    d = _nested_update(result.match, new_match)
    return models.SearchResult(result.entry, d)


def _nested_update(d, u):
    _d = d.copy()
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            _d[k] = _nested_update(d.get(k, {}), v)
        else:
            _d[k] = _d.get(k, set())
            _d[k].update(v)
    return _d


def _parse_search_term(search_term: str):
    parts = search_term.split(":")
    if len(parts) == 1:
        return None, parts[0].lower()
    if len(parts) == 2:
        return parts[0].lower(), parts[1].lower()
    return "key", search_term.lower()


def get(data, search_terms):
    results = list(search(data, search_terms))

    for result in results:
        if result.entry["key"].lower() == search_terms[0].lower():
            return result

    if len(results) == 0:
        raise click.ClickException("No entries found")
    if len(results) > 1:
        raise click.ClickException("Multiple entries found")

    return results[0]


def get_by_key(data, key):
    for entry in internals.bib_entries(data):
        if entry["key"] == key:
            return entry
    raise click.ClickException('Couldn\'t find"{}"'.format(key))
