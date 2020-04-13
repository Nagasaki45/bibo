import click
import pytest  # type: ignore

from click_constraints import constrain


@constrain("no_copy", depends=["file"], conflicts=["destination"])
def add(**kwargs):
    pass  # Do something


def test_constrain():
    # Valid calls
    add()
    add(file="path/to/file.pdf")
    add(file="path/to/file.pdf", destination="path/to/folder")
    add(file="path/to/file.pdf", no_copy=True)

    # Invalid calls
    with pytest.raises(click.ClickException):
        add(no_copy=True)

    with pytest.raises(click.ClickException):
        add(file="path/to/file.pdf", destination="path/to/folder", no_copy=True)
