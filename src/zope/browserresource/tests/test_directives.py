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
"""'browser' namespace directive tests

$Id$
"""

import os
import unittest
from cStringIO import StringIO

from zope import component
from zope.interface import Interface, implements, directlyProvides, providedBy

import zope.security.management
from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.configuration.exceptions import ConfigurationError
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces import IDefaultViewName
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserSkinType, IDefaultSkin
from zope.security.proxy import removeSecurityProxy, ProxyFactory
from zope.security.permission import Permission
from zope.security.interfaces import IPermission
from zope.traversing.adapters import DefaultTraversable
from zope.traversing.interfaces import ITraversable

import zope.publisher.defaultview
import zope.browserresource
from zope.component import provideAdapter, provideUtility
from zope.component.testfiles.views import R1, IV
from zope.browserresource.file import FileResource
from zope.browserresource.i18nfile import I18nFileResource
from zope.browserresource.directory import DirectoryResource
from zope.testing import cleanup

tests_path = os.path.join(
    os.path.dirname(zope.browserresource.__file__),
    'tests')

template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'
   i18n_domain='zope'>
   %s
   </configure>"""


request = TestRequest()

class ITestLayer(IBrowserRequest):
    """Test Layer."""

class ITestSkin(ITestLayer):
    """Test Skin."""


class MyResource(object):

    def __init__(self, request):
        self.request = request


class Test(cleanup.CleanUp, unittest.TestCase):

    def setUp(self):
        super(Test, self).setUp()
        XMLConfig('meta.zcml', zope.browserresource)()
        provideAdapter(DefaultTraversable, (None,), ITraversable)

    def tearDown(self):
        super(Test, self).tearDown()

    def testI18nResource(self):
        self.assertEqual(component.queryAdapter(request, name='test'), None)

        path1 = os.path.join(tests_path, 'testfiles', 'test.pt')
        path2 = os.path.join(tests_path, 'testfiles', 'test2.pt')

        xmlconfig(StringIO(template % (
            '''
            <browser:i18n-resource name="test" defaultLanguage="fr">
              <browser:translation language="en" file="%s" />
              <browser:translation language="fr" file="%s" />
            </browser:i18n-resource>
            ''' % (path1, path2)
            )))

        v = component.getAdapter(request, name='test')
        self.assertEqual(
            component.queryAdapter(request, name='test').__class__,
            I18nFileResource)
        self.assertEqual(v._testData('en'), open(path1, 'rb').read())
        self.assertEqual(v._testData('fr'), open(path2, 'rb').read())

        # translation must be provided for the default language
        config = StringIO(template % (
            '''
            <browser:i18n-resource name="test" defaultLanguage="fr">
              <browser:translation language="en" file="%s" />
              <browser:translation language="lt" file="%s" />
            </browser:i18n-resource>
            ''' % (path1, path2)
            ))
        self.assertRaises(ConfigurationError, xmlconfig, config)

    def testFactory(self):
        self.assertEqual(
            component.queryAdapter(request, name='index.html'), None)

        xmlconfig(StringIO(template %
            '''
            <browser:resource
                name="index.html"
                factory="
                  zope.browserresource.tests.test_directives.MyResource"
                />
            '''
            ))

        r = component.getAdapter(request, name='index.html')
        self.assertEquals(r.__class__, MyResource)
        r = ProxyFactory(r)
        self.assertEqual(r.__name__, "index.html")

    def testFile(self):
        path = os.path.join(tests_path, 'testfiles', 'test.pt')

        self.assertEqual(component.queryAdapter(request, name='test'), None)

        xmlconfig(StringIO(template %
            '''
            <browser:resource
                name="index.html"
                file="%s"
                />
            ''' % path
            ))

        r = component.getAdapter(request, name='index.html')
        self.assertTrue(isinstance(r, FileResource))
        r = ProxyFactory(r)
        self.assertEqual(r.__name__, "index.html")

        # Make sure we can access available attrs and not others
        for n in ('GET', 'HEAD', 'publishTraverse', 'request', '__call__'):
            getattr(r, n)

        self.assertRaises(Exception, getattr, r, '_testData')

        r = removeSecurityProxy(r)
        self.assertEqual(r._testData(), open(path, 'rb').read())


    def testPluggableFactory(self):

        class ImageResource(object):
            def __init__(self, image, request):
                pass

        class ImageResourceFactory(object):
            def __init__(self, path, checker, name):
                pass
            def __call__(self, request):
                return ImageResource(None, request)

        from zope.browserresource.interfaces import IResourceFactoryFactory
        component.provideUtility(ImageResourceFactory, IResourceFactoryFactory,
                                 name='gif')

        xmlconfig(StringIO(template %
            '''
            <browser:resource
                name="test.gif"
                file="%s"
                />
            ''' % os.path.join(tests_path, 'testfiles', 'test.gif')
            ))

        r = component.getAdapter(request, name='test.gif')
        self.assertTrue(isinstance(r, ImageResource))

    def testDirectory(self):
        path = os.path.join(tests_path, 'testfiles', 'subdir')

        self.assertEqual(component.queryAdapter(request, name='dir'), None)

        xmlconfig(StringIO(template %
            '''
            <browser:resourceDirectory
                name="dir"
                directory="%s"
                />
            ''' % path
            ))

        r = component.getAdapter(request, name='dir')
        self.assertTrue(isinstance(r, DirectoryResource))
        r = ProxyFactory(r)
        self.assertEqual(r.__name__, "dir")

        # Make sure we can access available attrs and not others
        for n in ('publishTraverse', 'browserDefault', 'request', '__call__',
                  'get', '__getitem__'):
            getattr(r, n)

        self.assertRaises(Exception, getattr, r, 'directory_factory')

        inexistent_dir = StringIO(template %
            '''
            <browser:resourceDirectory
                name="dir"
                directory="does-not-exist"
                />
            ''')

        self.assertRaises(ConfigurationError, xmlconfig, inexistent_dir)

    def test_SkinResource(self):
        self.assertEqual(component.queryAdapter(request, name='test'), None)

        path = os.path.join(tests_path, 'testfiles', 'test.pt')
        xmlconfig(StringIO(template % (
            '''
            <browser:resource
                name="test"
                file="%s"
                layer="
                  zope.browserresource.tests.test_directives.ITestLayer"
                />
            ''' % path
            )))

        self.assertEqual(component.queryAdapter(request, name='test'), None)

        r = component.getAdapter(TestRequest(skin=ITestSkin), name='test')
        self.assertEqual(r._testData(), open(path, 'rb').read())


def test_suite():
    return unittest.makeSuite(Test)
