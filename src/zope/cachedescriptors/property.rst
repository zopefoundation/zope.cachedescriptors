===================
 Cached Properties
===================

Cached properties are computed properties that cache their computed
values.  They take into account instance attributes that they depend
on, so when the instance attributes change, the properties will change
the values they return.

CachedProperty
==============

Cached properties cache their data in ``_v_`` attributes, so they are
also useful for managing the computation of volatile attributes for
persistent objects. Let's look at an example:

    >>> from zope.cachedescriptors import property
    >>> import math

    >>> class Point:
    ...
    ...     def __init__(self, x, y):
    ...         self.x, self.y = x, y
    ...
    ...     @property.CachedProperty('x', 'y')
    ...     def radius(self):
    ...         print('computing radius')
    ...         return math.sqrt(self.x**2 + self.y**2)

    >>> point = Point(1.0, 2.0)

If we ask for the radius the first time:

    >>> '%.2f' % point.radius
    computing radius
    '2.24'

We see that the radius function is called, but if we ask for it again:

    >>> '%.2f' % point.radius
    '2.24'

The function isn't called.  If we change one of the attribute the
radius depends on, it will be recomputed:

    >>> point.x = 2.0
    >>> '%.2f' % point.radius
    computing radius
    '2.83'

But changing other attributes doesn't cause recomputation:

    >>> point.q = 1
    >>> '%.2f' % point.radius
    '2.83'

Note that we don't have any non-volitile attributes added:

    >>> names = [name for name in point.__dict__ if not name.startswith('_v_')]
    >>> names.sort()
    >>> names
    ['q', 'x', 'y']

For backwards compatibility, the same thing can alternately be written
without using decorator syntax:

    >>> class Point:
    ...
    ...     def __init__(self, x, y):
    ...         self.x, self.y = x, y
    ...
    ...     def radius(self):
    ...         print('computing radius')
    ...         return math.sqrt(self.x**2 + self.y**2)
    ...     radius = property.CachedProperty(radius, 'x', 'y')

    >>> point = Point(1.0, 2.0)

If we ask for the radius the first time:

    >>> '%.2f' % point.radius
    computing radius
    '2.24'

We see that the radius function is called, but if we ask for it again:

    >>> '%.2f' % point.radius
    '2.24'

The function isn't called.  If we change one of the attribute the
radius depends on, it will be recomputed:

    >>> point.x = 2.0
    >>> '%.2f' % point.radius
    computing radius
    '2.83'

Documentation and the ``__name__`` are preserved if the attribute is accessed through
the class. This allows Sphinx to extract the documentation.

    >>> class Point:
    ...
    ...     def __init__(self, x, y):
    ...         self.x, self.y = x, y
    ...
    ...     @property.CachedProperty('x', 'y')
    ...     def radius(self):
    ...         '''The length of the line between self.x and self.y'''
    ...         print('computing radius')
    ...         return math.sqrt(self.x**2 + self.y**2)

    >>> print(Point.radius.__doc__)
    The length of the line between self.x and self.y
    >>> print(Point.radius.__name__)
    radius

It is possible to specify a CachedProperty that has no dependencies.
For backwards compatibility this can be written in a few different ways::

    >>> class Point:
    ...     def __init__(self, x, y):
    ...         self.x, self.y = x, y
    ...
    ...     @property.CachedProperty
    ...     def no_deps_no_parens(self):
    ...         print("No deps, no parens")
    ...         return 1
    ...
    ...     @property.CachedProperty()
    ...     def no_deps(self):
    ...         print("No deps")
    ...         return 2
    ...
    ...     def no_deps_old_style(self):
    ...         print("No deps, old style")
    ...         return 3
    ...     no_deps_old_style = property.CachedProperty(no_deps_old_style)


    >>> point = Point(1.0, 2.0)
    >>> point.no_deps_no_parens
    No deps, no parens
    1
    >>> point.no_deps_no_parens
    1
    >>> point.no_deps
    No deps
    2
    >>> point.no_deps
    2
    >>> point.no_deps_old_style
    No deps, old style
    3
    >>> point.no_deps_old_style
    3


Lazy Computed Attributes
========================

The `property` module provides another descriptor that supports a
slightly different caching model: lazy attributes.  Like cached
proprties, they are computed the first time they are used. however,
they aren't stored in volatile attributes and they aren't
automatically updated when other attributes change.  Furthermore, the
store their data using their attribute name, thus overriding
themselves. This provides much faster attribute access after the
attribute has been computed. Let's look at the previous example using
lazy attributes:

    >>> class Point:
    ...
    ...     def __init__(self, x, y):
    ...         self.x, self.y = x, y
    ...
    ...     @property.Lazy
    ...     def radius(self):
    ...         print('computing radius')
    ...         return math.sqrt(self.x**2 + self.y**2)

    >>> point = Point(1.0, 2.0)

