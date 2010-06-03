========
Overview
========

*This package is at present not reusable without depending on a large
chunk of the Zope Toolkit and its assumptions. It is maintained by the*
`Zope Toolkit project <http://docs.zope.org/zopetoolkit/>`_.

This package provides an implementation of browser resources. It also
provides directives for defining those resources using ZCML.

Resources are static files and directories that are served to the browser
directly from the filesystem. The most common example are images, CSS style
sheets, or JavaScript files.

Resources are be registered under a symbolic name and can later be referred to
by that name, so their usage is independent from their physical location.

You can register a single file with the `<browser:resource>` directive, and a
whole directory with the `<browser:resourceDirectory>` directive, for example

  <browser:resource
    file="/path/to/static.file"
    name="myfile"
    />

  <browser:resourceDirectory
    directory="/path/to/images"
    name="main-images"
    />

This causes a named adapter to be registered that adapts the request to
zope.interface.Interface (XXX why do we not use an explicit interface?),
so to later retrieve a resource, use
`zope.component.getAdapter(request, name='myfile')`.

There are two ways to traverse to a resource,

1. with the 'empty' view on a site, e. g. `http://localhost/@@/myfile`
   (This is declared by zope.browserresource)

2. with the `++resource++` namespace, e. g. `http://localhost/++resource++myfile`
   (This is declared by zope.traversing.namespace)

In case of resource-directories traversal simply continues through its contents,
e. g. `http://localhost/@@/main-images/subdir/sample.jpg`

Rather than putting together the URL to a resource manually, you should use
zope.traversing.browser.interfaces.IAbsoluteURL to get the URL, or for a
shorthand, call the resource object. This has an additional benefit:

If you want to serve resources from a different URL, for example
because you want to use a web server specialized in serving static files instead
of the appserver, you can register an IAbsoluteURL adapter for the site under
the name 'resource' that will be used to compute the base URLs for resources.

For example, if you register 'http://static.example.com/' as the base 'resource'
URL, the resources from the above example would yield the following absolute
URLs: http://static.example.com/@@/myfile and
http://static.example.com/@@/main-images
