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
"""File-based browser resources.

$Id$
"""

import os
import time
try:
    from email.utils import formatdate, parsedate_tz, mktime_tz
except ImportError: # python 2.4
    from email.Utils import formatdate, parsedate_tz, mktime_tz

from zope.contenttype import guess_content_type
from zope.interface import implements, classProvides
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.browserresource.resource import Resource
from zope.browserresource.interfaces import IResourceFactory
from zope.browserresource.interfaces import IResourceFactoryFactory


class File(object):
    
    def __init__(self, path, name):
        self.path = path
        self.__name__ = name

        f = open(path, 'rb')
        data = f.read()
        f.close()
        self.content_type = guess_content_type(path, data)[0]

        self.lmt = float(os.path.getmtime(path)) or time.time()
        self.lmh = formatdate(self.lmt, usegmt=True)


class FileResource(BrowserView, Resource):

    implements(IBrowserPublisher)

    cacheTimeout = 86400

    def publishTraverse(self, request, name):
        '''File resources can't be traversed further, so raise NotFound if
        someone tries to traverse it.
        
          >>> factory = FileResourceFactory(testFilePath, nullChecker, 'test.txt')
          >>> request = TestRequest()
          >>> resource = factory(request)
          >>> resource.publishTraverse(request, '_testData')
          Traceback (most recent call last):
          ...
          NotFound: Object: None, name: '_testData'

        '''
        raise NotFound(None, name)

    def browserDefault(self, request):
        '''Return a callable for processing browser requests.

          >>> factory = FileResourceFactory(testFilePath, nullChecker, 'test.txt')
          >>> request = TestRequest(REQUEST_METHOD='GET')
          >>> resource = factory(request)
          >>> view, next = resource.browserDefault(request)
          >>> view() == open(testFilePath, 'rb').read()
          True
          >>> next == ()
          True

          >>> request = TestRequest(REQUEST_METHOD='HEAD')
          >>> resource = factory(request)
          >>> view, next = resource.browserDefault(request)
          >>> view() == ''
          True
          >>> next == ()
          True
        
        '''
        return getattr(self, request.method), ()

    def chooseContext(self):
        '''Choose the appropriate context.
        
        This method can be overriden in subclasses, that need to choose
        appropriate file, based on current request or other condition,
        like, for example, i18n files.
        
        '''
        return self.context

    def GET(self):
        '''Return a file data for downloading with GET requests
        
          >>> factory = FileResourceFactory(testFilePath, nullChecker, 'test.txt')
          >>> request = TestRequest()
          >>> resource = factory(request)
          >>> resource.GET() ==  open(testFilePath, 'rb').read()
          True
          >>> request.response.getHeader('Content-Type') == 'text/plain'
          True
        
        Let's test If-Modified-Since header support.

          >>> timestamp = time.time()
        
          >>> file = factory._FileResourceFactory__file # get mangled file
          >>> file.lmt = timestamp
          >>> file.lmh = formatdate(timestamp, usegmt=True)

          >>> before = timestamp - 1000
          >>> request = TestRequest(HTTP_IF_MODIFIED_SINCE=formatdate(before, usegmt=True))
          >>> resource = factory(request)
          >>> bool(resource.GET())
          True

          >>> after = timestamp + 1000
          >>> request = TestRequest(HTTP_IF_MODIFIED_SINCE=formatdate(after, usegmt=True))
          >>> resource = factory(request)
          >>> bool(resource.GET())
          False
          >>> request.response.getStatus()
          304

        It won't fail on bad If-Modified-Since headers.

          >>> request = TestRequest(HTTP_IF_MODIFIED_SINCE='bad header')
          >>> resource = factory(request)
          >>> bool(resource.GET())
          True

        '''

        file = self.chooseContext()
        request = self.request
        response = request.response

        setCacheControl(response, self.cacheTimeout)

        # HTTP If-Modified-Since header handling. This is duplicated
        # from OFS.Image.Image - it really should be consolidated
        # somewhere...
        header = request.getHeader('If-Modified-Since', None)
        if header is not None:
            header = header.split(';')[0]
            # Some proxies seem to send invalid date strings for this
            # header. If the date string is not valid, we ignore it
            # rather than raise an error to be generally consistent
            # with common servers such as Apache (which can usually
            # understand the screwy date string as a lucky side effect
            # of the way they parse it).
            try:
                mod_since = long(mktime_tz(parsedate_tz(header)))
            except:
                mod_since = None
            if mod_since is not None:
                if getattr(file, 'lmt', None):
                    last_mod = long(file.lmt)
                else:
                    last_mod = 0L
                if last_mod > 0 and last_mod <= mod_since:
                    response.setStatus(304)
                    return ''

        response.setHeader('Content-Type', file.content_type)
        response.setHeader('Last-Modified', file.lmh)

        f = open(file.path,'rb')
        data = f.read()
        f.close()

        return data

    def HEAD(self):
        '''Return proper headers and no content for HEAD requests
        
          >>> factory = FileResourceFactory(testFilePath, nullChecker, 'test.txt')
          >>> request = TestRequest()
          >>> resource = factory(request)
          >>> resource.HEAD() == ''
          True
          >>> request.response.getHeader('Content-Type') == 'text/plain'
          True

        '''
        file = self.chooseContext()
        response = self.request.response
        response.setHeader('Content-Type', file.content_type)
        response.setHeader('Last-Modified', file.lmh)
        setCacheControl(response, self.cacheTimeout)
        return ''

    # for unit tests
    def _testData(self):
        f = open(self.context.path, 'rb')
        data = f.read()
        f.close()
        return data


def setCacheControl(response, secs=86400):
    # Cache for one day by default
    response.setHeader('Cache-Control', 'public,max-age=%s' % secs)
    t = time.time() + secs
    response.setHeader('Expires', formatdate(t, usegmt=True))


class FileResourceFactory(object):

    resourceClass = FileResource

    implements(IResourceFactory)
    classProvides(IResourceFactoryFactory)

    def __init__(self, path, checker, name):
        self.__file = File(path, name)
        self.__checker = checker
        self.__name = name

    def __call__(self, request):
        resource = self.resourceClass(self.__file, request)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource
