import os
import re
import subprocess
import tempfile


def cite(keys, database, bibstyle='plain'):
    aux_filepath = _write_aux_file(keys, database, bibstyle)
    _bibtex(aux_filepath)
    bbl_filepath = aux_filepath.replace('.aux', '.bbl')
    return _parse_bbl(bbl_filepath)


def _write_aux_file(keys, database, bibstyle):
    auxfile = tempfile.NamedTemporaryFile('w', suffix='.aux', delete=False)
    with auxfile as f:
        print(r'\bibdata{{{}}}'.format(database), file=f)
        print(r'\bibstyle{{{}}}'.format(bibstyle), file=f)
        for key in keys:
            line = r'\citation{{{}}}'.format(key)
            print(line, file=f)

    return auxfile.name


def _bibtex(aux_filepath):
    cwd, aux_filename = os.path.split(aux_filepath)
    p = subprocess.Popen(['bibtex', aux_filename], cwd=cwd)
    p.wait()
    assert p.returncode == 0


bibitem_pattern = re.compile(r'^\\bibitem(\[.*\])?\{(?P<key>.*)\}\n')


def _parse_bbl(bbl_filepath):
    with open(bbl_filepath) as f:
        content = f.read()

    to_return = {}

    raw_items = content.split('\n\n')

    for raw in raw_items[1:-1]:
        key = bibitem_pattern.search(raw).group('key')
        to_return[key] = _process_text(raw)

    return to_return


def _process_text(text):
    text = re.sub(bibitem_pattern, '', text)
    text = ' '.join(l.strip() for l in text.splitlines())
    lines = text.split('\\newblock ')
    text = ' '.join(_process_line(l) for l in lines)
    return text


def _process_line(line):
    line = line.strip()
    line = line.replace('~', ' ')
    line = re.sub(r'\{\\em (.*)\}', r'\1', line)
    return line
