"""
Command line reference manager with a single source of truth: the .bib file.
Inspired by beets.
"""

import pkg_resources
import sys

import click
import click_plugins
import pybibs
import pyperclip

from . import internals
from . import query

PATH_OPTION = click.Path(writable=True, readable=True, dir_okay=False)
FILE_OPTION = click.option(
    '--file',
    help='File to link to this entry.',
    type=click.Path(exists=True, readable=True, dir_okay=False),
)
DESTINATION_OPTION = click.option(
    '--destination',
    help='A folder to put the file in.',
    type=click.Path(exists=True, readable=True, dir_okay=True, file_okay=False),
)
SEARCH_TERMS_OPTION = click.argument('search_terms', nargs=-1)


@click_plugins.with_plugins(pkg_resources.iter_entry_points('bibo.plugins'))
@click.group(help=__doc__)
@click.option('--database', envvar='BIBO_DATABASE', help='A .bib file.',
              required=True, type=PATH_OPTION)
@click.pass_context
def cli(ctx, database):
    ctx.ensure_object(dict)
    ctx.obj['database'] = database

    # Read the database. Create (in memory) if doesn't exist
    try:
        ctx.obj['data'] = pybibs.read_file(database)
    except FileNotFoundError:
        ctx.obj['data'] = []


@cli.command(short_help='List entries.')
@click.option('--raw', is_flag=True, help='Format as raw .bib entries')
@SEARCH_TERMS_OPTION
@click.pass_context
def list(ctx, search_terms, raw):
    for entry in query.search(ctx.obj['data'], search_terms):
        if raw:
            txt = pybibs.write_string([entry])
        else:
            txt = internals.format_entry(entry)
        click.echo(txt)


@cli.command(short_help='Open the file linked to an entry.')
@SEARCH_TERMS_OPTION
@click.pass_context
def open(ctx, search_terms):
    entry = query.get(ctx.obj['data'], search_terms)

    file_field = entry['fields'].get('file')
    if not file_field:
        click.echo('No file is associated with this entry')
        sys.exit(1)

    internals.open_file(file_field)


@cli.command(short_help='Add a new entry.')
@FILE_OPTION
@DESTINATION_OPTION
@click.pass_context
def add(ctx, destination, **kwargs):
    file_ = kwargs.pop('file')
    file_validation(file_, destination)

    data = ctx.obj['data']
    bib = click.edit(text=pyperclip.paste())
    entry = pybibs.read_entry_string(bib)
    data.append(entry)

    if file_:
        internals.set_file(data, entry, file_)

    pybibs.write_file(data, ctx.obj['database'])


@cli.command(short_help='Remove an entry or a field.')
@SEARCH_TERMS_OPTION
@click.option('--field', help='Field to remove.')
@click.pass_context
def remove(ctx, search_terms, field):
    data = ctx.obj['data']

    entries = [e for e in query.search(data, search_terms)]

    for entry in entries:
        if field is None:
            internals.remove_entry(data, entry)
        else:
            if field in entry['fields']:
                del entry['fields'][field]
            else:
                click.echo('No such field')

    pybibs.write_file(data, ctx.obj['database'])


@cli.command(short_help='Edit an entry.')
@SEARCH_TERMS_OPTION
@click.option('--type', help='Set the type.')
@click.option('--key', help='Set the key.')
@FILE_OPTION
@DESTINATION_OPTION
@click.option('--field', help='Field to edit.')
@click.pass_context
def edit(ctx, search_terms, key, field, destination, **kwargs):
    type_ = kwargs.pop('type')
    file_ = kwargs.pop('file')
    file_validation(file_, destination)

    data = ctx.obj['data']
    entry = query.get(data, search_terms)

    if type_:
        entry['type'] = type_
    if key:
        entry['key'] = key
    if file_:
        internals.set_file(data, entry, file_)
    if field:
        current_value = entry['fields'].get(field, '')
        updated_value = click.edit(text=current_value).strip()
        entry['fields'][field] = updated_value

    pybibs.write_file(data, ctx.obj['database'])


def file_validation(file_, destination):
    if destination and not file_:
        raise click.BadOptionUsage(
            'destination',
            'Specifying destination without a file is meaningless.',
        )

if __name__ == '__main__':
    cli()
