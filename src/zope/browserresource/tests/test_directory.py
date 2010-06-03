##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Directory-based resources test

$Id$
"""
import os
from unittest import TestCase, main, makeSuite

from zope.publisher.interfaces import NotFound
from zope.proxy import isProxy
from zope.publisher.browser import TestRequest
from zope.security import proxy
from zope.security.checker import NamesChecker, ProxyFactory
from zope.interface import implements
from zope.location.interfaces import IContained
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.component import provideAdapter, provideUtility

from zope.testing import cleanup

from zope.browserresource.directory import \
     DirectoryResourceFactory, DirectoryResource
from zope.browserresource.file import FileResource
import zope.browserresource.tests as p
from zope.browserresource.tests import support

test_directory = os.path.dirname(p.__file__)

checker = NamesChecker(
    ('get', '__getitem__', 'request', 'publishTraverse')
    )

class Ob(object):
    implements(IContained)
    __parent__ = __name__ = None

ob = Ob()

class Test(support.SiteHandler, cleanup.CleanUp, TestCase):

    def setUp(self):
        super(Test, self).setUp()
        provideAdapter(AbsoluteURL, (None, None), IAbsoluteURL)

    def testNotFound(self):
        path = os.path.join(test_directory, 'testfiles')
        request = TestRequest()
        factory = DirectoryResourceFactory(path, checker, 'testfiles')
        resource = factory(request)
        self.assertRaises(NotFound, resource.publishTraverse,
                          resource.request, 'doesnotexist')
        self.assertRaises(NotFound, resource.get, 'doesnotexist')

    def testBrowserDefault(self):
        path = os.path.join(test_directory, 'testfiles')
        request = TestRequest()
        factory = DirectoryResourceFactory(path, checker, 'testfiles')
        resource = factory(request)
        view, next = resource.browserDefault(request)
        self.assertEquals(view(), '')
        self.assertEquals(next, ())

    def testGetitem(self):
        path = os.path.join(test_directory, 'testfiles')
        request = TestRequest()
        factory = DirectoryResourceFactory(path, checker, 'testfiles')
        resource = factory(request)
        self.assertRaises(KeyError, resource.__getitem__, 'doesnotexist')
        file = resource['test.txt']

    def testProxy(self):
        path = os.path.join(test_directory, 'testfiles')
        request = TestRequest()
        factory = DirectoryResourceFactory(path, checker, 'testfiles')
        resource = factory(request)
        file = ProxyFactory(resource['test.txt'])
        self.assert_(isProxy(file))

    def testURL(self):
        request = TestRequest()
        request._vh_root = support.site
        path = os.path.join(test_directory, 'testfiles')
        files = DirectoryResourceFactory(path, checker, 'test_files')(request)
        files.__parent__ = support.site
        file = files['test.gif']
        self.assertEquals(file(), 'http://127.0.0.1/@@/test_files/test.gif')

    def testURL2Level(self):
        request = TestRequest()
        request._vh_root = support.site
        ob.__parent__ = support.site
        ob.__name__ = 'ob'
        path = os.path.join(test_directory, 'testfiles')
        files = DirectoryResourceFactory(path, checker, 'test_files')(request)
        files.__parent__ = ob
        file = files['test.gif']
        self.assertEquals(file(), 'http://127.0.0.1/@@/test_files/test.gif')

    def testURL3Level(self):
        request = TestRequest()
        request._vh_root = support.site
        ob.__parent__ = support.site
        ob.__name__ = 'ob'
        path = os.path.join(test_directory, 'testfiles')
        files = DirectoryResourceFactory(path, checker, 'test_files')(request)
        files.__parent__ = ob
        file = files['test.gif']
        self.assertEquals(file(), 'http://127.0.0.1/@@/test_files/test.gif')
        subdir = files['subdir']
        self.assert_(proxy.isinstance(subdir, DirectoryResource))
        file = subdir['test.gif']
        self.assertEquals(file(),
                          'http://127.0.0.1/@@/test_files/subdir/test.gif')

    def testPluggableFactories(self):
        path = os.path.join(test_directory, 'testfiles')
        request = TestRequest()
        resource = DirectoryResourceFactory(path, checker, 'files')(request)

        class ImageResource(object):
            def __init__(self, image, request):
                pass

        class ImageResourceFactory(object):
            def __init__(self, path, checker, name):
                pass
            def __call__(self, request):
                return ImageResource(None, request)

        from zope.browserresource.interfaces import IResourceFactoryFactory
        provideUtility(ImageResourceFactory, IResourceFactoryFactory, 'gif')

        image = resource['test.gif']
        self.assert_(proxy.isinstance(image, ImageResource))

        file = resource['test.txt']
        self.assert_(proxy.isinstance(file, FileResource))

def test_suite():
    return makeSuite(Test)
