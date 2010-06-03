##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Resource Directory

A 'resource directory' is an on-disk directory which is registered as
a resource using the <resourceDirectory> ZCML directive.  The
directory is treated as a source for individual resources; it can be
traversed to retrieve resources represented by contained files, which
can in turn be treated as resources.  The contained files have
__name__ values which include a '/' separating the __name__ of the
resource directory from the name of the file within the directory.

$Id$
"""
import os

from zope.component import queryUtility
from zope.interface import implements, classProvides
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.browserresource.file import FileResourceFactory
from zope.browserresource.resource import Resource
from zope.browserresource.interfaces import IResourceFactory
from zope.browserresource.interfaces import IResourceFactoryFactory

_marker = object()

def empty():
    return ''

# we only need this class as a context for DirectoryResource
class Directory(object):

    def __init__(self, path, checker, name):
        self.path = path
        self.checker = checker
        self.__name__ = name

class DirectoryResource(BrowserView, Resource):

    implements(IBrowserPublisher)

    default_factory = FileResourceFactory
    directory_factory = None # this will be assigned later in the module

    def publishTraverse(self, request, name):
        '''See interface IBrowserPublisher'''
        return self.get(name)

    def browserDefault(self, request):
        '''See interface IBrowserPublisher'''
        return empty, ()

    def __getitem__(self, name):
        res = self.get(name, None)
        if res is None:
            raise KeyError(name)
        return res

    def get(self, name, default=_marker):
        path = self.context.path
        filename = os.path.join(path, name)
        isfile = os.path.isfile(filename)
        isdir = os.path.isdir(filename)

        if not (isfile or isdir):
            if default is _marker:
                raise NotFound(None, name)
            return default

        if isfile:
            ext = os.path.splitext(os.path.normcase(name))[1][1:]
            factory = queryUtility(IResourceFactoryFactory, ext,
                                   self.default_factory)
        else:
            factory = self.directory_factory

        rname = self.__name__ + '/' + name
        resource = factory(filename, self.context.checker, rname)(self.request)
        resource.__parent__ = self
        return resource


class DirectoryResourceFactory(object):

    implements(IResourceFactory)
    classProvides(IResourceFactoryFactory)

    factoryClass = DirectoryResource

    def __init__(self, path, checker, name):
        self.__dir = Directory(path, checker, name)
        self.__checker = checker
        self.__name = name

    def __call__(self, request):
        resource = self.factoryClass(self.__dir, request)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource

DirectoryResource.directory_factory = DirectoryResourceFactory
