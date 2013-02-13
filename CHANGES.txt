=======
CHANGES
=======

4.0.1 (unreleased)
------------------

- Nothing changed yet.


4.0.0 (2013-02-13)
------------------

- Dropped support for Python 2.4 and 2.5.

- Added support for Python 3.2 and 3.3.


3.5.1 (2010-04-30)
------------------

- Removed undeclared testing dependency on zope.testing.

3.5.0 (2009-02-10)
------------------

- Remove dependency on ZODB by allowing to specify storage factory for
  ``zope.cachedescriptors.method.cachedIn`` which is now `dict` by default.
  If you need to use BTree instead, you must pass it as `factory` argument
  to the ``zope.cachedescriptors.method.cachedIn`` decorator.

- Remove zpkg-related file.

- Clean up package description and documentation a bit.

- Change package mailing list address to zope-dev at zope.org, as
  zope3-dev at zope.org is now retired.

3.4.0 (2007-08-30)
------------------

Initial release as an independent package
