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
"""Basic Page Template expression types.

$Id: expressions.py,v 1.1 2003/04/14 12:15:51 matth Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

import re, sys
from types import StringTypes

from zope.tales.tales import ExpressionEngine
from zope.tales.tales import CompilerError
from zope.tales.tales import RegistrationError
from zope.tales.tales import _valid_name, _parse_expr, NAME_RE, Undefined 
from zope.tales.pythonexpr import PythonExpr

Undefs = (Undefined, AttributeError, KeyError, TypeError, IndexError)

_marker = object()

def simpleTraverse(object, path_items, econtext):
    """Traverses a sequence of names, first trying attributes then items.
    """

    for name in path_items:
        next = getattr(object, name, _marker)
        if next is not _marker:
            object = next
        elif hasattr(object, '__getitem__'):
            object = object[name]
        else:
            raise NameError, name
    return object


class SubPathExpr:
    def __init__(self, path, traverser):
        self._path = path = str(path).strip().split('/')
        self._base = base = path.pop(0)
        self._traverser = traverser
        if not _valid_name(base):
            raise CompilerError, 'Invalid variable name "%s"' % base
        # Parse path
        self._dp = dp = []
        for i in range(len(path)):
            e = path[i]
            if e[:1] == '?' and _valid_name(e[1:]):
                dp.append((i, e[1:]))
        dp.reverse()

    def _eval(self, econtext,
              list=list, isinstance=isinstance):
        vars = econtext.vars
        path = self._path
        if self._dp:
            path = list(path) # Copy!
            for i, varname in self._dp:
                val = vars[varname]
                if isinstance(val, StringTypes):
                    path[i] = val
                else:
                    # If the value isn't a string, assume it's a sequence
                    # of path names.
                    path[i:i+1] = list(val)
        base = self._base
        if base == 'CONTEXTS':  # Special base name
            ob = econtext.contexts
        else:
            ob = vars[base]
        if isinstance(ob, DeferWrapper):
            ob = ob()
        if path:
            ob = self._traverser(ob, path, econtext)
        return ob



class PathExpr:
    """One or more subpath expressions, separated by '|'.
    """

    # _default_type_names contains the expression type names this
    # class is usually registered for.
    _default_type_names = (
        'standard',
        'path',
        'exists',
        'nocall',
        )

    def __init__(self, name, expr, engine, traverser=simpleTraverse):
        self._s = expr
        self._name = name
        paths = expr.split('|')
        self._subexprs = []
        add = self._subexprs.append
        for i in range(len(paths)):
            path = paths[i].lstrip()
            if _parse_expr(path):
                # This part is the start of another expression type,
                # so glue it back together and compile it.
                add(engine.compile('|'.join(paths[i:]).lstrip()))
                break
            add(SubPathExpr(path, traverser)._eval)

    def _exists(self, econtext):
        for expr in self._subexprs:
            try:
                expr(econtext)
            except Undefs:
                pass
            else:
                return 1
        return 0

    def _eval(self, econtext):
        for expr in self._subexprs[:-1]:
            # Try all but the last subexpression, skipping undefined ones.
            try:
                ob = expr(econtext)
            except Undefs:
                pass
            else:
                break
        else:
            # On the last subexpression allow exceptions through.
            ob = self._subexprs[-1](econtext)

        if self._name == 'nocall':
            return ob

        # Call the object if it is callable.
        if hasattr(ob, '__call__'):
            return ob()
        return ob

    def __call__(self, econtext):
        if self._name == 'exists':
            return self._exists(econtext)
        return self._eval(econtext)

    def __str__(self):
        return '%s expression (%s)' % (self._name, `self._s`)

    def __repr__(self):
        return '<PathExpr %s:%s>' % (self._name, `self._s`)



_interp = re.compile(r'\$(%(n)s)|\${(%(n)s(?:/[^}]*)*)}' % {'n': NAME_RE})

class StringExpr:
    def __init__(self, name, expr, engine):
        self._s = expr
        if '%' in expr:
            expr = expr.replace('%', '%%')
        self._vars = vars = []
        if '$' in expr:
            # Use whatever expr type is registered as "path".
            path_type = engine.getTypes()['path']
            parts = []
            for exp in expr.split('$$'):
                if parts: parts.append('$')
                m = _interp.search(exp)
                while m is not None:
                    parts.append(exp[:m.start()])
                    parts.append('%s')
                    vars.append(path_type(
                        'path', m.group(1) or m.group(2), engine))
                    exp = exp[m.end():]
                    m = _interp.search(exp)
                if '$' in exp:
                    raise CompilerError, (
                        '$ must be doubled or followed by a simple path')
                parts.append(exp)
            expr = ''.join(parts)
        self._expr = expr

    def __call__(self, econtext):
        vvals = []
        for var in self._vars:
            v = var(econtext)
            vvals.append(v)
        return self._expr % tuple(vvals)

    def __str__(self):
        return 'string expression (%s)' % `self._s`

    def __repr__(self):
        return '<StringExpr %s>' % `self._s`


class NotExpr:
    def __init__(self, name, expr, engine):
        self._s = expr = expr.lstrip()
        self._c = engine.compile(expr)

    def __call__(self, econtext):
        return int(not econtext.evaluateBoolean(self._c))

    def __repr__(self):
        return '<NotExpr %s>' % `self._s`


class DeferWrapper:
    def __init__(self, expr, econtext):
        self._expr = expr
        self._econtext = econtext

    def __str__(self):
        return str(self())

    def __call__(self):
        return self._expr(self._econtext)


class DeferExpr:
    def __init__(self, name, expr, compiler):
        self._s = expr = expr.lstrip()
        self._c = compiler.compile(expr)

    def __call__(self, econtext):
        return DeferWrapper(self._c, econtext)

    def __repr__(self):
        return '<DeferExpr %s>' % `self._s`


class SimpleModuleImporter:
    """Minimal module importer with no security."""
    def __getitem__(self, module):
        mod = __import__(module)
        path = module.split('.')
        for name in path[1:]:
            mod = getattr(mod, name)
        return mod
