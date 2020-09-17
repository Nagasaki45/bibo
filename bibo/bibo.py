"""
Command line reference manager with a single source of truth: the .bib file.
Inspired by beets.
"""

import os
import pkg_resources
import sys

import click
import click_constraints
import click_plugins  # type: ignore
import pybibs
import pyperclip  # type: ignore
import requests

from . import cite
from . import internals
from . import query

PATH_OPTION = click.Path(writable=True, readable=True, dir_okay=False)
FILE_OPTIONS = internals.combine_decorators(
    [
        click.option(
            "--file",
            help="Path to file to link to this entry.",
            type=click.Path(exists=True, readable=True, dir_okay=False),
            autocompletion=internals.complete_path,
        ),
        click.option(
            "--destination",
            help="A folder to put the file in.",
            type=click.Path(exists=True, readable=True, dir_okay=True, file_okay=False),
            autocompletion=internals.complete_path,
        ),
        click.option(
            "--no-copy",
            help="Add the specified file in its current location without copying.",
            is_flag=True,
        ),
        click_constraints.constrain("destination", depends=["file"]),
        click_constraints.constrain(
            "no_copy",
            depends=["file"],
            conflicts=["destination"],
        ),
    ]
)
SEARCH_TERMS_OPTION = click.argument(
    "search_term",
    nargs=-1,
    autocompletion=internals.complete_key,
)


@click_plugins.with_plugins(pkg_resources.iter_entry_points("bibo.plugins"))
@click.group(help=__doc__)
@click.version_option()
@click.option(
    "--database",
    envvar=internals.BIBO_DATABASE_ENV_VAR,
    help="""
A path to a .bib file. Overrides the BIBO_DATABASE environment variable.
""",
    required=True,
    type=PATH_OPTION,
    autocompletion=internals.complete_path,
)
@click.pass_context
def cli(ctx, database):
    ctx.ensure_object(dict)
    ctx.obj["database"] = os.path.abspath(database)
    ctx.obj["data"] = internals.load_database(database)


@cli.command("list", short_help="List entries.")
@click.option("--raw", is_flag=True, help="Format as raw .bib entries.")
@click.option(
    "--bibstyle",
    default="plain",
    help="""
Bibtex bibliography style to use for citation formatting.
For more information check https://www.overleaf.com/learn/latex/Bibtex_bibliography_styles.
""",
)
@click.option(
    "--format",
    help="""
Custom format pattern.
Use ``$`` in front of a key, type, or field to create custom formatter.
For example: ``--format '$author ($year) - $title'``.
""",
)
@click.option("--verbose", is_flag=True, help="Show verbose information.")
@SEARCH_TERMS_OPTION
@click.pass_context
def list_(ctx, search_term, raw, bibstyle, verbose, **kwargs):
    """
    List entries in the database.

    A SEARCH_TERM matches an entry if it appears in the type, key, or any
    of the fields of the entry.
    If multiple search terms are provided an entry should match all of them.
    It is possible to match against a specific key, type, or field as
    follows: ``author:einstein``, ``year:2018`` or ``type:book``.
    Note that search terms are case insensitive.
    """

    format_pattern = kwargs.pop("format")
    assert not kwargs

    results = query.search(ctx.obj["data"], search_term)
    if raw:
        _list_raw((r.entry for r in results))
    elif format_pattern:
        _list_format_pattern((r.entry for r in results), format_pattern)
    else:
        _list_citations(results, ctx.obj["database"], bibstyle, verbose)


def _list_raw(entries):
    for entry in entries:
        click.echo(pybibs.write_string([entry]))


def _list_format_pattern(entries, format_pattern):
    for entry in entries:
        click.echo(internals.format_entry(entry, format_pattern))


def _list_citations(results, database, bibstyle, verbose):
    results = list(results)
    keys = [r.entry["key"] for r in results]
    exception = None
    try:
        citations = cite.cite(keys, database, bibstyle, verbose)
    except cite.BibtexException as e:
        exception = e

    for result in results:
        header = internals.header(result.entry)
        if exception:
            citation = cite.fallback(result.entry)
        else:
            citation = citations[result.entry["key"]]

        text = "\n".join([header, citation])
        text, extra_match_info = internals.highlight_match(text, result)

        click.echo(text)

        if extra_match_info:
            click.secho("Search matched by", underline=True)
        for key, val in extra_match_info.items():
            click.echo("{}: {}".format(key, val))

    if exception is not None:
        parts = [str(exception), "Using a fallback citation method"]
        if exception.use_verbose:
            parts.append("Use --verbose for more information")
        click.secho(". ".join(parts), fg="red")


