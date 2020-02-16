========
Commands
========

The Global ``--python`` Option
==============================

.. argparse::
   :ref: setl.cmds.get_parser
   :prog: setl
   :nodefault:
   :nosubcommands:

Setl is able to run "out of environment," i.e. does not need to be installed
into the same environment that builds the package. The interpreter is instead
passed in by the ``--python`` command. For example, the following command
builds the project against the command ``python2.7``::

    sefl --python=python2.7 build

The ``--python`` option accepts one of the followings:

* Absolute or relative path to a Python executable.
* Python command (``shutil.which`` is used to resolve).
* Python version specifier (the `Python launcher`_ is used to resolve).

.. _`Python launcher`: https://www.python.org/dev/peps/pep-0397/


Default Heuristic
-----------------

Setl tries to do the right thing if no ``--python`` value is explicitly given.
It looks for the following places, in this order:

* A non-empty environment variable ``SETL_PYTHON`` (interpreted with the same
  rules as ``--python``).
* If Setl is run in an activated virtual environment context, use that
  active environment's interpreter. (Setl detects the ``VIRTUAL_ENV``
  environment variable.)
* If Setl is *installed* inside a virtual environment, use the interpreter it
  is installed in (i.e. ``sys.executable``).

If all of the above checks fail, Setl will require an explicit ``--python``
value, or otherwise error out.

.. note:: The specified Python needs to have pip available.


Build Files
===========

.. argparse::
   :ref: setl.cmds.get_parser
   :prog: setl
   :path: build

Most of the flags have a direct ``setup.py build_*`` counterpart. ``--info``
corresponds to ``setup.py egg_info``.

If no flags are passed, Setl will run ``setup.py egg_info build`` to go through
all the build steps.


Install for Development
=======================

.. argparse::
   :ref: setl.cmds.get_parser
   :prog: setl
   :path: develop

Behaves very much like `setup.py develop`.


Build and Publish Distributions
===============================

.. argparse::
   :ref: setl.cmds.get_parser
   :prog: setl
   :path: publish
   :nodefault:

Builds distribution packages, and uploads them to a repository (package index).
The default is to upload to PyPI. Use the repository flags to change. For
example, this uploads the files to TestPyPI instead::

    setl publish --repository-url https://test.pypi.org/legacy/

Repository options are passed directly to Twine.


Clean up Built Files
====================

.. argparse::
   :ref: setl.cmds.get_parser
   :prog: setl
   :path: clean

Unlike ``setup.py clean``, this cleans up *all* the built files (except the
generated distributions). The in-tree ``.egg-info`` files associated to the
package is also removed.
