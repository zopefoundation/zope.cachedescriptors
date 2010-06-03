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
"""Resource URL access

$Id$
"""
from zope.component import queryAdapter
from zope.interface import implements
from zope.location import locate
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher

class Resources(BrowserView):
    """A view that can be traversed further to access browser resources
    
    This view is usually registered for zope.location.interfaces.ISite objects
    with no name, so resources will be available at <site>/@@/<resource>.

    Let's test how it's traversed to get registered resources. Let's create
    a sample resource class and register it.

      >>> from zope.component import provideAdapter
      >>> from zope.interface import Interface
      >>> from zope.publisher.interfaces import NotFound
      >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
      >>> from zope.publisher.browser import TestRequest

      >>> class Resource(object):
      ...     def __init__(self,request):
      ...         self.request = request
      ...     def __call__(self):
      ...         return 'http://localhost/testresource'
   
      >>> provideAdapter(Resource, (IDefaultBrowserLayer,), Interface, 'test')
    
    Now, create a site and request objects and get the Resources object to
    work with.
     
      >>> site = object()
      >>> request = TestRequest()
      >>> resources = Resources(site, request)

    Okay, let's test the publishTraverse method. It should traverse to our
    registered resource.

      >>> resource = resources.publishTraverse(request, 'test')
      >>> resource.__parent__ is site
      True
      >>> resource.__name__ == 'test'
      True
      >>> resource()
      'http://localhost/testresource'

    However, it will raise NotFound exception if we try to traverse to an
    unregistered resource.

      >>> resources.publishTraverse(request, 'does-not-exist')
      Traceback (most recent call last):
      ...
      NotFound: Object: <zope.browserresource.resources.Resources object at 0x...>,
                name: 'does-not-exist'
      
    When accessed without further traversing, it returns an empty page and no
    futher traversing steps.
    
      >>> view, path = resources.browserDefault(request)
      >>> view() == ''
      True
      >>> path == ()
      True

    The Resources view also provides __getitem__ method for use in templates.
    
      >>> resource = resources['test']
      >>> resource.__parent__ is site
      True
      >>> resource.__name__ == 'test'
      True
      >>> resource()
      'http://localhost/testresource'
    
    """

    implements(IBrowserPublisher)

    def publishTraverse(self, request, name):
        '''See zope.publisher.interfaces.browser.IBrowserPublisher interface'''
        resource = queryAdapter(request, name=name)
        if resource is None:
            raise NotFound(self, name)

        locate(resource, self.context, name)
        return resource

    def browserDefault(self, request):
        '''See zope.publisher.interfaces.browser.IBrowserPublisher interface'''
        return empty, ()

    def __getitem__(self, name):
        '''A helper method to make this view usable from templates,
        so resources can be acessed in template like context/@@/<resourcename>.
        '''
        return self.publishTraverse(self.request, name)


def empty():
    return ''
