"""
Command line reference manager with a single source of truth: the .bib file.
Inspired by beets.
"""

import collections
import datetime
import os
import pkg_resources
import re
import shutil
import subprocess
import sys

import click
import click_plugins
import pybibs
import pyperclip

from . import query

PATH_OPTION = click.Path(exists=True, writable=True, readable=True,
                         dir_okay=False)
PDF_OPTION = click.option(
    '--pdf',
    help='PDF to link to this entry.',
    type=click.Path(exists=True, readable=True, dir_okay=False),
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
    ctx.obj['data'] = pybibs.read_file(database)


@cli.command(short_help='List entries.')
@click.option('--raw', is_flag=True, help='Format as raw .bib entries')
@SEARCH_TERMS_OPTION
@click.pass_context
def list(ctx, search_terms, raw):
    for entry in query.search(ctx.obj['data'], search_terms):
        if raw:
            txt = pybibs.write_string([entry])
        else:
            txt = format_entry(entry)
        click.echo(txt)


@cli.command(short_help='Open the PDF linked to an entry.')
@SEARCH_TERMS_OPTION
@click.pass_context
def open(ctx, search_terms):
    entry = query.get(ctx.obj['data'], search_terms)

    file_field = entry['fields'].get('file')
    if not file_field:
        click.echo('No file is associated with this entry')
        sys.exit(1)

    open_file(file_field)


@cli.command(short_help='Add a new entry.')
@PDF_OPTION
@click.pass_context
def add(ctx, pdf):
    data = ctx.obj['data']
    bib = click.edit(text=pyperclip.paste())
    entry = pybibs.read_entry_string(bib)
    data.append(entry)

    if pdf:
        set_pdf(data, entry, pdf)

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
            remove_entry(data, entry)
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
@PDF_OPTION
@click.option('--field', help='Field to edit.')
@click.pass_context
def edit(ctx, search_terms, key, field, pdf, **kwargs):
    type_ = kwargs.pop('type')

    data = ctx.obj['data']
    entry = query.get(data, search_terms)

    if type_:
        entry['type'] = type_
    if key:
        entry['key'] = key
    if pdf:
        set_pdf(data, entry, pdf)
    if field:
        current_value = entry['fields'].get(field, '')
        updated_value = click.edit(text=current_value).strip()
        entry['fields'][field] = updated_value

    pybibs.write_file(data, ctx.obj['database'])


# Internals

def format_entry(entry):
    header = [click.style(entry['key'], fg='green')]
    fields = entry['fields']
    if fields.get('tags'):
        header.append(click.style(fields['tags'], fg='cyan'))
    if fields.get('file'):
        header.append('📁')
    if fields.get('url'):
        header.append('🔗')
    return '\n'.join([
        ' '.join(header),
        '''{author} ({year}). {title}'''.format_map(fields)
    ])


def open_file(filepath):
    """
    Open file with the default system app.
    Copied from https://stackoverflow.com/a/435669/1224456
    """
    if sys.platform.startswith('darwin'):
        subprocess.Popen(('open', filepath))
    elif os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        subprocess.Popen(('xdg-open', filepath))


def default_destination_path(data):
    """
    A heuristic to get the folder with all other files from bib, using majority
    vote.
    """
    counter = collections.Counter()
    for entry in data:
        file_field = entry['fields'].get('file')
        if not file_field:
            continue
        path = os.path.dirname(file_field)
        counter[path] += 1
    return sorted(counter, reverse=True)[0]


def remove_entry(data, entry):
    '''
    Remove an entry in place.
    '''
    file_field = entry['fields'].get('file')
    if file_field:
        try:
            os.remove(file_field)
        except FileNotFoundError:
            click.echo('This entry\'s file was missing')

    data.remove(entry)


def set_pdf(data, entry, pdf):
    destination_path = default_destination_path(data)
    destination = os.path.join(destination_path, entry['key'] + '.pdf')
    entry['fields']['file'] = f':{destination}:PDF'
    shutil.copy(pdf, destination)


if __name__ == '__main__':
    cli()
