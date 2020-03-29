from __future__ import print_function

import os
import re
import subprocess
import sys
import tempfile


class BibtexException(Exception):
    def __init__(self, msg, use_verbose=False):
        super(BibtexException, self).__init__(msg)
        self.use_verbose = use_verbose


def cite(keys, database, bibstyle="plain", verbose=False):
    if not keys:
        return {}
    aux_filepath = _write_aux_file(keys, database, bibstyle)
    _bibtex(aux_filepath, verbose)
    bbl_filepath = aux_filepath.replace(".aux", ".bbl")
    return _parse_bbl(bbl_filepath)


def fallback(entry):
    fields = entry["fields"]
    if "author" in fields and "year" in fields and "title" in fields:
        return "{author} ({year}). {title}".format(**fields)
    if "author" in fields and "year" in fields:
        return "{author} ({year})".format(**fields)
    if "author" in fields and "title" in fields:
        return "{author}. {title}".format(**fields)
    if "title" in fields and "year" in fields:
        return "{title} ({year})".format(**fields)
    return entry["type"]


def _write_aux_file(keys, database, bibstyle):
    auxfile = tempfile.NamedTemporaryFile("w", suffix=".aux", delete=False)
    with auxfile as f:
        print(r"\bibdata{{{}}}".format(database), file=f)
        print(r"\bibstyle{{{}}}".format(bibstyle), file=f)
        for key in keys:
            line = r"\citation{{{}}}".format(key)
            print(line, file=f)

    return auxfile.name


def _bibtex(aux_filepath, verbose):
    cwd, aux_filename = os.path.split(aux_filepath)
    stdout = sys.stdout if verbose else subprocess.PIPE
    stderr = sys.stderr if verbose else subprocess.PIPE
    try:
        p = subprocess.Popen(
            ["bibtex", aux_filename], cwd=cwd, stdout=stdout, stderr=stderr
        )
    except OSError:  # Common for py 2 and 3 and parent of FileNotFoundError
        raise BibtexException("bibtex is not available")
    p.wait()
    if p.returncode != 0:
        raise BibtexException("bibtex failed", use_verbose=True)


bibitem_pattern = re.compile(r"^\\bibitem(\[.*\])?\{(?P<key>.*)\}\n")


def _parse_bbl(bbl_filepath):
    with open(bbl_filepath) as f:
        content = f.read()

    to_return = {}

    raw_items = content.split("\n\n")

    for raw in raw_items[1:-1]:
        key = bibitem_pattern.search(raw).group("key")
        to_return[key] = _process_text(raw)

    return to_return


def _process_text(text):
    text = re.sub(bibitem_pattern, "", text)
    text = " ".join(l.strip() for l in text.splitlines())
    lines = text.split("\\newblock ")
    text = " ".join(_process_line(l) for l in lines)
    return text


def _process_line(line):
    line = line.strip()
    line = line.replace("~", " ")
    line = re.sub(r"\{\\em (.*)\}", r"\1", line)
    return line
