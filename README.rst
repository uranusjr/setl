====
Setl
====

Setl (pronounced like *settle*) is a simple way to work with PEP 518 projects
with Setuptools as the backend.

The interface is strongly influenced by Flit_. Currently a proof of concept.

.. _Flit: https://flit.readthedocs.io/en/latest/


Usage
=====

1. Create a project with appropriate ``setup.py`` and/or ``setup.cfg`` metadata
   declarations.

2. Create ``pyproject.toml`` and provide the needed `PEP 518`_ definitions. An
   empty file is sufficient if you want to use the default values.

3. Run this command to upload your code to PyPI (using ``--python`` to
   specify the Python to build the package against)::

        setl --python path/to/python publish

.. _`PEP 518`: https://www.python.org/dev/peps/pep-0518/


Miscellaneous
=============

To install a package locally for development, run::

    setl --python path/to/python develop

(This is simply a wrapper to ``path/to/python -m pip install -e``.)

All *build* commands are available via ``setl build``::

    setl --python path/to/python build [--ext] [--py] [--clib] [--scripts]

To create package distributions (equivalent to ``flit build``), use::

    setl --python path/to/python dist [--source] [--wheel]

The ``--python`` specification accepts one of the followings:

* Absolute or relative path to a Python executable.
* Python command (``shutil.which`` is used to resolve).
* Python version specifier (the `Python launcher`_ is used to resolve).

.. _`Python launcher`: https://www.python.org/dev/peps/pep-0397/

It can also be specified by environment variable ``SETL_PYTHON``.

If not specified, Setl will try to infer the command from virtual environment
contextx, both the one currently active, and the one Setl is installed in.
The option is required if there’s no active virtual environment, and Setl is
installed globally.
