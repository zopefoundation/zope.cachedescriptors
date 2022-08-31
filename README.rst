===========================
 ``zope.cachedescriptors``
===========================

.. image:: https://img.shields.io/pypi/v/zope.cachedescriptors.svg
        :target: https://pypi.org/project/zope.cachedescriptors/
        :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/zope.cachedescriptors.svg
        :target: https://pypi.org/project/zope.cachedescriptors/
        :alt: Supported Python versions

.. image:: https://github.com/zopefoundation/zope.cachedescriptors/actions/workflows/tests.yml/badge.svg
        :target: https://github.com/zopefoundation/zope.cachedescriptors/actions/workflows/tests.yml

.. image:: https://readthedocs.org/projects/zopehookable/badge/?version=latest
        :target: http://zopehookable.readthedocs.io/en/latest/
        :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/zopefoundation/zope.cachedescriptors/badge.svg?branch=master
        :target: https://coveralls.io/github/zopefoundation/zope.cachedescriptors?branch=master

Cached descriptors cache their output.  They take into account
instance attributes that they depend on, so when the instance
attributes change, the descriptors will change the values they
return.

Cached descriptors cache their data in ``_v_`` attributes, so they are
also useful for managing the computation of volatile attributes for
persistent objects.

Persistent descriptors:

- ``property``

  A simple computed property.

  See ``src/zope/cachedescriptors/property.rst``.

- ``method``

  Idempotent method.  The return values are cached based on method
  arguments and on any instance attributes that the methods are
  defined to depend on.

  .. note::

     Only a cache based on arguments has been implemented so far.

  See ``src/zope/cachedescriptors/method.rst``.
