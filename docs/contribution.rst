Contribution
============

Installing the development environment
--------------------------------------

Make sure the :ref:`prerequisites <Prerequisites>` are installed.

Then, preferably in a virtual environment, run

.. code-block:: bash

    pip install -e .[dev]


Running tests
-------------

.. code-block:: bash

    pytest

It automatically checks code formatting with `black <https://github.com/psf/black>`_. If code formatting errors are detected they can be manually fixed, or try running ``black .``.


Generating the documentation
----------------------------

.. code-block:: bash

    cd docs
    make html

To view the documentation, in a separate terminal, run

.. code-block:: bash

    cd _build/html
    python -m http.server

Now open your browser and go to `http://localhost:8000 <http://localhost:8000>`_.

Cleaning the docs is handy. Use

.. code-block:: bash

    make clean


Commits and pull requests
-------------------------

Contributions to bibo are highly welcome!
Please include tests for whatever you're working on.
Don't worry about code coverage too much.
Before commiting your changes make sure all tests pass.

Try to include the issue number in the commit message if relevant, as per `this tutorial <https://help.github.com/en/enterprise/2.16/user/github/managing-your-work-on-github/closing-issues-using-keywords>`_.
Use ``#XXX`` to reference the issue or ``Fix #XXX`` if issue fixed by the commit.

Pull requests should be based on the ``dev`` branch.

Feel free to add yourself to the CONTRIBUTORS file 😊


Plugins development
-------------------

Take a look at some of the existing :ref:`plugins <plugins>`.
They use the `click-plugins <https://github.com/click-contrib/click-plugins>`_ library, so check out its documentation.
Note that internal APIs in bibo (and the packages that are installed with it, like pybibs and click_constraints) will probably change quite a lot until bibo gets a stable release.
