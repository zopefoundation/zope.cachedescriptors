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
"""File-based browser resource tests.

$Id$
"""
import os
import unittest
from zope.testing import cleanup, doctest

from zope.publisher.browser import TestRequest
from zope.security.checker import NamesChecker


def setUp(test):
    cleanup.setUp()
    data_dir = os.path.join(os.path.dirname(__file__), 'testfiles')

    test.globs['testFilePath'] = os.path.join(data_dir, 'test.txt')
    test.globs['nullChecker'] = NamesChecker()
    test.globs['TestRequest'] = TestRequest


def tearDown(test):
    cleanup.tearDown()

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(
            'zope.browserresource.file',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE),
        ))
