##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""Resource interfaces

$Id$
"""
from zope.interface import Interface, Attribute


class IResource(Interface):

    request = Attribute('Request object that is requesting the resource')

    def __call__():
        """return the absolute URL of this resource."""

class IResourceFactory(Interface):
    
    def __call__(request):
        """Return an IResource object"""

class IResourceFactoryFactory(Interface):
    """A factory for IResourceFactory objects
    
    These factories are registered as named utilities that can be selected
    for creating resource factories in a pluggable way.
    
    Resource directories and browser:resource directive use these utilities
    to choose what resource to create, depending on the file extension, so
    third-party packages could easily plug-in additional resource types.
    
    """
    
    def __call__(path, checker, name):
        """Return an IResourceFactory"""
