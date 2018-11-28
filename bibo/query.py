import itertools

import click


def search(data, search_term):
    for entry in data:

        searchables = itertools.chain(
            entry['fields'].values(),
            (entry[x] for x in ['key', 'type']),
        )

        for searchable in searchables:
            if search_term.lower() in searchable.lower():
                yield entry
                break


def get(data, search_term):
    search_results = search(data, search_term)

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
