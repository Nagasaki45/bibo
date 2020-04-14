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
    d: typing.Dict[str, typing.Any] = {}

    # For cases where the entire search term is a key (e.g. best:author)
    matches = re.findall(search_term, entry["key"], re.IGNORECASE)
    if matches:
        d.setdefault("key", set()).update(matches)

    search_field, search_value = _parse_search_term(search_term)

    for part in ["key", "type"]:
        if search_field and search_field != part:
            continue
        matches = re.findall(search_value, entry[part], re.IGNORECASE)
        if matches:
            d.setdefault(part, set()).update(matches)
    for field, value in entry.get("fields", {}).items():
        if search_field and search_field != field:
            continue
        matches = re.findall(search_value, value, re.IGNORECASE)
        if matches:
            d.setdefault("fields", {}).setdefault(field, set()).update(matches)
    return d


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


def _parse_search_term(search_term):
    parts = search_term.split(":")
    if len(parts) == 1:
        return None, parts[0].lower()
    if len(parts) == 2:
        return parts[0].lower(), parts[1].lower()
    raise click.ClickException("Invalid search term")


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
