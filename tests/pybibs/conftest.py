from collections import OrderedDict

import pytest


@pytest.fixture()
def raw():
    return """
@article{israel,
  author = {Israel, Moshe},
  title = {Article title},
  year = {2008}
}

@book{orwell,
  author = {Orwell, George},
  title = {1984},
  year = {1949}
}
""".strip()


@pytest.fixture()
def parsed():
    return [
        {
            'key': 'israel',
            'type': 'article',
            'fields':
            OrderedDict([
                ('author', 'Israel, Moshe'),
                ('title', 'Article title'),
                ('year', '2008'),
            ]),
        },
        {
            'key': 'orwell',
            'type': 'book',
            'fields':
            OrderedDict([
                ('author', 'Orwell, George'),
                ('title', '1984'),
                ('year', '1949'),
            ]),
        },
    ]


@pytest.fixture
def raw_entry_key_values():
    return """
author = "Israel, Moshe",
title = "Some title",
year = 2008
""".strip()


@pytest.fixture
def database():
    return 'tests/pybibs/data/huge.bib'
