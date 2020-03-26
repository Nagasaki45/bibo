"""
Command line reference manager with a single source of truth: the .bib file.
Inspired by beets.
"""

import os
import pkg_resources
import sys

import click
import click_constraints
import click_plugins
import pybibs
import pyperclip
import requests

from . import cite
from . import internals
from . import query

PATH_OPTION = click.Path(writable=True, readable=True, dir_okay=False)
FILE_OPTIONS = internals.combine_decorators([
    click.option(
        '--file',
        help='File to link to this entry.',
        type=click.Path(exists=True, readable=True, dir_okay=False),
    ),
    click.option(
        '--destination',
        help='A folder to put the file in.',
        type=click.Path(exists=True, readable=True, dir_okay=True, file_okay=False),
    ),
    click.option(
        '--no-copy',
        help='Add the specified file in its current location without copying.',
        is_flag=True,
    ),
    click_constraints.constrain(
        'destination',
        depends=['file']
    ),
    click_constraints.constrain(
        'no_copy',
        depends=['file'],
        conflicts=['destination'],
    ),
])
SEARCH_TERMS_OPTION = click.argument(
    'search_terms',
    nargs=-1,
    autocompletion=internals.complete_key,
)


@click_plugins.with_plugins(pkg_resources.iter_entry_points('bibo.plugins'))
@click.group(help=__doc__)
@click.version_option()
@click.option('--database', envvar=internals.BIBO_DATABASE_ENV_VAR,
              help='A .bib file.', required=True, type=PATH_OPTION)
@click.pass_context
def cli(ctx, database):
    ctx.ensure_object(dict)
    ctx.obj['database'] = os.path.abspath(database)
    ctx.obj['data'] = internals.load_database(database)


@cli.command('list', short_help='List entries.')
@click.option('--raw', is_flag=True, help='Format as raw .bib entries')
@click.option('--bibstyle', default='plain', help='Citation format')
@click.option('--verbose', is_flag=True, help='Print verbose information')
@click.option('--format', help='Format pattern')
@SEARCH_TERMS_OPTION
@click.pass_context
def list_(ctx, search_terms, raw, bibstyle, verbose, **kwargs):
    format_pattern = kwargs.pop('format')
    assert not kwargs

    entries = query.search(ctx.obj['data'], search_terms)
    if raw:
        _list_raw(entries)
    elif format_pattern:
        _list_format_pattern(entries, format_pattern)
    else:
        _list_citations(entries, ctx.obj['database'], bibstyle, verbose)


def _list_raw(entries):
    for entry in entries:
        click.echo(pybibs.write_string([entry]))


def _list_format_pattern(entries, format_pattern):
    for entry in entries:
        click.echo(internals.format_entry(entry, format_pattern))


def _list_citations(entries, database, bibstyle, verbose):
    entries = [e for e in entries if e['type'] != 'string']
    keys = [e['key'] for e in entries]
    exception = None
    try:
        citations = cite.cite(keys, database, bibstyle, verbose)
    except cite.BibtexException as e:
        exception = e

    for entry in entries:
        parts = [
            internals.header(entry),
            cite.fallback(entry) if exception else citations[entry['key']],
        ]
        click.echo('\n'.join(parts))

    if exception is not None:
        parts = [str(exception), 'Using a fallback citation method']
        if exception.use_verbose:
            parts.append('Use --verbose for more information')
        click.secho('. '.join(parts), fg='red')


@cli.command('open', short_help='Open the file / url / doi associated with an entry.')
@SEARCH_TERMS_OPTION
@click.pass_context
def open_(ctx, search_terms):
    entry = query.get(ctx.obj['data'], search_terms)

    for field_name in ['file', 'url', 'doi']:
        value = entry.get('fields', {}).get(field_name)
        if value:
            if field_name == 'doi':
                value = 'https://doi.org/' + value
            click.launch(value)
            break
    else:
        raise click.ClickException('No file / url / doi is associated with this entry')


@cli.command(short_help='Add a new entry.')
@FILE_OPTIONS
@click.option('--doi', help='Add entry by DOI.')
@click.pass_context
def add(ctx, destination, doi, no_copy, **kwargs):
    file_ = kwargs.pop('file')

    data = ctx.obj['data']
    if doi is not None:
        url = 'http://dx.doi.org/{}'.format(doi)
        headers = {'Accept': 'application/x-bibtex'}
        resp = requests.get(url, headers=headers)
        assert resp.status_code == 200
        raw_bib = resp.text
    else:
        raw_bib = pyperclip.paste()
    bib = internals.editor(text=raw_bib)
    entry = pybibs.read_entry_string(bib)

    internals.unique_key_validation(entry['key'], data)

    data.append(entry)

    if file_:
        internals.set_file(data, entry, file_, destination, no_copy)

    pybibs.write_file(data, ctx.obj['database'])


@cli.command(short_help='Remove an entry or a field.')
@click.argument('key', autocompletion=internals.complete_key)
@click.argument('field', nargs=-1)
@click.pass_context
def remove(ctx, key, field):
    data = ctx.obj['data']
    entry = query.get_by_key(data, key)

    if not field:
        data.remove(entry)
    elif 'fields' in entry:
        for f in field:
            if f in entry['fields']:
                del entry['fields'][f]
            else:
                click.echo('"{}" has no field "{}"'.format(key, f))
    else:
        click.echo('"{}" has no fields'.format(key))

    pybibs.write_file(data, ctx.obj['database'])


@cli.command(short_help='Edit an entry.')
@click.argument('key', autocompletion=internals.complete_key)
@click.argument('field_value', nargs=-1)
@FILE_OPTIONS
@click.pass_context
def edit(ctx, key, field_value, destination, no_copy, **kwargs):
    '''
    FIELD_VALUE

    To set fields: author=Einstein tags=interesting.
    Leave the value empty to open in editor.
    Set the key / type in the same way.
    '''
    file_ = kwargs.pop('file')

    data = ctx.obj['data']
    entry = query.get_by_key(data, key)

    if file_:
        internals.set_file(data, entry, file_, destination, no_copy)
    for fv in field_value:
        if '=' in fv:
            field, value = fv.split('=')
        else:
            field = fv
            current_value = entry['fields'].get(field, '')
            value = internals.editor(text=current_value).strip()
        if field == 'key':
            internals.unique_key_validation(value, data)
            entry['key'] = value
        elif field == 'type':
            entry['type'] = value
        else:
            entry['fields'][field] = value

    pybibs.write_file(data, ctx.obj['database'])


if __name__ == '__main__':
    cli()
