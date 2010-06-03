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
"""ZCML directive handlers for browser resources

$Id$
"""
import os

from zope.component import queryUtility
from zope.component.interface import provideInterface
from zope.component.zcml import handler
from zope.configuration.exceptions import ConfigurationError
from zope.interface import Interface, implements, classProvides
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.security.checker import CheckerPublic, NamesChecker, Checker
from zope.security.proxy import Proxy

from zope.browserresource.directory import DirectoryResourceFactory
from zope.browserresource.file import File, FileResourceFactory
from zope.browserresource.i18nfile import I18nFileResourceFactory
from zope.browserresource.icon import IconViewFactory
from zope.browserresource.interfaces import IResourceFactory
from zope.browserresource.interfaces import IResourceFactoryFactory

allowed_names = ('GET', 'HEAD', 'publishTraverse', 'browserDefault',
                 'request', '__call__')

class ResourceFactoryWrapper(object):

    implements(IResourceFactory)
    classProvides(IResourceFactoryFactory)

    def __init__(self, factory, checker, name):
        self.__factory = factory
        self.__checker = checker
        self.__name = name

    def __call__(self, request):
        resource = self.__factory(request)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource
    

def resource(_context, name, layer=IDefaultBrowserLayer,
             permission='zope.Public', factory=None,
             file=None, image=None, template=None):

    if permission == 'zope.Public':
        permission = CheckerPublic

    checker = NamesChecker(allowed_names, permission)

    if (factory and (file or image or template)) or \
       (file and (factory or image or template)) or \
       (image and (factory or file or template)) or \
       (template and (factory or file or image)):
        raise ConfigurationError(
            "Must use exactly one of factory or file or image or template"
            " attributes for resource directives"
            )

    if image or template:
        import warnings
        warnings.warn_explicit(
            'The "template" and "image" attributes of resource '
            'directive are deprecated in favor of pluggable '
            'file resource factories based on file extensions. '
            'Use the "file" attribute instead.',
            DeprecationWarning,
            _context.info.file, _context.info.line)
        if image:
            file = image
        elif template:
            file = template

    _context.action(
        discriminator = ('resource', name, IBrowserRequest, layer),
        callable = resourceHandler,
        args = (name, layer, checker, factory, file, _context.info),
        )


def resourceHandler(name, layer, checker, factory, file, context_info):
    if factory is not None:
        factory = ResourceFactoryWrapper(factory, checker, name)
    else:
        ext = os.path.splitext(os.path.normcase(file))[1][1:]
        factory_factory = queryUtility(IResourceFactoryFactory, ext,
                                       FileResourceFactory)
        factory = factory_factory(file, checker, name)
    handler('registerAdapter', factory, (layer,), Interface, name, context_info)


def resourceDirectory(_context, name, directory, layer=IDefaultBrowserLayer,
                      permission='zope.Public'):
    if permission == 'zope.Public':
        permission = CheckerPublic

    checker = NamesChecker(allowed_names + ('__getitem__', 'get'),
                           permission)

    if not os.path.isdir(directory):
        raise ConfigurationError(
            "Directory %s does not exist" % directory
            )

    factory = DirectoryResourceFactory(directory, checker, name)
    _context.action(
        discriminator = ('resource', name, IBrowserRequest, layer),
        callable = handler,
        args = ('registerAdapter',
                factory, (layer,), Interface, name, _context.info),
        )


def icon(_context, name, for_, file=None, resource=None,
                  layer=IDefaultBrowserLayer, title=None,
                  width=16, height=16):

    iname = for_.getName()

    if title is None:
        title = iname
        if title.startswith('I'):
            title = title[1:] # Remove leading 'I'

    if file is not None and resource is not None:
        raise ConfigurationError(
            "Can't use more than one of file, and resource "
            "attributes for icon directives"
            )
    elif file is not None:
        resource = '-'.join(for_.__module__.split('.'))
        resource = "%s-%s-%s" % (resource, iname, name)
        ext = os.path.splitext(file)[1]
        if ext:
            resource += ext

        # give this module another name, so we can use the "resource" directive
        # in it that won't conflict with our local variable with the same name.
        from zope.browserresource import metaconfigure
        metaconfigure.resource(_context, file=file, name=resource, layer=layer)
    elif resource is None:
        raise ConfigurationError(
            "At least one of the file, and resource "
            "attributes for resource directives must be specified"
            )

    vfactory = IconViewFactory(resource, title, width, height)

    _context.action(
        discriminator = ('view', name, vfactory, layer),
        callable = handler,
        args = ('registerAdapter',
                vfactory, (for_, layer), Interface, name, _context.info)
        )

    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (for_.__module__+'.'+for_.getName(),
                for_)
        )


class I18nResource(object):

    type = IBrowserRequest
    default_allowed_attributes = '__call__'

    def __init__(self, _context, name=None, defaultLanguage='en',
                 layer=IDefaultBrowserLayer, permission=None):
        self._context = _context
        self.name = name
        self.defaultLanguage = defaultLanguage
        self.layer = layer
        self.permission = permission
        self.__data = {}

    def translation(self, _context, language, file=None, image=None):

        if file is not None and image is not None:
            raise ConfigurationError(
                "Can't use more than one of file, and image "
                "attributes for resource directives"
                )
        elif file is None and image is None:
            raise ConfigurationError(
                "At least one of the file, and image "
                "attributes for resource directives must be specified"
                )

        if image is not None:
            import warnings
            warnings.warn_explicit(
                'The "image" attribute of i18n-resource directive is '
                'deprecated in favor of simple files. Use the "file" '
                'attribute instead.',
                DeprecationWarning,
                _context.info.file, _context.info.line)
            file = image

        self.__data[language] = File(_context.path(file), self.name)


    def __call__(self, require = None):
        if self.name is None:
            return

        if self.defaultLanguage not in self.__data:
            raise ConfigurationError(
                "A translation for the default language (%s) "
                "must be specified" % self.defaultLanguage
                )

        permission = self.permission
        factory = I18nFileResourceFactory(self.__data, self.defaultLanguage)

        if permission:
            if require is None:
                require = {}

            if permission == 'zope.Public':
                permission = CheckerPublic

        if require:
            checker = Checker(require)

            factory = self._proxyFactory(factory, checker)

        self._context.action(
            discriminator = ('i18n-resource', self.name, self.type, self.layer),
            callable = handler,
            args = ('registerAdapter',
                    factory, (self.layer,), Interface, self.name,
                    self._context.info)
            )


    def _proxyFactory(self, factory, checker):
        def proxyView(request,
                      factory=factory, checker=checker):
            resource = factory(request)

            # We need this in case the resource gets unwrapped and
            # needs to be rewrapped
            resource.__Security_checker__ = checker

            return Proxy(resource, checker)

        return proxyView
