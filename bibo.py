"""
A reference manager with single source of truth: the .bib file.
"""

import collections
import os
import re
import subprocess
import sys

from flask import Flask, session, redirect, url_for, render_template, request
from pybtex.database import parse_file

FILE_FIELD = re.compile('^:(?P<filepath>.*):[A-Z]+$')

app = Flask(__name__)
app.secret_key = "It's a secret"

filepath = sys.argv[1]


@app.route('/')
def index():
    bib_data = parse_file(filepath)
    return render_template(
        'index.html',
        bib_data=bib_data,
        bib_file=os.path.basename(filepath),
    )


@app.route('/entry/<entry_key>')
def entry(entry_key):
    bib_data = parse_file(filepath)
    entry = bib_data.entries[entry_key]
    return render_template('entry.html', entry=entry)


@app.route('/entry/<entry_key>/open-file')
def open_file(entry_key):
    bib_data = parse_file(filepath)
    entry = bib_data.entries[entry_key]
    pdfpath = re.match(FILE_FIELD, entry.fields['file']).group('filepath')
    open_file(pdfpath)
    return 'Success!'


@app.route('/add', methods=['GET', 'POST'])
def add():
    bib_data = parse_file(filepath)
    if request.method == 'GET':
        return render_template(
            'add.html',
            destination_path=default_destination_path(bib_data),
        )
    else:
        pdf = request.files['pdf']
        bib = request.form['bib'].replace('\r\n', '\n')
        destination_path = request.form['destinationPath']

        # Append bib entry to database
        with open(filepath, 'a') as f:
            f.write('\n\n')
            f.write(bib)

        if pdf:
            # Add file field to entry
            bib_data = parse_file(filepath)
            new_entry = bib_data.entries.values()[-1]
            destination = os.path.join(destination_path, new_entry.key + '.pdf')
            new_entry.fields['file'] = f':{destination}:PDF'
            bib_data.to_file(filepath)

            # Copy file to destination
            pdf.save(destination)

        return redirect(url_for('index'))


# Internals

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


def default_destination_path(bib_data):
    """
    A heuristic to get the folder with all other files from bib, using majority
    vote.
    """
    counter = collections.Counter()
    for entry in bib_data.entries.values():
        if not 'file' in entry.fields:
            continue
        _, full_path, _ = entry.fields['file'].split(':')
        path = os.path.dirname(full_path)
        counter[path] += 1
    return sorted(counter, reverse=True)[0]


if __name__ == '__main__':
    app.run(debug=True)
