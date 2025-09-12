=========
 Changes
=========

7.0 (2025-09-12)
================

- Replace ``pkg_resources`` namespace with PEP 420 native namespace.


6.1 (2025-02-14)
================

- Add support for Python 3.12, 3.13.

- Drop support for Python 3.7, 3.8.

- ``tales.Context.getValue`` now returns the innermost (not outermost)
  value for the given variable. Fixes
  `#19 <https://github.com/zopefoundation/zope.tales/issues/19>`_.


6.0 (2023-07-12)
================

- Drop support for Python 2.7, 3.5, 3.6.

- Add support for Python 3.11.


5.2 (2022-08-24)
================

- Add support for Python 3.9, 3.10.

- Fix error message raised if the first element of a path expression is not
  a valid name.


5.1 (2020-07-06)
================

- Packaging and test configuration cleanups.

- Improve `PathExpr` reusability
  Provide customizable support for the use of builtins in path expressions
  (`#23 <https://github.com/zopefoundation/zope.tales/issues/23>`_).


5.0.2 (2020-03-27)
==================

- Cleanups for Plone 5.2:

  * in path alternatives, whitespace can now surround ``|``,

  * non-ASCII in ``SubPathExpr`` now raises a ``CompilerError``
    (instead of a ``UnicodeEncodeError``; to be compatible with
    the ``chameleon`` template engine).


5.0.1 (2019-06-26)
==================

- Fix problem with list comprehensions not working in Python 3. This was due
  to the code not detecting variables used in side those expressions properly.


5.0 (2019-04-08)
================

- Drop support for Python 3.4.

- Fix test failures and deprecation warnings occurring when using Python 3.8a1.
  (`#15 <https://github.com/zopefoundation/zope.tales/pull/15>`_)

- Flake8 the code.


4.3 (2018-10-05)
================

- Add support for Python 3.7.

- Host documentation at https://zopetales.readthedocs.io

4.2.0 (2017-09-22)
==================

- Add support for Python 3.5 and 3.6.

- Drop support for Python 2.6, 3.2 and 3.3.

- Drop support for ``python setup.py test``.

- Reach 100% test coverage and maintain it via tox.ini and Travis CI.

4.1.1 (2015-06-06)
==================

- Add support for Python 3.2 and PyPy3.


4.1.0 (2014-12-29)
==================

.. note::

   Support for PyPy3 is pending release of a fix for:
   https://bitbucket.org/pypy/pypy/issue/1946

- Add support for Python 3.4.

- Add support for testing on Travis.


4.0.2 (2013-11-12)
==================

- Add missing ``six`` dependency


4.0.1 (2013-02-22)
==================

- Fix a previously untested Python 3.3 compatibility problem.


4.0.0 (2013-02-14)
==================

- Remove hard dependency on ``zope.tal``, which was already conditionalized
  but required via ``setup.py``.

- Add support for Python 3.3 and PyPy.

- Replace deprecated ``zope.interface.implements`` usage with equivalent
  ``zope.interface.implementer`` decorator.

- Drop support for Python 2.4 and 2.5.

- Fix documentation link in README.txt


3.5.2 (2012-05-23)
==================

- Subexpressions of a 'string:' expression can be only path expressions.
  https://bugs.launchpad.net/zope.tales/+bug/1002242


3.5.1 (2010-04-30)
==================

- Remove use of ``zope.testing.doctestunit`` in favor of stdlib's 'doctest.


3.5.0 (2010-01-01)
==================

- Port the lazy expression from ``Products.PageTemplates``.


3.4.0 (2007-10-03)
==================

- Update package setup.

- Initial release outside the Zope 3 trunk.


3.2.0 (2006-01-05)
==================

- Corresponds to the verison of the zope.tales package shipped as part of
  the Zope 3.2.0 release.

- Documentation / test fixes.


3.0.0 (2004-11-07)
==================

- Corresponds to the verison of the zope.tales package shipped as part of
  the Zope X3.0.0 release.
