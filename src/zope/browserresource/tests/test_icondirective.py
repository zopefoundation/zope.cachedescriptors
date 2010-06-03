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
"""Test Icon-Directive

$Id$
"""
import os
from StringIO import StringIO
from unittest import TestCase, main, makeSuite

from zope import component
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.interface import implements
from zope.publisher.browser import TestRequest
from zope.security.checker import ProxyFactory, CheckerPublic
from zope.security.interfaces import Forbidden
from zope.security.proxy import removeSecurityProxy
from zope.traversing.interfaces import IContainmentRoot
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.traversing.browser.interfaces import IAbsoluteURL

import zope.location.interfaces
import zope.browserresource
from zope.component.testfiles.views import IC
from zope.browserresource.tests import support
from zope.testing import cleanup


template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'
   i18n_domain='zope'
   >
   %s
   </configure>"""


request = TestRequest()

class Ob(object):
    implements(IC)

ob = Ob()
request._vh_root = support.site

def defineCheckers():
    # define the appropriate checker for a FileResource for these tests
    from zope.security.protectclass import protectName
    from zope.browserresource.file import FileResource
    protectName(FileResource, '__call__', 'zope.Public')


class Test(support.SiteHandler, cleanup.CleanUp, TestCase):

    def setUp(self):
        super(Test, self).setUp()
        XMLConfig('meta.zcml', zope.browserresource)()
        defineCheckers()
        component.provideAdapter(AbsoluteURL, (None, None), IAbsoluteURL)
        
    def test(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, request), name='zmi_icon'),
            None)

        import zope.browserresource.tests as p
        path = os.path.dirname(p.__file__)
        path = os.path.join(path, 'testfiles', 'test.gif')

        # Configure the icon and make sure we can render the resulting view:
        xmlconfig(StringIO(template % (
            '''
            <browser:icon name="zmi_icon"
                      for="zope.component.testfiles.views.IC"
                      file="%s" />
            ''' % path
            )))

        view = component.getMultiAdapter((ob, request), name='zmi_icon')
        rname = 'zope-component-testfiles-views-IC-zmi_icon.gif'
        self.assertEqual(
            view(),
            '<img src="http://127.0.0.1/@@/%s" alt="C" '
            'width="16" height="16" border="0" />'
            % rname)

        self.assertEqual(view.url(), 'http://127.0.0.1/@@/' + rname)

        # Make sure that the title attribute works
        xmlconfig(StringIO(template % (
            '''
            <browser:icon name="zmi_icon_w_title"
                      for="zope.component.testfiles.views.IC"
                      file="%s" title="click this!" />
            ''' % path
            )))

        view = component.getMultiAdapter(
            (ob, request), name='zmi_icon_w_title')
        rname = 'zope-component-testfiles-views-IC-zmi_icon_w_title.gif'
        self.assertEqual(
            view(),
            '<img src="http://127.0.0.1/@@/%s" alt="click this!" '
            'width="16" height="16" border="0" />'
            % rname)

        # Make sure that the width and height attributes work
        xmlconfig(StringIO(template % (
            '''
            <browser:icon name="zmi_icon_w_width_and_height"
                      for="zope.component.testfiles.views.IC"
                      file="%s"
                      width="20" height="12" />
            ''' % path
            )))

        view = component.getMultiAdapter((ob, request),
                                         name='zmi_icon_w_width_and_height')
        rname = ('zope-component-testfiles-views-IC-'
                 'zmi_icon_w_width_and_height.gif')
        self.assertEqual(
            view(),
            '<img src="http://127.0.0.1/@@/%s" alt="C" '
            'width="20" height="12" border="0" />'
            % rname)

        # Make sure that the image was installed as a resource:
        resource = ProxyFactory(component.getAdapter(request, name=rname))
        self.assertRaises(Forbidden, getattr, resource, '_testData')
        resource = removeSecurityProxy(resource)
        self.assertEqual(resource._testData(), open(path, 'rb').read())

    def testResource(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, request), name='zmi_icon'), None)

        import zope.browserresource.tests as p
        path = os.path.dirname(p.__file__)
        path = os.path.join(path, 'testfiles', 'test.gif')

        xmlconfig(StringIO(template % (
            '''
            <browser:resource name="zmi_icon_res"
                      file="%s" />
            <browser:icon name="zmi_icon"
                      for="zope.component.testfiles.views.IC"
                      resource="zmi_icon_res" />
            ''' % path
            )))

        view = component.getMultiAdapter((ob, request), name='zmi_icon')
        rname = "zmi_icon_res"
        self.assertEqual(
            view(),
            '<img src="http://127.0.0.1/@@/%s" alt="C" width="16" '
            'height="16" border="0" />'
            % rname)

        resource = ProxyFactory(component.getAdapter(request, name=rname))

        self.assertRaises(Forbidden, getattr, resource, '_testData')
        resource = removeSecurityProxy(resource)
        self.assertEqual(resource._testData(), open(path, 'rb').read())

    def testResourceErrors(self):
        self.assertEqual(
            component.queryMultiAdapter((ob, request), name='zmi_icon'), None)

        import zope.browserresource.tests as p
        path = os.path.dirname(p.__file__)
        path = os.path.join(path, 'testfiles', 'test.gif')

        config = StringIO(template % (
            '''
            <browser:resource name="zmi_icon_res"
                      file="%s" />
            <browser:icon name="zmi_icon"
                      for="zope.component.testfiles.views.IC"
                      file="%s"
                      resource="zmi_icon_res" />
            ''' % (path, path)
            ))
        self.assertRaises(ConfigurationError, xmlconfig, config)

        config = StringIO(template % (
            """
            <browser:icon name="zmi_icon"
                      for="zope.component.testfiles.views.IC"
                      />
            """
            ))
        self.assertRaises(ConfigurationError, xmlconfig, config)


def test_suite():
    return makeSuite(Test)
