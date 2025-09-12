##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.cachedescriptors package
"""
import os

from setuptools import setup


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()


setup(
    name='zope.cachedescriptors',
    version='6.0',
    url='http://github.com/zopefoundation/zope.cachedescriptors',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.dev',
    license='ZPL-2.1',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
    ],
    description='Method and property caching decorators',
    keywords='persistent caching decorator method property',
    long_description=(
        read('README.rst')
        + '\n' +
        read('src', 'zope', 'cachedescriptors', 'property.rst')
        + '\n' +
        read('src', 'zope', 'cachedescriptors', 'method.rst')
        + '\n' +
        read('CHANGES.rst')),
    include_package_data=True,
    python_requires='>=3.9',
    install_requires=[
        'setuptools',
    ],
    extras_require={
        'test': [],
    },
    zip_safe=False,
)
