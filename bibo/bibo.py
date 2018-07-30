"""
A reference manager with single source of truth: the .bib file.
"""

import collections
import os
import re
import subprocess
import sys

from flask import Flask, session, redirect, url_for, render_template, request
import pybibs

FILE_FIELD = re.compile('^:(?P<filepath>.*):[A-Z]+$')

app = Flask(__name__)
app.secret_key = "It's a secret"

filepath = sys.argv[1]


@app.route('/')
def index():
    bib_data = pybibs.read_file(filepath)
    return render_template(
        'index.html',
        bib_data=bib_data,
        bib_file=os.path.basename(filepath),
    )


@app.route('/entry/<entry_key>/open-file')
def open_file(entry_key):
    bib_data = pybibs.read_file(filepath)
    entry = bib_data[entry_key]
    pdfpath = re.match(FILE_FIELD, entry['file']).group('filepath')
    open_file(pdfpath)
    return 'Success!'


@app.route('/add', methods=['GET', 'POST'])
def add():
    bib_data = pybibs.read_file(filepath)

    if request.method == 'GET':
        return render_template(
            'add.html',
            destination_path=default_destination_path(bib_data),
        )

    else:
        pdf = request.files['pdf']
        bib = request.form['bib']
        destination_path = request.form['destinationPath']
        new_entry = pybibs.read_entry_string(bib.replace('\r\n', '\n'))

        if pdf:
            destination = os.path.join(destination_path, new_entry['key'] + '.pdf')
            new_entry['file'] = f':{destination}:PDF'
            pdf.save(destination)

        # Add the new entry to the database
        bib_data[new_entry['key']] = new_entry
        pybibs.write_file(bib_data, filepath)

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
    for entry in bib_data.values():
        if not 'file' in entry:
            continue
        _, full_path, _ = entry['file'].split(':')
        path = os.path.dirname(full_path)
        counter[path] += 1
    return sorted(counter, reverse=True)[0]


def main():
    app.run()


if __name__ == '__main__':
    main()
