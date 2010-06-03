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
"""Resource base class and AbsoluteURL adapter

$Id$
"""
from zope.component import adapts, getMultiAdapter, queryMultiAdapter
from zope.interface import implements, implementsOnly
from zope.location import Location
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.site.hooks import getSite
from zope.traversing.browser.interfaces import IAbsoluteURL
import zope.traversing.browser.absoluteurl

from zope.browserresource.interfaces import IResource


class Resource(Location):

    implements(IResource)

    def __init__(self, request):
        self.request = request

    def __call__(self):
        return str(getMultiAdapter((self, self.request), IAbsoluteURL))


class AbsoluteURL(zope.traversing.browser.absoluteurl.AbsoluteURL):

    implementsOnly(IAbsoluteURL)
    adapts(IResource, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _createUrl(self, baseUrl, name):
        return "%s/@@/%s" % (baseUrl, name)

    def __str__(self):
        name = self.context.__name__
        if name.startswith('++resource++'):
            name = name[12:]

        site = getSite()
        base = queryMultiAdapter((site, self.request), IAbsoluteURL,
            name="resource")
        if base is None:
            url = str(getMultiAdapter((site, self.request), IAbsoluteURL))
        else:
            url = str(base)

        return self._createUrl(url, name)