@cli.command("open", short_help="Open the file, URL, or doi associated with an entry.")
@SEARCH_TERMS_OPTION
@click.pass_context
def open_(ctx, search_term):
    """
    Open an entry in the database if a ``file``, ``url``, or ``doi`` field
    exists (with precedence in this order).

    A file will be open by the application defined by your system according
    to the file extension.
    For example, a PDF should be opened by a PDF reader and a folder should
    be opened by a file browser.
    URLs and DOIs should be opened in the web browser

    A SEARCH_TERM matches an entry if it appears in the type, key, or any
    of the fields of the entry.
    If multiple search terms are provided an entry should match all of them.
    It is possible to match against a specific key, type, or field as
    follows: ``author:einstein``, ``year:2018`` or ``type:book``.
    Note that search terms are case insensitive.

    This command fails if the number of entries that match the search is
    different than one.
    """
    entry = query.get(ctx.obj["data"], search_term).entry

    for field_name in ["file", "url", "doi"]:
        value = entry.get("fields", {}).get(field_name)
        if value:
            if field_name == "doi":
                value = "https://doi.org/" + value
            click.launch(value)
            break
    else:
        raise click.ClickException("No file, url, or doi is associated with this entry")


@cli.command(short_help="Add a new entry.")
@FILE_OPTIONS
@click.option("--doi", help="Add entry by DOI.")
@click.pass_context
def add(ctx, destination, doi, no_copy, **kwargs):
    """
    Add a new entry to the database.

    Find a bib entry you would like to add.
    Copy it to the clipboard, and run the command.
    It will be opened in your editor for validation or manual editing.
    Upon saving, the entry is added to the database.

    Don't forget to set the EDITOR environment variable for this command
    to work properly.
    """
    file_ = kwargs.pop("file")

    data = ctx.obj["data"]
    if doi is not None:
        url = "http://dx.doi.org/{}".format(doi)
        headers = {"Accept": "application/x-bibtex"}
        resp = requests.get(url, headers=headers)
        assert resp.status_code == 200
        raw_bib = resp.text
    else:
        raw_bib = pyperclip.paste()
    bib = internals.editor(text=raw_bib)
    entry = pybibs.read_entry_string(bib)

    internals.unique_key_validation(entry["key"], data)

    data.append(entry)

    if file_:
        internals.set_file(data, entry, file_, destination, no_copy)

    pybibs.write_file(data, ctx.obj["database"])


@cli.command(short_help="Remove an entry or a field.")
@click.argument("key", autocompletion=internals.complete_key)
@click.argument("field", nargs=-1)
@click.pass_context
def remove(ctx, key, field):
    """
    Remove an entry from the database or remove a field from an entry.

    To remove an entry specify its key.
    To fields specify the key and list all fields for removal.
    """
    data = ctx.obj["data"]
    entry = query.get_by_key(data, key)

    if not field:
        data.remove(entry)
    elif "fields" in entry:
        for f in field:
            if f in entry["fields"]:
                del entry["fields"][f]
            else:
                click.echo('"{}" has no field "{}"'.format(key, f))
    else:
        click.echo('"{}" has no fields'.format(key))

    pybibs.write_file(data, ctx.obj["database"])


@cli.command(short_help="Edit an entry.")
@click.argument("key", autocompletion=internals.complete_key)
@click.argument("field_value", nargs=-1)
@FILE_OPTIONS
@click.pass_context
def edit(ctx, key, field_value, destination, no_copy, **kwargs):
    """
    Edit an entry.

    Use FIELD_VALUE to set fields as follows: ``author=Einstein``, or
    ``tags=interesting``.
    Leave the value empty to open in editor.
    Set the key or type in the same way.

    Don't forget to set the EDITOR environment variable for this command
    to work properly.
    """
    file_ = kwargs.pop("file")

    data = ctx.obj["data"]
    entry = query.get_by_key(data, key)

    if file_:
        internals.set_file(data, entry, file_, destination, no_copy)
    for fv in field_value:
        if "=" in fv:
            field, value = fv.split("=")
        else:
            field = fv
            current_value = entry["fields"].get(field, "")
            value = internals.editor(text=current_value).strip()
        if field == "key":
            internals.unique_key_validation(value, data)
            entry["key"] = value
        elif field == "type":
            entry["type"] = value
        else:
            entry["fields"][field] = value

    pybibs.write_file(data, ctx.obj["database"])


if __name__ == "__main__":
    cli()
