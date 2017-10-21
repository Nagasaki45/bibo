"""
A reference manager with single source of truth: the .bib file.
"""

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
    bib_data = load_bib(filepath)
    return render_template('index.html', bib_data=bib_data)


@app.route('/entry/<entry_key>')
def entry(entry_key):
    bib_data = load_bib(filepath)
    entry = bib_data.entries[entry_key]
    return render_template('entry.html', entry=entry)


@app.route('/entry/<entry_key>/open-file')
def open_file(entry_key):
    bib_data = load_bib(filepath)
    entry = bib_data.entries[entry_key]
    pdfpath = re.match(FILE_FIELD, entry.fields['file']).group('filepath')
    open_file(pdfpath)
    return 'Success!'


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('import.html')
    else:
        pdf = request.files['pdf']
        # TODO do something
        # pdf.save('/var/www/uploads/uploaded_file.txt')
        return redirect(url_for('index'))


# Internals

def load_bib(filepath):
    bib_data = parse_file(filepath)

    # An awful hack to put the weirdly implemented author in the dict.
    for entry in bib_data.entries.values():
        try:
            entry.fields['author'] = entry.fields['author']
        except KeyError:
            pass

    return bib_data


def open_file(filepath):
    """
    Open file with the default system app.
    Copied from https://stackoverflow.com/a/435669/1224456
    """
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', filepath))
    elif os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', filepath))


if __name__ == '__main__':
    app.run(debug=True)
