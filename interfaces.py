##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Interface that describes the 'macros' attribute of a PageTemplate.

$Id: interfaces.py,v 1.1 2003/05/20 20:29:38 jim Exp $
"""

try:
    from zope import tal
except ImportError:
    tal = None

if tal is not None:
    from zope.tal.interfaces import ITALIterator

    class ITALESIterator(ITALIterator):
        """TAL Iterator provided by TALES

        Values of this iterator are assigned to items in the repeat namespace.

        For example, with a TAL statement like: tal:repeat="item items",
        an iterator will be assigned to "repeat/item".  The iterator
        provides a number of handy methods useful in writing TAL loops.
        """

        def number():
            """Return the position (starting with "1") within the iteration
            """

        def even():
            """Return whether the current position is even
            """

        def odd():
            """Return whether the current position is odd
            """

        def letter():
            """Return the position (starting with "a") within the iteration
            """

        def Letter():
            """Return the position (starting with "A") within the iteration
            """

        def roman():
            """Return the position (starting with "i") within the iteration
            """

        def Roman():
            """Return the position (starting with "I") within the iteration
            """

        def start():
            """Return whether the current position is the first position
            """

        def end():
            """Return whether the current position is the last position
            """

        def item():
            """Return whether the item at the current position
            """

        def length():
            """Return whether the length of the sequence

            Note that this may fail if the TAL iterator was created on a Python
            iterator.
            """
    
