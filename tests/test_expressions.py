##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os, sys, unittest

from zope.tales.engine import Engine

class Data:

    def __init__(self, **kw):
        self.__dict__.update(kw)

    def __repr__(self): return self.name


def dict(**kw):
    return kw


class ExpressionTests(unittest.TestCase):

    def setUp(self):
        # Test expression compilation
        self.context = Data(
            vars = dict(
              x = Data(
                 name = 'xander',
                 y = Data(
                    name = 'yikes',
                    z = Data(name = 'zope')
                    )
                 ),
              y = Data(z = 3),
              b = 'boot',
              B = 2,
              )
            )


        self.engine = Engine

    def testSimple(self):
        expr = self.engine.compile('x')
        context=self.context
        self.assertEqual(expr(context), context.vars['x'])

    def testPath(self):
        expr = self.engine.compile('x/y')
        context=self.context
        self.assertEqual(expr(context), context.vars['x'].y)

    def testLongPath(self):
        expr = self.engine.compile('x/y/z')
        context=self.context
        self.assertEqual(expr(context), context.vars['x'].y.z)

    def testOrPath(self):
        expr = self.engine.compile('path:a|b|c/d/e')
        context=self.context
        self.assertEqual(expr(context), 'boot')

    def testString(self):
        expr = self.engine.compile('string:Fred')
        context=self.context
        self.assertEqual(expr(context), 'Fred')

    def testStringSub(self):
        expr = self.engine.compile('string:A$B')
        context=self.context
        self.assertEqual(expr(context), 'A2')

    def testStringSubComplex(self):
        expr = self.engine.compile('string:a ${x/y} b ${y/z} c')
        context=self.context
        self.assertEqual(expr(context), 'a yikes b 3 c')

    def testPython(self):
        expr = self.engine.compile('python: 2 + 2')
        context=self.context
        self.assertEqual(expr(context), 4)

    def testPythonNewline(self):
        expr = self.engine.compile('python: 2 \n+\n 2\n')
        context=self.context
        self.assertEqual(expr(context), 4)

def test_suite():
    return unittest.makeSuite(ExpressionTests)


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
