# coding=utf-8

import collections
import collections.abc
import glob
import itertools
import os
import re
import shutil
import typing

import click

import pybibs

from . import models

BIBO_DATABASE_ENV_VAR = "BIBO_DATABASE"
_ANSI_BOLD = "\033[1m"
_ANSI_UNBOLD = "\033[22m"


def header(entry):
    parts = [click.style(entry["key"], fg="green")]
    fields = entry["fields"]
    if fields.get("tags"):
        parts.append(click.style(fields["tags"], fg="cyan"))
    if fields.get("file"):
        parts.append("📁")
    if fields.get("url") or fields.get("doi"):
        parts.append("🔗")
    return " ".join(parts)


def format_entry(entry, format_pattern):
    output = []
    replacement_start_index = -1
    for i, char in enumerate(format_pattern):
        if char == "$":
            replacement_start_index = i + 1
        elif (not char.isalpha()) and (replacement_start_index >= 0):
            field = format_pattern[replacement_start_index:i]
            output.append(_lookup(entry, field))
            output.append(char)
            replacement_start_index = -1
        elif replacement_start_index == -1:
            output.append(char)
    if replacement_start_index >= 0:
        field = format_pattern[replacement_start_index:]
        output.append(_lookup(entry, field))
    return "".join(output)


def _lookup(entry, field):
    if field in entry:
        return entry[field]
    if "fields" in entry and field in entry["fields"]:
        return entry["fields"][field]
    return "$" + field


def destination_heuristic(data):
    """
    A heuristic to get the folder with all other files from bib, using majority
    vote.
    """
    counter = collections.Counter()
    for entry in bib_entries(data):
        file_field = entry["fields"].get("file")
        if not file_field:
            continue
        path = os.path.dirname(file_field)
        counter[path] += 1

    if not counter:  # No paths found
        raise click.ClickException(
            "Path finding heuristics failed: no paths in the database"
        )

    # Find the paths that appears most often
    sorted_paths = counter.most_common()
    groupby = itertools.groupby(sorted_paths, key=lambda x: x[1])
    _, group = next(groupby)

    # We know that there's at least one candidate. Make sure it's
    # the only one
    candidate, _ = next(group)
    try:
        next(group)
    except StopIteration:
        return candidate
    else:
        raise click.ClickException(
            "Path finding heuristics failed: "
            "there are multiple equally valid paths in the database"
        )


def string_to_basename(s):
    """
    Converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"[\s-]+", "-", s)


def set_file(data, entry, file_, destination=None, no_copy=False):
    if no_copy:
        entry["fields"]["file"] = os.path.abspath(file_)
        return

    if not destination:
        destination = destination_heuristic(data)
    destination = os.path.abspath(destination)
    _, file_extension = os.path.splitext(file_)
    basename = string_to_basename(entry["key"])
    path = os.path.join(destination, basename + file_extension)
    entry["fields"]["file"] = path
    click.echo("Copying {} to {}".format(file_, path))
    shutil.copy(file_, path)


def editor(*args, **kwargs):
    """
    Wrapper for `click.edit` that raises an error when None is returned.
    """
    result = click.edit(*args, **kwargs)
    if result is None:
        msg = "Editor exited without saving, command aborted"
        raise click.ClickException(msg)
    return result


def get_database(args):
    for arg_a, arg_b in zip(args, args[1:]):
        if arg_a == "--database":
            return arg_b


def complete_key(ctx, args, incomplete):
    """
    Autocompletion for keys.
    """
    database = get_database(args) or os.environ.get(BIBO_DATABASE_ENV_VAR)
    if database:
        data = load_database(database)
    else:
        data = []
    data = bib_entries(data)
    return [x["key"] for x in data if incomplete.lower() in x["key"].lower()]


def load_database(database):
    """
    Load the database from .bib. Create (in memory) if doesn't exist.
    """
    try:
        return pybibs.read_file(database)
    except IOError:
        return []


def combine_decorators(decorators):
    # Copied from https://stackoverflow.com/a/4122845/1224456
    def decorator(f):
        for d in reversed(decorators):
            f = d(f)
        return f

    return decorator


def bib_entries(entries):
    """
    Yield only the actual bibliographic items from a list of entries.
    Drop @string / @comment / @preamble entries.
    """
    for e in entries:
        if e["type"].lower() not in ["string", "comment", "preamble"]:
            yield e


def unique_key_validation(new_key, data):
    if new_key in (e["key"] for e in bib_entries(data)):
        raise click.ClickException("Duplicate key, command aborted")


def complete_path(ctx, args, incomplete):
    """
    Autocompletion for files, matches the glob of incomplete argument, and
    provide basename prompts.
    """
    wildc_path = os.path.expanduser(os.path.expandvars(incomplete)) + "*"
    options = []
    for path in glob.glob(wildc_path):
        if os.access(path, os.R_OK):
            options.append((path, os.path.basename(path)))
    return options


def bold(s: str) -> str:
    """Return `s` wrapped in ANSI bold."""
    return "{}{}{}".format(_ANSI_BOLD, s, _ANSI_UNBOLD)


def highlight_text(text, highlight):
    """
    Return `text` with sub-string `highlight` in bold.
    """

    def highlighter(s):
        return bold(s.group(0))

    text = re.sub(highlight, highlighter, text, flags=re.IGNORECASE)
    # Drop ANSI unbold followed by ANSI bold
    return text.replace(_ANSI_UNBOLD + _ANSI_BOLD, "")


def highlight_match(
    text: str, result: models.SearchResult, extra_match_info: dict = None
) -> typing.Tuple[str, dict]:
    """
    Highlight `text` with `result.match` info. Every bit of info that is in
    `result.match` but not in `text` is added to the `extra_match_info` to
    present to the user.
    """
    if extra_match_info is None:
        extra_match_info = {}
    for key, vals in result.match.items():
        if isinstance(vals, collections.abc.Mapping):
            inner_result = models.SearchResult(
                result.entry[key],
                result.match[key],
            )
            text, extra_match_info = highlight_match(
                text,
                inner_result,
                extra_match_info,
            )
        else:
            for val in vals:
                if val.lower() in text.lower():
                    text = highlight_text(text, val)
                else:
                    extra_match_val = extra_match_info.get(key, result.entry[key])
                    extra_match_val = highlight_text(extra_match_val, val)
                    extra_match_info[key] = extra_match_val
    return text, extra_match_info
