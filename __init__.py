##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Cached descriptors

Cached descriptors cache their output.  They take into account
instance attributes that they depend on, so when the instance
attributes change, the descriptors will change the values they
return.

Cached descriptors cache their data in _v_ attributes, so they are
also useful for managing the computation of volatile attributes for
persistent objects.

Persistent descriptors:

  property

     A simple computed property

  method

     Idempotent method.  The return values are cached based on method
     arguments and on any instance attributes that the methods are
     defined to depend on.

     **Note**, methods haven't been implemented yet.

$Id$
"""
