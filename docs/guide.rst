Quick start guide
=================


Setup your database
-------------------

The ``--database`` argument
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When running bibo you should tell it where your ``.bib`` file is. For example, to list the entries in your database, run

.. code-block:: bash

    bibo --database /path/to/your/database.bib list

If you don't yet have a ``.bib`` file, or want to start working on a new one pass a path to where you want your ``.bib`` file to be and bibo will create the new file for you.


The ``BIBO_DATABASE`` environment variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most of the time you will probably use the same ``.bib`` file. So, instead of passing the ``--database`` argument whenever you call bibo you can define the ``BIBO_DATABASE`` environment variable with the path to your ``.bib`` file. From now on, if you don't pass the ``--database`` argument explicitly, bibo will use this predefined database. Note that this is the only bit of configuration bibo uses. Everything else is in your ``.bib`` file!


Commands
--------

To check all of bibo's commands run

.. code-block:: bash

    bibo --help


To read additional information about each command and its arguments run, for example

.. code-block:: bash

    bibo list --help


``list``
~~~~~~~~

Listing all entries in the database, or filtered with search terms (see bellow). For example

.. code-block:: bash

    bibo list Albert Einstein

will list all entries with the values 'Albert' and 'Einstein' in any field (or type / key). Use the ``--raw`` option to list the raw bibtex entry, without fancy formatting, or provide a bibstyle to adapt the listing to specific citing format. Valid bibstyles are determined by the bibtex software, check out `this <https://www.overleaf.com/learn/latex/Bibtex_bibliography_styles>`_ for reference. The default bibstyle is ``plain``.


``add``
~~~~~~~

To add a new entry to the database, copy the ``bibtex`` citation from, let's say, google scholar, and run

.. code-block:: bash

    bibo add

bibo will open your editor and paste the clipboard content to it. You are free to edit this content and save it to add the entry to the database.

If you want to include a file (a PDF, for example) run the same command with ``--file /path/to/file`` at the end. After saving the bibtex citation in the editor bibo will search through the already existing paths in your database, find the most commonly used one, and copy the file you specified to there, renaming it to the bibtex key. If you don't want this automatic destination heuristic you can specify the destination yourself by adding ``--destination /path/to/folder/``.


``open``
~~~~~~~~

Try running

.. code-block:: bash

    bibo open Albert Einstein


Lets assume that there's a single entry in the database by Albert Einstein (more about search terms below), and the ``file`` / ``url`` / ``doi`` field is defined. An ``open`` command will open the file / URL / DOI of this entry, with precedence following this order. A file will be opened with the appropriate application. If it's a PDF it will probably be your PDF reader. But it can also be a presentation, ``.zip`` file, or even a folder. URLs and DOIs would be opened by your web browser.


``edit``
~~~~~~~~

The ``edit`` command allows you to edit a single entry by key. You can set a field / key / type by running, for example

.. code-block:: bash

    bibo edit einstein_paper tags=interesting

Setting the key / type is the same.

If the value is omitted your editor will open with the current content of the field (or empty if there was no title). Saving will update the database.

The ``edit`` command is also used to link a file to the entry. It is done exactly the same way as the ``add`` command.


``remove``
~~~~~~~~~~

The ``remove`` command is used to remove an entry by key, like that

.. code-block:: bash

    bibo remove einstein_paper

It can also remove one or more fields, for example

.. code-block:: bash

    bibo remove einstein_paper tags review


Queries
-------

Most of bibo's commands expect you to provide search terms. Some of them, like the ``open`` command, will only work if the search terms matches a single entry in the database. A single search term matches an entry if it appears in the type, key, or any of the fields of the entry. If multiple search terms are provided an entry should match all of them. Note that search terms are case insensitive. In addition, it is possible to match against a specific field with, for example ``author:einstein`` or ``year:2018``. You can match against type / key in a similar fashion, with, let's say ``type:book``.
