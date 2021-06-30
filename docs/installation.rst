Installation
============

Prerequisites
-------------

1. On linux, make sure to install ``xclip``.
2. Optionally, define the ``EDITOR`` environment variable to an editor of your choice (this is usually already set on unix systems).
3. Optionally, for improved presentation, install ``bibtex``.


``pip`` installation
--------------------

.. code-block:: bash

    pip3 install bibo


On linux / mac you might need to prepend the above command with ``sudo`` for system wide installation, or, preferably, use the ``--user`` flag like this:

.. code-block:: bash

    pip3 install --user bibo


For more information see the `official packages installation guide`_.


Auto-complete
-------------

To activate auto-complete, if you're using Bash add the following to your ``.bashrc``

.. code-block:: bash

    eval "$(_BIBO_COMPLETE=bash_source bibo)"

If you're on zsh add this to your ``.zshrc``

.. code-block:: bash

    eval "$(_BIBO_COMPLETE=zsh_source bibo)"

Now, while in the middle of a command, press <TAB> to auto-complete options, arguments, or keys from your ``.bib`` database.

.. _`official packages installation guide`: https://packaging.python.org/tutorials/installing-packages/
