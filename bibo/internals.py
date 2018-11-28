import collections
import itertools
import os
import shutil
import subprocess
import sys

import click


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


def destination_heuristic(data):
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

    if not counter:  # No paths found
        return None

    # Find the paths that appears most often
    sorted_paths = sorted(counter, reverse=True)
    groupby = itertools.groupby(sorted_paths, key=len)
    _, group = next(groupby)

    # We know that there's at least one candidate. Make sure it's
    # the only one
    candidate = next(group)
    try:
        next(group)
    except StopIteration:
        return candidate
    else:
        return None


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


def set_file(data, entry, file_):
    destination_path = destination_heuristic(data)
    _, file_extension = os.path.splitext(file_)
    destination = os.path.join(destination_path, entry['key'] + file_extension)
    entry['fields']['file'] = destination
    shutil.copy(file_, destination)
