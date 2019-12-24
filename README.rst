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

2. Create ``pyproject.toml`` and define the ``build-system`` table. It should
   look something like this::

        [build-system]
        requires = ["setuptools", "wheel"]
        build-backend = "setuptools.build_meta"

3. Run this command to upload your code to PyPI::

        setl publish

Miscellaneous
=============

To install a package locally for development, run::

    setl install [--python path/to/python] --editable

All *build* commands are available via ``setl build``::

    setl build [--python path/to/python] [--ext] [--py] [--clib] [--scripts]

To create package distributions (equivalent to ``flit build``), use::

    setl dist [--python path/to/python] [--source] [--wheel]
