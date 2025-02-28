##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""TALES

An implementation of a TAL expression engine
"""
import re
from html import escape

from zope.interface import Interface
from zope.interface import implementer

from zope.tales.interfaces import ITALESIterator


class ITALExpressionEngine(Interface):
    pass


class ITALExpressionCompiler(Interface):
    pass


class ITALExpressionErrorInfo(Interface):
    pass


try:
    # Override with real, if present
    from zope.tal.interfaces import ITALExpressionCompiler  # noqa: F811
    from zope.tal.interfaces import ITALExpressionEngine  # noqa: F811
    from zope.tal.interfaces import ITALExpressionErrorInfo  # noqa: F811
except ModuleNotFoundError:
    pass


NAME_RE = r"[a-zA-Z][a-zA-Z0-9_]*"
_parse_expr = re.compile(r"(%s):" % NAME_RE).match
_valid_name = re.compile('%s$' % NAME_RE).match


class TALESError(Exception):
    """Error during TALES evaluation"""


class Undefined(TALESError):
    """Exception raised on traversal of an undefined path."""


class CompilerError(Exception):
    """TALES Compiler Error"""


class RegistrationError(Exception):
    """Expression type or base name registration Error."""


_default = object()


@implementer(ITALESIterator)
class Iterator:
    """
    TALES Iterator.

    Default implementation of :class:`zope.tales.interfaces.ITALESIterator`.

    """

    def __init__(self, name, seq, context):
        """Construct an iterator

        Iterators are defined for a name, a sequence, or an iterator and a
        context, where a context simply has a setLocal method:

        >>> context = Context(ExpressionEngine(), {})
        >>> it = Iterator('foo', ("apple", "pear", "orange"), context)

        A local variable is not set until the iterator is used:

        >>> int("foo" in context.vars)
        0

        We can create an iterator on an empty sequence:

        >>> it = Iterator('foo', (), context)

        An iterator works as well:

        >>> it = Iterator('foo', {"apple":1, "pear":1, "orange":1}, context)
        >>> next(it)
        True

        >>> it = Iterator('foo', {}, context)
        >>> next(it)
        False

        >>> it = Iterator('foo', iter((1, 2, 3)), context)
        >>> next(it)
        True
        >>> next(it)
        True

        """

        self._seq = seq
        self._iter = i = iter(seq)
        self._nextIndex = 0
        self._name = name
        self._setLocal = context.setLocal

        # This is tricky. We want to know if we are on the last item,
        # but we can't know that without trying to get it. :(
        self._last = False
        try:
            self._next = next(i)
        except StopIteration:
            self._done = True
        else:
            self._done = False

    def __next__(self):
        """Advance the iterator, if possible.

        >>> context = Context(ExpressionEngine(), {})
        >>> it = Iterator('foo', ("apple", "pear", "orange"), context)
        >>> bool(next(it))
        True
        >>> context.vars['foo']
        'apple'
        >>> bool(next(it))
        True
        >>> context.vars['foo']
        'pear'
        >>> bool(next(it))
        True
        >>> context.vars['foo']
        'orange'
        >>> bool(next(it))
        False

        >>> it = Iterator('foo', {"apple":1, "pear":1, "orange":1}, context)
        >>> bool(next(it))
        True
        >>> bool(next(it))
        True
        >>> bool(next(it))
        True
        >>> bool(next(it))
        False

        >>> it = Iterator('foo', (), context)
        >>> bool(next(it))
        False

        >>> it = Iterator('foo', {}, context)
        >>> bool(next(it))
        False


        If we can advance, set a local variable to the new value.
        """
        # Note that these are *NOT* Python iterators!
        if self._done:
            return False
        self._item = v = self._next
        try:
            self._next = next(self._iter)
        except StopIteration:
            self._done = True
            self._last = True

        self._nextIndex += 1
        self._setLocal(self._name, v)
        return True

    def index(self):
        """Get the iterator index

        >>> context = Context(ExpressionEngine(), {})
        >>> it = Iterator('foo', ("apple", "pear", "orange"), context)
        >>> it.index()
        Traceback (most recent call last):
        ...
        TypeError: No iteration position
        >>> int(bool(next(it)))
        1
        >>> it.index()
        0
        >>> int(bool(next(it)))
        1
        >>> it.index()
        1
        >>> int(bool(next(it)))
        1
        >>> it.index()
        2
        """
        index = self._nextIndex - 1
        if index < 0:
            raise TypeError("No iteration position")
        return index

    def number(self):
        """Get the iterator position

        >>> context = Context(ExpressionEngine(), {})
        >>> it = Iterator('foo', ("apple", "pear", "orange"), context)
        >>> int(bool(next(it)))
        1
        >>> it.number()
        1
        >>> int(bool(next(it)))
        1
        >>> it.number()
        2
        >>> int(bool(next(it)))
        1
        >>> it.number()
        3
        """
        return self._nextIndex

    def even(self):
        """Test whether the position is even

        >>> context = Context(ExpressionEngine(), {})
        >>> it = Iterator('foo', ("apple", "pear", "orange"), context)
        >>> next(it)
        True
        >>> it.even()
        True
        >>> next(it)
        True
        >>> it.even()
        False
        >>> next(it)
        True
        >>> it.even()
        True
        """
        return not ((self._nextIndex - 1) % 2)

    def odd(self):
        """Test whether the position is odd

        >>> context = Context(ExpressionEngine(), {})
        >>> it = Iterator('foo', ("apple", "pear", "orange"), context)
        >>> next(it)
        True
        >>> it.odd()
        False
        >>> next(it)
        True
        >>> it.odd()
        True
        >>> next(it)
        True
        >>> it.odd()
        False
        """
        return bool((self._nextIndex - 1) % 2)

    def parity(self):
        """Return 'odd' or 'even' depending on the position's parity

        >>> context = Context(ExpressionEngine(), {})
        >>> it = Iterator('foo', ("apple", "pear", "orange"), context)
        >>> next(it)
        True
        >>> it.parity()
        'odd'
        >>> next(it)
        True
        >>> it.parity()
        'even'
        >>> next(it)
        True
        >>> it.parity()
        'odd'
        """
        if self._nextIndex % 2:
            return 'odd'
        return 'even'

    def letter(self, base=ord('a'), radix=26):
        """Get the iterator position as a lower-case letter

        >>> context = Context(ExpressionEngine(), {})
        >>> it = Iterator('foo', ("apple", "pear", "orange"), context)
        >>> it.letter()
        Traceback (most recent call last):
        ...
        TypeError: No iteration position
        >>> next(it)
        True
        >>> it.letter()
        'a'
        >>> next(it)
        True
        >>> it.letter()
        'b'
        >>> next(it)
        True
        >>> it.letter()
        'c'
        """
        index = self._nextIndex - 1
        if index < 0:
            raise TypeError("No iteration position")
        s = ''
        while 1:
            index, off = divmod(index, radix)
            s = chr(base + off) + s
            if not index:
                return s

    def Letter(self):
        """Get the iterator position as an upper-case letter

        >>> context = Context(ExpressionEngine(), {})
        >>> it = Iterator('foo', ("apple", "pear", "orange"), context)
        >>> next(it)
        True
        >>> it.Letter()
        'A'
        >>> next(it)
        True
        >>> it.Letter()
        'B'
        >>> next(it)
        True
        >>> it.Letter()
        'C'
        """
        return self.letter(base=ord('A'))

    def Roman(self, rnvalues=(
            (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
            (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
            (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I'))):
        """Get the iterator position as an upper-case roman numeral

        >>> context = Context(ExpressionEngine(), {})
        >>> it = Iterator('foo', ("apple", "pear", "orange"), context)
        >>> next(it)
        True
        >>> it.Roman()
        'I'
        >>> next(it)
        True
        >>> it.Roman()
        'II'
        >>> next(it)
        True
        >>> it.Roman()
        'III'
        """
        n = self._nextIndex
        s = ''
        for v, r in rnvalues:
            rct, n = divmod(n, v)
            s = s + r * rct
        return s

    def roman(self):
        """Get the iterator position as a lower-case roman numeral

        >>> context = Context(ExpressionEngine(), {})
        >>> it = Iterator('foo', ("apple", "pear", "orange"), context)
        >>> next(it)
        True
        >>> it.roman()
        'i'
        >>> next(it)
        True
        >>> it.roman()
        'ii'
        >>> next(it)
        True
        >>> it.roman()
        'iii'
        """
        return self.Roman().lower()

    def start(self):
        """Test whether the position is the first position

        >>> context = Context(ExpressionEngine(), {})
        >>> it = Iterator('foo', ("apple", "pear", "orange"), context)
        >>> next(it)
        True
        >>> it.start()
        True
        >>> next(it)
        True
        >>> it.start()
        False
        >>> next(it)
        True
        >>> it.start()
        False

        >>> it = Iterator('foo', {}, context)
        >>> it.start()
        False
        >>> next(it)
        False
        >>> it.start()
        False
        """
        return self._nextIndex == 1

    def end(self):
        """Test whether the position is the last position

        >>> context = Context(ExpressionEngine(), {})
        >>> it = Iterator('foo', ("apple", "pear", "orange"), context)
        >>> next(it)
        True
        >>> it.end()
        False
        >>> next(it)
        True
        >>> it.end()
        False
        >>> next(it)
        True
        >>> it.end()
        True

        >>> it = Iterator('foo', {}, context)
        >>> it.end()
        False
        >>> next(it)
        False
        >>> it.end()
        False
        """
        return self._last

    def item(self):
        """Get the iterator value

        >>> context = Context(ExpressionEngine(), {})
        >>> it = Iterator('foo', ("apple", "pear", "orange"), context)
        >>> it.item()
        Traceback (most recent call last):
        ...
        TypeError: No iteration position
        >>> next(it)
        True
        >>> it.item()
        'apple'
        >>> next(it)
        True
        >>> it.item()
        'pear'
        >>> next(it)
        True
        >>> it.item()
        'orange'

        >>> it = Iterator('foo', {1:2}, context)
        >>> next(it)
        True
        >>> it.item()
        1

        """
        if self._nextIndex == 0:
            raise TypeError("No iteration position")
        return self._item

    def length(self):
        """Get the length of the iterator sequence

        >>> context = Context(ExpressionEngine(), {})
        >>> it = Iterator('foo', ("apple", "pear", "orange"), context)
        >>> it.length()
        3

        You can even get the length of a mapping:

        >>> it = Iterator('foo', {"apple":1, "pear":2, "orange":3}, context)
        >>> it.length()
        3

        But you can't get the length of an iterable which doesn't
        support len():

        >>> class MyIter(object):
        ...     def __init__(self, seq):
        ...         self._iter = iter(seq)
        ...     def __iter__(self):
        ...         return self
        ...     def __next__(self):
        ...         return next(self._iter)
        ...     next = __next__
        >>> it = Iterator('foo', MyIter({"apple":1, "pear":2}), context)
        >>> try:
        ...     it.length()
        ... except TypeError:
        ...     pass
        ... else:
        ...     print('Expected TypeError')
        """
        return len(self._seq)


@implementer(ITALExpressionErrorInfo)
class ErrorInfo:
    """Information about an exception passed to an on-error handler."""

    # XXX: This is a duplicate of zope.tal.taldefs.ErrorInfo
    value = None

    def __init__(self, err, position=(None, None)):
        self.type = err
        if isinstance(err, Exception):
            self.type = err.__class__
            self.value = err

        self.lineno = position[0]
        self.offset = position[1]


@implementer(ITALExpressionCompiler)
class ExpressionEngine:
    """
    Expression compiler, an implementation of
    :class:`zope.tal.interfaces.ITALExpressionCompiler`.

    An instance of this class keeps :meth:`a mutable collection of
    expression type handlers
    <zope.tales.tales.ExpressionEngine.registerType>`.  It can compile
    expression strings by delegating to these handlers.  It can
    :meth:`provide an expression engine
    <zope.tales.tales.ExpressionEngine.getContext>`, which is capable
    of holding state and evaluating compiled expressions.

    By default, this object does not know how to compile any
    expression types.  See :data:`zope.tales.engine.Engine` and
    :func:`zope.tales.engine.DefaultEngine` for pre-configured
    instances supporting the standard expression types.
    """

    def __init__(self):
        self.types = {}
        self.base_names = {}
        self.namespaces = {}
        self.iteratorFactory = Iterator

    def registerFunctionNamespace(self, namespacename, namespacecallable):
        """
        Register a function namespace

        :param str namespace: a string containing the name of the namespace to
            be registered

        :param callable namespacecallable: a callable object which takes the
            following parameter:

            :context: the object on which the functions
                    provided by this namespace will
                    be called

            This callable should return an object which
            can be traversed to get the functions provided
            by the this namespace.

        For example::

           class stringFuncs(object):

              def __init__(self,context):
                 self.context = str(context)

              def upper(self):
                 return self.context.upper()

              def lower(self):
                 return self.context.lower()

            engine.registerFunctionNamespace('string', stringFuncs)
        """
        self.namespaces[namespacename] = namespacecallable

    def getFunctionNamespace(self, namespacename):
        """ Returns the function namespace """
        return self.namespaces[namespacename]

    def registerType(self, name, handler):
        """
        Register an expression of *name* to be handled with *handler*.

        :raises RegistrationError: If this is a duplicate registration for
            *name*, or if *name* is not a valid expression type name.
        """
        if not _valid_name(name):
            raise RegistrationError(
                'Invalid expression type name "%s".' % name)
        types = self.types
        if name in types:
            raise RegistrationError(
                'Multiple registrations for Expression type "%s".' % name)
        types[name] = handler

    def getTypes(self):
        return self.types

    def registerBaseName(self, name, object):
        if not _valid_name(name):
            raise RegistrationError('Invalid base name "%s".' % name)
        base_names = self.base_names
        if name in base_names:
            raise RegistrationError(
                'Multiple registrations for base name "%s".' % name)
        base_names[name] = object

    def getBaseNames(self):
        return self.base_names

    def compile(self, expression):
        m = _parse_expr(expression)
        if m:
            type = m.group(1)
            expr = expression[m.end():]
        else:
            type = "standard"
            expr = expression
        try:
            handler = self.types[type]
        except KeyError:
            raise CompilerError('Unrecognized expression type "%s".' % type)
        return handler(type, expr, self)

    def getContext(self, contexts=None, **kwcontexts):
        """
        Return a new expression engine.

        The keyword arguments passed in *kwcantexts* become the default
        variable context for the returned engine. If *contexts* is given, it
        should be a mapping, and the values it contains will override
        the keyword arguments.

        :rtype: Context
        """
        if contexts is not None:
            if kwcontexts:
                kwcontexts.update(contexts)
            else:
                kwcontexts = contexts
        return Context(self, kwcontexts)

    def getCompilerError(self):
        return CompilerError


@implementer(ITALExpressionEngine)
class Context:
    """
    Expression engine, an implementation of
    :class:`zope.tal.interfaces.ITALExpressionEngine`.

    This class is called ``Context`` because an instance of this class
    holds context information (namespaces) that it uses when evaluating
    compiled expressions.
    """
    position = (None, None)
    source_file = None

    def __init__(self, engine, contexts):
        """
        :param engine: A :class:`ExpressionEngine` (a
            :class:`zope.tal.interfaces.ITALExpressionCompiler`)
        :param contexts: A mapping (namespace) of variables that forms the base
            variable scope.
        """
        self._engine = engine
        self.contexts = contexts
        self.setContext('nothing', None)
        self.setContext('default', _default)

        self.repeat_vars = rv = {}
        # Wrap this, as it is visible to restricted code
        self.setContext('repeat', rv)
        self.setContext('loop', rv)  # alias

        self.vars = vars = contexts.copy()
        self._vars_stack = [vars]

        # Keep track of what needs to be popped as each scope ends.
        self._scope_stack = []

    def setContext(self, name, value):
        """Hook to allow subclasses to do things like adding security proxies.
        """
        self.contexts[name] = value

    def beginScope(self):
        self.vars = vars = self.vars.copy()
        self._vars_stack.append(vars)
        self._scope_stack.append([])

    def endScope(self):
        self._vars_stack.pop()
        self.vars = self._vars_stack[-1]

        scope = self._scope_stack.pop()
        # Pop repeat variables, if any
        i = len(scope)
        while i:
            i = i - 1
            name, value = scope[i]
            if value is None:
                del self.repeat_vars[name]
            else:
                self.repeat_vars[name] = value

    def setLocal(self, name, value):
        self.vars[name] = value

    def setGlobal(self, name, value):
        for vars in self._vars_stack:
            vars[name] = value

    def getValue(self, name, default=None):
        """return the current value of variable *name* or *default*."""
        # ``beginScope`` puts a copy of all variables into ``vars``
        #  and pushes it onto ``_vars_stack``,
        # ``endScope`` pops the last element of ``vars_stack`` into ``vars``,
        # ``setGlobal`` updates all variable bindings in ``_vars_stack``
        # (and thereby, implicitly, ``vars``).
        # Consequently, the current value of a variable can
        # always be found in ``vars``
        # (no need to iterate over ``_vars_stack``).
        return self.vars.get(name, default)

    def setRepeat(self, name, expr):
        expr = self.evaluate(expr)
        if not expr:
            return self._engine.iteratorFactory(name, (), self)
        it = self._engine.iteratorFactory(name, expr, self)
        old_value = self.repeat_vars.get(name)
        self._scope_stack[-1].append((name, old_value))
        self.repeat_vars[name] = it
        return it

    def evaluate(self, expression):
        """
        Evaluate the *expression* by calling it, passing in this object,
        and return the raw results.

        If *expression* is a string, it is first compiled.
        """
        if isinstance(expression, str):
            expression = self._engine.compile(expression)
        __traceback_supplement__ = (
            TALESTracebackSupplement, self, expression)
        return expression(self)

    evaluateValue = evaluate

    def evaluateBoolean(self, expr):
        """
        Evaluate the expression and return the boolean value of its result.
        """
        # "not not", while frowned upon by linters might be faster
        # than bool() because it avoids a builtin lookup. Plus it can't be
        # reassigned.
        return not not self.evaluate(expr)

    def evaluateText(self, expr):
        text = self.evaluate(expr)
        if text is self.getDefault() or text is None:
            return text
        if isinstance(text, str):
            # text could already be something text-ish, e.g. a Message object
            return text
        return str(text)

    evaluateStructure = evaluate

    # TODO: Should return None or a macro definition
    evaluateMacro = evaluate

    def createErrorInfo(self, err, position):
        return ErrorInfo(err, position)

    def getDefault(self):
        return _default

    def setSourceFile(self, source_file):
        self.source_file = source_file

    def setPosition(self, position):
        self.position = position

    def translate(self, msgid, domain=None, mapping=None, default=None):
        # custom Context implementations are supposed to customize
        # this to call whichever translation routine they want to use
        return str(msgid)


class TALESTracebackSupplement:
    """Implementation of zope.exceptions.ITracebackSupplement"""

    def __init__(self, context, expression):
        self.context = context
        self.source_url = context.source_file
        self.line = context.position[0]
        self.column = context.position[1]
        self.expression = repr(expression)

    def getInfo(self, as_html=0):
        import pprint
        data = self.context.contexts.copy()
        if 'modules' in data:
            del data['modules']  # the list is really long and boring
        s = pprint.pformat(data)
        if not as_html:
            return '   - Names:\n      %s' % s.replace('\n', '\n      ')

        return '<b>Names:</b><pre>%s</pre>' % (escape(s))
