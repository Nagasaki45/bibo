import os

import pybibs


def test_read_string(raw):
    bib = pybibs.read_string(raw)
    assert len(bib) == 2
    entry = bib[0]
    assert entry['key'] == 'israel'
    assert entry['type'] == 'article'
    assert entry['fields']['author'] == 'Israel, Moshe'
    assert entry['fields']['year'] == '2008'


def test_read_file(database):
    bib = pybibs.read_file(database)
    for entry in bib:
        if entry['key'] == 'bailenson2005digital':
            break
    else:
        raise AssertionError('Couldn\'t find bailenson2005digital in parsed data')


def test_entry_contains_key_and_type(raw):
    bib = pybibs.read_string(raw)
    assert bib[0]['key'] == 'israel'
    assert bib[0].get('type') == 'article'


def test_read_multiline(multiline_entry):
    bib = pybibs.read_string(multiline_entry)
    assert bib[0]['fields']['author'] == 'Israel, Moshe and Yosef, Shlomo'


def test_read_bens_multiline(bens_multiline_entry):
    bib = pybibs.read_string(bens_multiline_entry)
    fields = bib[0]['fields']
    expected_title = '{Radio Time-Domain Signatures of Magnetar Birth}'
    expected_keywords = 'Astrophysics - High Energy Astrophysical Phenomena'
    assert fields['title'] == expected_title
    assert fields['keywords'] == expected_keywords
    assert fields['year'] == '2019'
