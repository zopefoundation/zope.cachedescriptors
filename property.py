##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""Cached properties

See the CachedProperty class.

$Id$
"""
ncaches = 0l

class CachedProperty(object):
    """Cached Properties

    Cached properties are computed properties that cache their computed
    values.  They take into account instance attributes that they depend
    on, so when the instance attributes change, the properties will change
    the values they return.
    
    Cached properties cache their data in _v_ attributes, so they are
    also useful for managing the computation of volatile attributes for
    persistent objects.

    Example::

      from persistent import Persistent 
      from zope.cachedescriptors.property import CachedProperty

      class FileManager(Persistent):

         def __init__(self, filename):
             self.filename = filename

         def file(self):
             return open(self.filename)

         file = CachedProperty(file, 'filename')

      file_manager = FileManager('data.txt')

      x = file_manager.file.read(10)

    """

    def __init__(self, func, *names):
        global ncaches
        ncaches += 1
        self.data = (func, names,
                     "_v_cached_property_key_%s" % ncaches,
                     "_v_cached_property_value_%s" % ncaches)

    def __get__(self, inst, class_):
        if inst is None:
            return self

        func, names, key_name, value_name = self.data

        key = names and [getattr(inst, name) for name in names]
        value = getattr(inst, value_name, self)

        if value is not self:
            # We have a cached value
            if key == getattr(inst, key_name, self):
                # Cache is still good!
                return value
            
        # We need to compute and cache the value

        value = func(inst)
        setattr(inst, key_name, key)
        setattr(inst, value_name, value)
        
        return value
