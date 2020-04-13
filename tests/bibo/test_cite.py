from unittest import mock

import click
import pytest  # type: ignore

from bibo import cite


def test_cite_simple(database):
    results = cite.cite(["tolkien1937hobit"], database)
    expected = "John R. R. Tolkien. The Hobbit. 1937."
    assert results["tolkien1937hobit"] == expected


def test_cite_complex1(database):
    key = "duncan1974signalling"
    results = cite.cite([key], database)
    expected = "Starkey Duncan Jr and George Niederehe. On signalling that it's your turn to speak. Journal of experimental social psychology, 10(3):234--247, 1974."
    assert results[key] == expected


def test_cite_complex2(database):
    key = "gurion2018real"
    results = cite.cite([key], database)
    expected = "Tom Gurion, Patrick GT Healey, and Julian Hough. Real-time testing of non-verbal interaction: An experimental method and platform. In The 22nd workshop on the Semantics and Pragmatics of Dialogue, 2018."
    assert results[key] == expected


def test_cite_no_keys(database):
    result = cite.cite([], database)
    assert result == {}


@mock.patch("subprocess.Popen")
def test_cite_missing_bibtex(popen_mock, database):
    popen_mock.side_effect = OSError()
    with pytest.raises(cite.BibtexException, match="bibtex is not available") as e:
        cite.cite(["tolkien1937"], database)


@mock.patch("subprocess.Popen")
def test_cite_bibtex_issues(popen_mock, database):
    p = mock.Mock()
    p.wait.return_value = 1
    popen_mock.return_value = p
    with pytest.raises(cite.BibtexException, match="bibtex failed") as e:
        cite.cite(["tolkien1937"], database)
