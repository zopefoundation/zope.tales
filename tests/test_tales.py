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
import os
import sys
import unittest

from zope.tales import tales


class TALESTests(unittest.TestCase):

    def testIterator0(self):
        # Test sample Iterator class
        context = Harness()
        it = tales.Iterator('name', (), context)
        assert not it.next(), "Empty iterator"
        context._complete_()

    def testIterator1(self):
        # Test sample Iterator class
        context = Harness()
        it = tales.Iterator('name', (1,), context)
        context._assert_('setLocal', 'name', 1)
        assert it.next() and not it.next(), "Single-element iterator"
        context._complete_()

    def testIterator2(self):
        # Test sample Iterator class
        context = Harness()
        it = tales.Iterator('text', 'text', context)
        for c in 'text':
            context._assert_('setLocal', 'text', c)
        for c in 'text':
            assert it.next(), "Multi-element iterator"
        assert not it.next(), "Multi-element iterator"
        context._complete_()

    def testRegisterType(self):
        # Test expression type registration
        e = tales.ExpressionEngine()
        e.registerType('simple', tales.SimpleExpr)
        assert e.getTypes()['simple'] == tales.SimpleExpr

    def testRegisterTypeUnique(self):
        # Test expression type registration uniqueness
        e = tales.ExpressionEngine()
        e.registerType('simple', tales.SimpleExpr)
        try:
            e.registerType('simple', tales.SimpleExpr)
        except tales.RegistrationError:
            pass
        else:
            assert 0, "Duplicate registration accepted."

    def testRegisterTypeNameConstraints(self):
        # Test constraints on expression type names
        e = tales.ExpressionEngine()
        for name in '1A', 'A!', 'AB ':
            try:
                e.registerType(name, tales.SimpleExpr)
            except tales.RegistrationError:
                pass
            else:
                assert 0, 'Invalid type name "%s" accepted.' % name

    def testCompile(self):
        # Test expression compilation
        e = tales.ExpressionEngine()
        e.registerType('simple', tales.SimpleExpr)
        ce = e.compile('simple:x')
        assert ce(None) == ('simple', 'x'), (
            'Improperly compiled expression %s.' % `ce`)

    def testGetContext(self):
        # Test Context creation
        tales.ExpressionEngine().getContext()
        tales.ExpressionEngine().getContext(v=1)
        tales.ExpressionEngine().getContext(x=1, y=2)

    def getContext(self, **kws):
        e = tales.ExpressionEngine()
        e.registerType('simple', tales.SimpleExpr)
        return apply(e.getContext, (), kws)

    def testContext0(self):
        # Test use of Context
        se = self.getContext().evaluate('simple:x')
        assert se == ('simple', 'x'), (
            'Improperly evaluated expression %s.' % `se`)

    def testVariables(self):
        # Test variables
        ctxt = self.getContext()
        c = ctxt.vars
        ctxt.beginScope()
        ctxt.setLocal('v1', 1)
        ctxt.setLocal('v2', 2)

        assert c['v1'] == 1, 'Variable "v1"'

        ctxt.beginScope()
        ctxt.setLocal('v1', 3)
        ctxt.setGlobal('g', 1)

        assert c['v1'] == 3, 'Inner scope'
        assert c['v2'] == 2, 'Outer scope'
        assert c['g'] == 1, 'Global'

        ctxt.endScope()

        assert c['v1'] == 1, "Uncovered local"
        assert c['g'] == 1, "Global from inner scope"

        ctxt.endScope()


class Harness:
    def __init__(self):
        self.__callstack = []

    def _assert_(self, name, *args, **kwargs):
        self.__callstack.append((name, args, kwargs))

    def _complete_(self):
        assert len(self.__callstack) == 0, "Harness methods called"

    def __getattr__(self, name):
        cs = self.__callstack
        assert len(cs), 'Unexpected harness method call "%s".' % name
        assert cs[0][0] == name, (
            'Harness method name "%s" called, "%s" expected.' %
            (name, cs[0][0]) )
        return self._method_

    def _method_(self, *args, **kwargs):
        name, aargs, akwargs = self.__callstack.pop(0)
        assert aargs == args, "Harness method arguments"
        assert akwargs == kwargs, "Harness method keyword args"


def test_suite():
    return unittest.makeSuite(TALESTests)


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
