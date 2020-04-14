Quick start guide
=================

bibo is a command line application, so some familiarity with the command line is assumed.
Make sure you followed the :ref:`installation <Installation>` first.
Now, let's dive in!


Setting up the database
-----------------------

When running bibo you should tell it where your ``.bib`` file is.
It is commonly done by setting the ``BIBO_DATABASE`` environment variable.
On unix, run the following (google for other OSs).

.. code-block:: bash

    export BIBO_DATABASE=bibo_test.bib

Bibo will create the file when we start to add entries to it.


Adding entries
--------------

Now, copy the ``bibtex`` entry below to the clipboard:

.. code-block::

    @article{einstein1935can,
      title={Can quantum-mechanical description of physical reality be considered complete?},
      author={Einstein, Albert and Podolsky, Boris and Rosen, Nathan},
      journal={Physical review},
      volume={47},
      number={10},
      pages={777},
      year={1935},
      publisher={APS}
    }

Let's add this entry to bibo's database.

.. code-block:: bash

    bibo add

bibo will open your editor and paste the clipboard content to it.
You are free to manually edit the raw entry.
When ready, save and exit the editor.

We can also add entries by their `digital object identifier (DOI) <https://en.wikipedia.org/wiki/Digital_object_identifier>`_.

.. code-block:: bash

    bibo add --doi 10.1037/0033-295X.108.4.814

Again, save and exit.


Searching
---------

.. code-block:: bash

    bibo list Albert Einstein

will list all entries with the values 'Albert' and 'Einstein' in any field (or type / key).
Try to search for the other entry we added by DOI, the one from Haidt.


Opening entries
---------------

Try running

.. code-block:: bash

    bibo open haidt

It should open the browser and take you to the page where the DOI is pointing.
Opening entries with a PDF file in their ``file`` field opens the PDF in your reader.


Where to go from here
---------------------

We have only scratched the surface with the 3 most important commands of bibo: ``add``, ``list``, and ``open``.
You can discover the rest of the commands with

.. code-block:: bash

    bibo --help

Each command also has a ``--help`` option.
Don't be scared to use it.
