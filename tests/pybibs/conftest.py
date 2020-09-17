from collections import OrderedDict

import pytest  # type: ignore


@pytest.fixture()
def raw():
    return """
@article{israel,
  author = {Israel, Moshe},
  title = {Article title},
  year = {2008},
}

@book{orwell,
  author = {Orwell, George},
  title = {1984},
  year = {1949},
}
""".strip()


@pytest.fixture()
def multiline_entry():
    return """
@article{israel,
    author = {Israel, Moshe and
        Yosef, Shlomo}
}
""".strip()


@pytest.fixture()
def bens_multiline_entry():
    return """
@ARTICLE{2019arXiv190304691L,
   author = {{Law}, C.~J. and {Margalit}, B. and {Palliyaguru}, N.~T. and 
	{Metzger}, B.~D. and {Sironi}, L. and {Zheng}, Y. and {Berger}, E. and 
	{Margutti}, R. and {Beloborodov}, A. and {Nicholl}, M. and {Eftekhari}, T. and 
	{Vurm}, I. and {Williams}, P.~K.~G.},
    title = "{Radio Time-Domain Signatures of Magnetar Birth}",
  journal = {arXiv e-prints},
archivePrefix = "arXiv",
   eprint = {1903.04691},
 primaryClass = "astro-ph.HE",
 keywords = {Astrophysics - High Energy Astrophysical Phenomena},
     year = 2019,
    month = mar,
   adsurl = {http://adsabs.harvard.edu/abs/2019arXiv190304691L},
  adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}""".strip()


@pytest.fixture()
def parsed():
    return [
        {
            "key": "israel",
            "type": "article",
            "fields": OrderedDict(
                [
                    ("author", "Israel, Moshe"),
                    ("title", "Article title"),
                    ("year", "2008"),
                ]
            ),
        },
        {
            "key": "orwell",
            "type": "book",
            "fields": OrderedDict(
                [
                    ("author", "Orwell, George"),
                    ("title", "1984"),
                    ("year", "1949"),
                ]
            ),
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
    return "tests/pybibs/data/huge.bib"