If we ask for the radius the first time:

    >>> '%.2f' % point.radius
    computing radius
    '2.24'

We see that the radius function is called, but if we ask for it again:

    >>> '%.2f' % point.radius
    '2.24'

The function isn't called.  If we change one of the attribute the
radius depends on, it still isn't called:

    >>> point.x = 2.0
    >>> '%.2f' % point.radius
    '2.24'

If we want the radius to be recomputed, we have to manually delete it:

    >>> del point.radius

    >>> point.x = 2.0
    >>> '%.2f' % point.radius
    computing radius
    '2.83'

Note that the radius is stored in the instance dictionary:

    >>> '%.2f' % point.__dict__['radius']
    '2.83'

The lazy attribute needs to know the attribute name.  It normally
deduces the attribute name from the name of the function passed. If we
want to use a different name, we need to pass it:

    >>> def d(point):
    ...     print('computing diameter')
    ...     return 2*point.radius

    >>> Point.diameter = property.Lazy(d, 'diameter')
    >>> '%.2f' % point.diameter
    computing diameter
    '5.66'

Documentation and the ``__name__`` are preserved if the attribute is accessed through
the class. This allows Sphinx to extract the documentation.

    >>> class Point:
    ...
    ...     def __init__(self, x, y):
    ...         self.x, self.y = x, y
    ...
    ...     @property.Lazy
    ...     def radius(self):
    ...         '''The length of the line between self.x and self.y'''
    ...         print('computing radius')
    ...         return math.sqrt(self.x**2 + self.y**2)

    >>> print(Point.radius.__doc__)
    The length of the line between self.x and self.y
    >>> print(Point.radius.__name__)
    radius

The documentation of the attribute when accessed through the
instance will be the same as the return-value:

   >>> p = Point(1.0, 2.0)
   >>> p.radius.__doc__ == float.__doc__
   computing radius
   True

This is the same behaviour as the standard Python ``property``
decorator.

readproperty
============

readproperties are like lazy computed attributes except that the
attribute isn't set by the property:


    >>> class Point:
    ...
    ...     def __init__(self, x, y):
    ...         self.x, self.y = x, y
    ...
    ...     @property.readproperty
    ...     def radius(self):
    ...         print('computing radius')
    ...         return math.sqrt(self.x**2 + self.y**2)

    >>> point = Point(1.0, 2.0)

    >>> '%.2f' % point.radius
    computing radius
    '2.24'

    >>> '%.2f' % point.radius
    computing radius
    '2.24'

But you *can* replace the property by setting a value. This is the major
difference to the builtin `property`:

    >>> point.radius = 5
    >>> point.radius
    5

Documentation and the ``__name__`` are preserved if the attribute is accessed through
the class. This allows Sphinx to extract the documentation.

    >>> class Point:
    ...
    ...     def __init__(self, x, y):
    ...         self.x, self.y = x, y
    ...
    ...     @property.readproperty
    ...     def radius(self):
    ...         '''The length of the line between self.x and self.y'''
    ...         print('computing radius')
    ...         return math.sqrt(self.x**2 + self.y**2)

    >>> print(Point.radius.__doc__)
    The length of the line between self.x and self.y
    >>> print(Point.radius.__name__)
    radius

cachedIn
========

The `cachedIn` property allows to specify the attribute where to store the
computed value:

    >>> class Point:
    ...
    ...     def __init__(self, x, y):
    ...         self.x, self.y = x, y
    ...
    ...     @property.cachedIn('_radius_attribute')
    ...     def radius(self):
    ...         print('computing radius')
    ...         return math.sqrt(self.x**2 + self.y**2)

    >>> point = Point(1.0, 2.0)

    >>> '%.2f' % point.radius
    computing radius
    '2.24'

    >>> '%.2f' % point.radius
    '2.24'

The radius is cached in the attribute with the given name, `_radius_attribute`
in this case:

    >>> '%.2f' % point._radius_attribute
    '2.24'

When the attribute is removed the radius is re-calculated once. This allows
invalidation:

    >>> del point._radius_attribute

    >>> '%.2f' % point.radius
    computing radius
    '2.24'

    >>> '%.2f' % point.radius
    '2.24'

Documentation is preserved if the attribute is accessed through
the class. This allows Sphinx to extract the documentation.

    >>> class Point:
    ...
    ...     def __init__(self, x, y):
    ...         self.x, self.y = x, y
    ...
    ...     @property.cachedIn('_radius_attribute')
    ...     def radius(self):
    ...         '''The length of the line between self.x and self.y'''
    ...         print('computing radius')
    ...         return math.sqrt(self.x**2 + self.y**2)

    >>> print(Point.radius.__doc__)
    The length of the line between self.x and self.y
