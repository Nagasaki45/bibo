"""
A reference manager with single source of truth: the .bib file.
"""

import collections
import os
import re
import shutil
import subprocess
import sys

import click
import pybibs

from . import editor_input

FILE_FIELD = re.compile('^:(?P<filepath>.*):[A-Z]+$')
PATH_OPTION = click.Path(exists=True, writable=True, readable=True,
                         dir_okay=False)

@click.group()
@click.option('--database', envvar='BIBO_DATABASE', help='A .bib file',
              required=True, type=PATH_OPTION)
@click.pass_context
def cli(ctx, database):
    ctx.ensure_object(dict)
    ctx.obj['database'] = database
    ctx.obj['data'] = pybibs.read_file(database)


@cli.command()
@click.argument('search_term')
@click.pass_context
def list(ctx, search_term):
    for entry in search(ctx.obj['data'], search_term):
        click.echo(format_entry(entry))


@cli.command()
@click.argument('search_term')
@click.pass_context
def open(ctx, search_term):
    search_results = search(ctx.obj['data'], search_term)
    try:
        entry = next(search_results)
    except StopIteration:
        click.echo('No results found')
        sys.exit(1)
    try:
        next(search_results)
    except StopIteration:
        pass
    else:
        click.echo('Search returned multiple results')
        sys.exit(1)

    if not 'file' in entry:
        click.echo('No file is associated with this entry')
        sys.exit(1)

    pdfpath = re.match(FILE_FIELD, entry['file']).group('filepath')
    open_file(pdfpath)
 
 
@cli.command()
@click.option('--pdf', help='PDF to link to this entry',
              type=click.Path(exists=True, readable=True, dir_okay=False))
@click.pass_context
def add(ctx, pdf):
    data = ctx.obj['data']
    bib = editor_input.editor_input()
    new_entry = pybibs.read_entry_string(bib)

    if pdf:
        destination_path = default_destination_path(data)
        destination = os.path.join(destination_path, new_entry['key'] + '.pdf')
        new_entry['file'] = f':{destination}:PDF'
        shutil.copy(pdf, destination)

    # Add the new entry to the database
    data[new_entry['key']] = new_entry
    pybibs.write_file(data, ctx.obj['database'])


# Internals


def search(data, search_term):
    for key, fields in data.items():
        for field in fields.values():
            if search_term.lower() in field.lower():
                yield fields
                break


def format_entry(fields):
    return fields['key']


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


if __name__ == '__main__':
    cli()
