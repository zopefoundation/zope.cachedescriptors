##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Test caching of properties.

$Id$
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.cachedescriptors.property import CachedProperty

class C(object):

    called0 = called1 = called2 = 0
    state1 = state2 = 0

    def get0(self):
        self.called0 += 1
        return self.called0

    def get1(self):
        self.called1 += 1
        return self.called1

    def get2(self):
        self.called2 += 1
        return self.called2

    p0 = CachedProperty(get0)
    p1 = CachedProperty(get1, 'state1')
    p2 = CachedProperty(get2, 'state1', 'state2')

class Test(TestCase):

    def test_no_parameters(self):
        c = C()
        self.assertEqual(c.p0, 1)
        self.assertEqual(c.called0, 1)
        self.assertEqual(c.p0, 1)
        self.assertEqual(c.called0, 1)

    def test_one_parameters(self):
        c = C()
        self.assertEqual(c.p1, 1)
        self.assertEqual(c.called1, 1)
        self.assertEqual(c.p1, 1)
        self.assertEqual(c.called1, 1)
        c.state2 += 1
        self.assertEqual(c.p1, 1)
        self.assertEqual(c.called1, 1)
        c.state1 += 1
        self.assertEqual(c.p1, 2)
        self.assertEqual(c.called1, 2)
        self.assertEqual(c.p1, 2)
        self.assertEqual(c.called1, 2)

    def test_multiple_parameters(self):
        c = C()
        self.assertEqual(c.p2, 1)
        self.assertEqual(c.called2, 1)
        self.assertEqual(c.p2, 1)
        self.assertEqual(c.called2, 1)
        c.x = 1
        self.assertEqual(c.p2, 1)
        self.assertEqual(c.called2, 1)
        c.state2 += 1
        self.assertEqual(c.p2, 2)
        self.assertEqual(c.called2, 2)
        self.assertEqual(c.p2, 2)
        self.assertEqual(c.called2, 2)
        c.state1 += 1
        self.assertEqual(c.p2, 3)
        self.assertEqual(c.called2, 3)
        self.assertEqual(c.p2, 3)
        self.assertEqual(c.called2, 3)
        c.state1 += 1
        c.state2 += 1
        self.assertEqual(c.p2, 4)
        self.assertEqual(c.called2, 4)
        self.assertEqual(c.p2, 4)
        self.assertEqual(c.called2, 4)

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
