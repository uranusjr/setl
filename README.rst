====
Setl
====

Setl (pronounced like *settle*) is a simple way to work with PEP 518 projects
with Setuptools as the backend.

The interface is strongly influenced by Flit_.

.. _Flit: https://flit.readthedocs.io/en/latest/


Install
=======

The recommended install method is pipx_::

    pipx install setl

.. _pipx: https://pipxproject.github.io/pipx/

Setl needs to be installed with Python 3.7 or later, but **can be used to build
projects using older Python** with the ``--python`` option.


Quickstart for Setuptools Veterans
==================================

Aside from the usual Setuptools configurations, you need to create a file
``pyproject.toml`` beside ``setup.py``. An empty file is good enough.

Command comparisons to Setuptools:

+------------------+-------------------------------------------------+
| Setl             | Setuptools approximation                        |
+==================+=================================================+
| ``setl develop`` | ``setup.py develop``                            |
+------------------+-------------------------------------------------+
| ``setl build``   | ``setup.py egg_info build``                     |
+------------------+-------------------------------------------------+
| ``setl dist``    | ``setup.py egg_info build sdist bdist_wheel``   |
+------------------+-------------------------------------------------+
| ``setl publish`` | | ``setup.py egg_info build sdist bdist_wheel`` |
|                  | | ``twine upload``                              |
+------------------+-------------------------------------------------+


But Why?
========

The main difference is how build and runtime dependencies are installed.

Traditionally Setuptools projects use ``setup_requires``, but that has various
problems (e.g. fetch the dependencies as eggs) so pip discourages its
usage, and advices using PEP 518 to specify build time dependencies instead.
But Setuptools's project management commands do not handle PEP 518
declarations, leaving the user to install those build dependencies manually
before using ``setup.py``. Setl commands mimic pip's build setup before calling
their ``setup.py`` counterparts, so the build environment stays up-to-date.

Similarly, ``setup.py develop`` installs *runtime* dependencies with
``easy_install``, instead of pip. It therefore does not respect PEP 518
declarations in those dependencies, and may even fail if one of the
dependencies does not support the "legacy mode" build process.
``setl develop`` works around this by ``pip install``-ing runtime dependencies
before calling ``setup.py develop --no-deps``, so dependencies are installed
in the modern format.

The rest are more about providing more useful defaults. It is easy to forget
re-building ``egg-info`` when you modify metadata, so Setl tries to be
helpful. Nowadays people almost always want to build both sdist and wheel, so
Setl does it by default. The PyPA recommends against using ``setup.py upload``,
so Setl bundles it. Nothing rocket science.


Next Step
=========

Read the documentation for more!
