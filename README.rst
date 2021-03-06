====
Setl
====

.. image:: https://travis-ci.com/uranusjr/setl.svg?branch=master
    :target: https://travis-ci.com/uranusjr/setl
    :alt: Travis CI Status

.. image:: https://readthedocs.org/projects/setl/badge/?version=latest
    :target: https://setl.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

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
``pyproject.toml`` beside ``setup.py``, with the following content::

    [build-system]
    requires = ["setuptools>=43", "wheel"]

Command comparisons to Setuptools:

+------------------+-------------------------------------------------+
| Setl             | Setuptools approximation                        |
+==================+=================================================+
| ``setl develop`` | ``setup.py develop``                            |
+------------------+-------------------------------------------------+
| ``setl build``   | ``setup.py egg_info build``                     |
+------------------+-------------------------------------------------+
| ``setl publish`` | | ``setup.py egg_info build sdist bdist_wheel`` |
|                  | | ``twine upload``                              |
+------------------+-------------------------------------------------+


But Why?
========

The main difference is how build and runtime dependencies are installed.

Traditionally Setuptools projects use ``setup_requires``, but that has
`various problems <https://www.python.org/dev/peps/pep-0518/#id24>`__ and is
discouraged in favour of using PEP 518 to specify build time dependencies
instead. But Setuptools's project management commands do not handle PEP 518
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
to re-build ``egg-info`` when you modify metadata, so Setl tries to be
helpful. Nowadays people almost always want to build both sdist and wheel, so
Setl does it by default. The PyPA recommends against using ``setup.py upload``,
so Setl bundles Twine for uploading instead. Nothing rocket science.


Next Steps
==========

* Read the documentation_ for detailed command descriptions and inner workings.
* View the source_ and help contribute to the project.

.. _documentation: https://setl.readthedocs.io
.. _source: https://github.com/uranusjr/setl
