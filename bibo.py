import os
import re
import subprocess
import sys

import click
from pybtex.database import parse_file
import requests

import dict_printer
import scholar

FILE_FIELD = re.compile('^:(?P<filepath>.*):PDF$')


@click.group()
@click.argument('bib_file', type=str)
def cli(bib_file):
    """
    Simple command line bibliography manager.
    """
    cli.bib_data = parse_file(bib_file)


@cli.command(name='import')
@click.argument('pdf_file', type=click.File('r'))
@click.option('--directory', type=click.Path(file_okay=False, writable=True),
              default=None, help='Directory to move the PDF to.')
def import_(pdf_file, directory):
    """
    Import new entry from file.
    """
    print(f'import {pdf_file} {directory}')
    # settings = scholar.ScholarSettings()
    # settings.set_citation_format(scholar.ScholarSettings.CITFORM_BIBTEX)
    # querier = scholar.ScholarQuerier()
    # querier.apply_settings(settings)
    # query = scholar.SearchScholarQuery()
    # query.set_words('transformed social interaction')
    # querier.send_query(query)
    # # scholar.txt(querier, with_globals=False)
    # scholar.citation_export(querier)
    text_search_url = 'https://search.crossref.org/dois?q=transformed+social+interaction'
    doi_search_url = 'http://api.crossref.org/v1/works/{doi}/transform/application/x-bibtex'
    resp = requests.get(text_search_url)
    assert resp.status_code == 200, resp.status_code
    for result in resp.json():
        resp = requests.get(doi_search_url.format(doi=result['doi']))
        assert resp.status_code == 200, resp.status_code
        print(resp.content.decode('utf-8'))


@cli.command()
@click.argument('search_query', type=str)
def search(search_query):
    """
    Search an entry in the database.
    """
    for entry in search_gen(cli.bib_data, search_query):
        click.echo(click.style(entry.key, fg='green'))
        print(entry_pretty_format(entry))


@cli.command()
@click.argument('search_query', type=str)
def read(search_query):
    """
    Open a PDF for reading using the system PDF reader.
    """
    entries = list(search_gen(cli.bib_data, search_query))

    error = None
    if not entries:
        error = 'No entries found.'
    elif len(entries) > 1:
        error = 'Multiple entries found. Try to refine the search.'

    if error:
        click.echo(click.style(error, fg='red'))
    else:
        entry = entries[0]
        filepath = re.match(FILE_FIELD, entry.fields['file']).group('filepath')
        click.launch(filepath)


# Internals

def search_gen(bib_data, search_query):
    """
    Generate entries from the bib_data that matches the search term.
    """
    for entry in bib_data.entries.values():
        if entry_match_search(entry, search_query):
            yield entry


def entry_match_search(entry, search_query):
    if text_match_search(entry.key, search_query):
        return True
    elif any(text_match_search(f, search_query) for f in entry.fields.values()):
        return True
    return False


def text_match_search(text, search_query):
    return search_query.lower() in text.lower()


def entry_pretty_format(entry):
    """
    Pretty formatting an entry.
    """
    as_dict = {key: val for key, val in entry.fields.items()}
    try:  # The author field is weirdly implemented, hacking it in
        as_dict['author'] = entry.fields['author']
    except KeyError:
        pass
    return dict_printer.format(as_dict, ordered_keys=['author', 'year', 'title'])
