=========
 Changes
=========

6.0 (2025-09-12)
================

- Replace ``pkg_resources`` namespace with PEP 420 native namespace.


5.1 (2025-02-14)
================

- Add support for Python 3.12, 3.13.

- Drop support for Python 3.7, 3.8.


5.0 (2023-03-27)
================

- Add support for Python 3.11.

- Drop support for Python 2.7, 3.5, 3.6.


4.4 (2022-09-07)
================

- Drop support for Python 3.4.

- Add support for Python 3.7, 3.8, 3.9, 3.10.


4.3.1 (2017-12-09)
==================

- Fix test which will break in the upcoming Python 3.7 release.


4.3.0 (2017-07-27)
==================

- Add support for Python 3.6.

- Drop support for Python 3.3.


4.2.0 (2016-09-05)
==================

- Add support for Python 3.5.

- Drop support for Python 2.6 and 3.2.

- The properties from the ``property`` module all preserve the
  documentation string of the underlying function, and all except
  ``cachedIn`` preserve everything that ``functools.update_wrapper``
  preserves.

- ``property.CachedProperty`` is usable as a decorator, with or
  without dependent attribute names.

- ``method.cachedIn`` preserves the documentation string of the
  underlying function, and everything else that ``functools.wraps`` preserves.

4.1.0 (2014-12-26)
==================

- Add support for PyPy and PyPy3.

- Add support for Python 3.4.

- Add support for testing on Travis.


4.0.0 (2013-02-13)
==================

- Drop support for Python 2.4 and 2.5.

- Add support for Python 3.2 and 3.3.


3.5.1 (2010-04-30)
==================

- Remove undeclared testing dependency on zope.testing.

3.5.0 (2009-02-10)
==================

- Remove dependency on ZODB by allowing to specify storage factory for
  ``zope.cachedescriptors.method.cachedIn`` which is now ``dict`` by default.
  If you need to use BTree instead, you must pass it as ``factory`` argument
  to the ``zope.cachedescriptors.method.cachedIn`` decorator.

- Remove zpkg-related file.

- Clean up package description and documentation a bit.

- Change package mailing list address to zope-dev at zope.org, as
  zope3-dev at zope.org is now retired.

3.4.0 (2007-08-30)
==================

Initial release as an independent package
