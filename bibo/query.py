import itertools
import re

import click


def search(data, search_terms):
    if isinstance(search_terms, str):
        search_terms = [search_terms]
    search_terms = iter(search_terms)
    return _recursive_search(data, search_terms)


def _recursive_search(data, search_terms):
    try:
        search_term = next(search_terms)
        return _recursive_search(
            (e for e in data if _is_matching(e, search_term)),
            search_terms,
        )
    except StopIteration:
        return data


def _is_matching(entry, search_term):
    search_field, search_value = _parse_search_term(search_term)
    if search_field == 'general':
        return _is_matching_general_field(entry, search_value)
    else:
        return _is_matching_specific_field(entry, search_field, search_value)


def _is_matching_general_field(entry, search_value):
    searchables = itertools.chain(
        entry.get('fields', {}).values(),
        (entry[x] for x in ['key', 'type']),
    )

    for searchable in searchables:
        if search_value in searchable.lower():
            return True
    return False


def _is_matching_specific_field(entry, search_field, search_value):
    if search_field == 'key':
        return search_value in entry['key'].lower()
    if search_field == 'type':
        return search_value in entry['type'].lower()
    for field, value in entry.get('fields', {}).items():
        if search_field == field.lower():
            return search_value in value.lower()
    return False


def _parse_search_term(search_term):
    # Split unless preceded by '\'
    parts = re.split(r'(?<!\\):', search_term)
    if len(parts) == 1:
        return 'general', parts[0].lower().replace('\\:', ':')
    if len(parts) == 2:
        return parts[0].lower(), parts[1].lower().replace('\\:', ':')
    raise click.ClickException('Invalid search term')


def get(data, search_terms):
    search_results = search(data, search_terms)

    try:
        entry = next(search_results)
    except StopIteration:
        raise click.ClickException('No entries found')

    try:
        next(search_results)
    except StopIteration:
        pass
    else:
        raise click.ClickException('Multiple entries found')

    return entry


def get_by_key(data, key):
    for entry in data:
        if entry['key'] == key:
            return entry
    raise click.ClickException('Couldn\'t find"{}"'.format(key))
