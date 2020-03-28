bibo
####

.. image:: https://travis-ci.org/Nagasaki45/bibo.svg?branch=master
    :target: https://travis-ci.org/Nagasaki45/bibo

.. image:: https://codecov.io/gh/Nagasaki45/bibo/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/Nagasaki45/bibo

Command line reference manager with a single source of truth: the ``.bib`` file. Inspired by `beets`_.

.. image:: https://asciinema.org/a/313768.svg
  :target: https://asciinema.org/a/313768

Why?
----

There are many reference managers out there, so why writing another one? bibo is different for a few reasons:

1. It relies solely on your ``.bib`` file to track information. This is bibo's main selling point! Your ``.bib`` file and your other files (PDFs, for example) are exactly where you want them to be. You have full control over your data.
2. Being a command line tool, integration with other command line applications is easy and powerful.
3. It's extensible with plugins (more on this later).


Installation
-------------

Prerequisites
=============

1. On linux, make sure to install ``xclip``.
2. Optionally, define the ``EDITOR`` environment variable to an editor of your choice (this is usually already set on unix systems).
3. Optionally, for improved presentation, install ``bibtex``.


``pip`` installation
====================

.. code-block:: bash

    pip3 install bibo


On linux / mac you might need to prepend the above command with ``sudo`` for system wide installation, or, preferably, use the ``--user`` flag like this:

.. code-block:: bash

    pip3 install --user bibo


For more information see the `official packages installation guide`_.


Auto-complete
=============

To activate auto-complete, if you're using Bash add the following to your ``.bashrc``

.. code-block:: bash

    eval "$(_BIBO_COMPLETE=source bibo)"

If you're on zsh add this to your ``.zshrc``

.. code-block:: bash

    eval "$(_BIBO_COMPLETE=source_zsh bibo)"

Now, while in the middle of a command, press <TAB> to auto-complete options, arguments, or keys from your ``.bib`` database.


Quick start guide
-----------------

- `Setup your database`_
- Commands_

  - list_
  - add_
  - open_
  - edit_
  - remove_

- Queries_


.. _`Setup your database`:

Setup your database
=====================

The ``--database`` argument
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When running bibo you should tell it where your ``.bib`` file is. For example, to list the entries in your database, run

.. code-block:: bash

    bibo --database /path/to/your/database.bib list

If you don't yet have a ``.bib`` file, or want to start working on a new one pass a path to where you want your ``.bib`` file to be and bibo will create the new file for you.


The ``BIBO_DATABASE`` environment variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most of the time you will probably use the same ``.bib`` file. So, instead of passing the ``--database`` argument whenever you call bibo you can define the ``BIBO_DATABASE`` environment variable with the path to your ``.bib`` file. From now on, if you don't pass the ``--database`` argument explicitly, bibo will use this predefined database. Note that this is the only bit of configuration bibo uses. Everything else is in your ``.bib`` file!


.. _Commands:

Commands
========

To check all of bibo's commands run

.. code-block:: bash

    bibo --help


To read additional information about each command and its arguments run, for example

.. code-block:: bash

    bibo list --help


.. _list:

``list``
~~~~~~~~

Listing all entries in the database, or filtered with search terms (see bellow). For example

.. code-block:: bash

    bibo list Albert Einstein

will list all entries with the values 'Albert' and 'Einstein' in any field (or type / key). Use the ``--raw`` option to list the raw bibtex entry, without fancy formatting, or provide a bibstyle to adapt the listing to specific citing format. Valid bibstyles are determined by the bibtex software, check out `this <https://www.overleaf.com/learn/latex/Bibtex_bibliography_styles>`_ for reference. The default bibstyle is ``plain``.


.. _add:

``add``
~~~~~~~

To add a new entry to the database, copy the ``bibtex`` citation from, let's say, google scholar, and run

.. code-block:: bash

    bibo add

bibo will open your editor and paste the clipboard content to it. You are free to edit this content and save it to add the entry to the database.

If you want to include a file (a PDF, for example) run the same command with ``--file /path/to/file`` at the end. After saving the bibtex citation in the editor bibo will search through the already existing paths in your database, find the most commonly used one, and copy the file you specified to there, renaming it to the bibtex key. If you don't want this automatic destination heuristic you can specify the destination yourself by adding ``--destination /path/to/folder/``.


.. _open:

``open``
~~~~~~~~

Try running

.. code-block:: bash

    bibo open Albert Einstein


Lets assume that there's a single entry in the database by Albert Einstein (more about search terms below), and the ``file`` / ``url`` / ``doi`` field is defined. An ``open`` command will open the file / URL / DOI of this entry, with precedence following this order. A file will be opened with the appropriate application. If it's a PDF it will probably be your PDF reader. But it can also be a presentation, ``.zip`` file, or even a folder. URLs and DOIs would be opened by your web browser.


.. _edit:

``edit``
~~~~~~~~

The ``edit`` command allows you to edit a single entry by key. You can set a field / key / type by running, for example

.. code-block:: bash

    bibo edit einstein_paper tags=interesting

Setting the key / type is the same.

If the value is omitted your editor will open with the current content of the field (or empty if there was no title). Saving will update the database.

The ``edit`` command is also used to link a file to the entry. It is done exactly the same way as the ``add`` command.


.. _remove:

``remove``
~~~~~~~~~~

The ``remove`` command is used to remove an entry by key, like that

.. code-block:: bash

    bibo remove einstein_paper

It can also remove one or more fields, for example

.. code-block:: bash

    bibo remove einstein_paper tags review


.. _Queries:

Queries
=======

Most of bibo's commands expect you to provide search terms. Some of them, like the ``open`` command, will only work if the search terms matches a single entry in the database. A single search term matches an entry if it appears in the type, key, or any of the fields of the entry. If multiple search terms are provided an entry should match all of them. Note that search terms are case insensitive. In addition, it is possible to match against a specific field with, for example ``author:einstein`` or ``year:2018``. You can match against type / key in a similar fashion, with, let's say ``type:book``.


Plugins by the community
------------------------

bibo is extensible with plugins. Here are some examples by the community:

- `bibo-todo <https://github.com/Kappers/bibo-todo>`_: Plugin for bibo, mark entry as todo with optional note.
- `bibo-mark-read <https://github.com/Nagasaki45/bibo-mark-read>`_: A bibo plugin to mark that an entry was read.
- `bibo-check <https://github.com/Nagasaki45/bibo-check>`_: A bibo plugin to check for mess in your files.

Send a pull request to add your bibo plugins to the list.


.. _beets: https://github.com/beetbox/beets
.. _`official packages installation guide`: https://packaging.python.org/tutorials/installing-packages/
