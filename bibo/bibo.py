"""
Command line reference manager with a single source of truth: the .bib file.
Inspired by beets.
"""

import collections
import datetime
import os
import re
import shutil
import subprocess
import sys

import click
import pybibs
import pyperclip

from . import query

FILE_FIELD = re.compile('^:(?P<filepath>.*):[A-Z]+$')
PATH_OPTION = click.Path(exists=True, writable=True, readable=True,
                         dir_okay=False)
PDF_OPTION = click.option(
    '--pdf',
    help='PDF to link to this entry.',
    type=click.Path(exists=True, readable=True, dir_okay=False),
)


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
@click.argument('search_term')
@click.pass_context
def list(ctx, search_term, raw):
    for entry in query.search(ctx.obj['data'], search_term):
        if raw:
            txt = pybibs.write_string({entry['key']: entry})
        else:
            txt = format_entry(entry)
        click.echo(txt)


@cli.command(short_help='Open the PDF linked to an entry.')
@click.argument('search_term')
@click.pass_context
def open(ctx, search_term):
    try:
        entry = query.get(ctx.obj['data'], search_term)
    except query.QueryException as e:
        click.echo(str(e))
        sys.exit(1)

    if not 'file' in entry:
        click.echo('No file is associated with this entry')
        sys.exit(1)

    pdfpath = file_field_to_filepath(entry['file'])
    open_file(pdfpath)


@cli.command(short_help='Add a new entry.')
@PDF_OPTION
@click.pass_context
def add(ctx, pdf):
    data = ctx.obj['data']
    bib = click.edit(text=pyperclip.paste())
    entry = pybibs.read_entry_string(bib)
    data[entry['key']] = entry

    if pdf:
        set_pdf(data, entry, pdf)

    pybibs.write_file(data, ctx.obj['database'])


@cli.command(short_help='Remove an entry or a field.')
@click.argument('search_term')
@click.option('--field', help='Field to remove.')
@click.pass_context
def remove(ctx, search_term, field):
    data = ctx.obj['data']

    for entry in query.search(data, search_term):
        if field is None:
            remove_entry(data, entry)
        else:
            if field in entry:
                del entry[field]
            else:
                click.echo('No such field')

    pybibs.write_file(data, ctx.obj['database'])


@cli.command('mark-read', short_help='Mark an entry as read.')
@click.argument('search_term')
@click.pass_context
def mark_read(ctx, search_term):
    data = ctx.obj['data']
    try:
        entry = query.get(data, search_term)
    except query.QueryException as e:
        click.echo(str(e))
        sys.exit(1)

    entry['readdate'] = str(datetime.date.today())

    pybibs.write_file(data, ctx.obj['database'])


@cli.command(short_help='Edit an entry.')
@click.argument('search_term')
@click.option('--type', help='Set the type.')
@click.option('--key', help='Set the key.')
@PDF_OPTION
@click.option('--field', help='Field to edit.')
@click.pass_context
def edit(ctx, search_term, key, field, pdf, **kwargs):
    type_ = kwargs.pop('type')

    data = ctx.obj['data']
    try:
        entry = query.get(data, search_term)
    except query.QueryException as e:
        click.echo(str(e))
        sys.exit(1)

    if type_:
        entry['type'] = type_
    if key:
        entry['key'] = key
        data[key] = entry
    if pdf:
        set_pdf(data, entry, pdf)
    if field:
        current_value = entry.get(field, '')
        updated_value = click.edit(text=current_value).strip()
        entry[field] = updated_value

    pybibs.write_file(data, ctx.obj['database'])


# Internals

def format_entry(fields):
    header = [click.style(fields['key'], fg='green')]
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
    for entry in data.values():
        if not 'file' in entry:
            continue
        _, full_path, _ = entry['file'].split(':')
        path = os.path.dirname(full_path)
        counter[path] += 1
    return sorted(counter, reverse=True)[0]


def file_field_to_filepath(file_field):
    return re.match(FILE_FIELD, file_field).group('filepath')


def remove_entry(data, entry):
    '''
    Remove an entry in place.
    '''
    file_field = entry.get('file')
    if file_field:
        try:
            os.remove(file_field_to_filepath(file_field))
        except FileNotFoundError:
            click.echo('This entry\'s file was missing')

    del data[entry['key']]


def set_pdf(data, entry, pdf):
    destination_path = default_destination_path(data)
    destination = os.path.join(destination_path, entry['key'] + '.pdf')
    entry['file'] = f':{destination}:PDF'
    shutil.copy(pdf, destination)


if __name__ == '__main__':
    cli()
