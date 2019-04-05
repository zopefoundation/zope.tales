import six
import unittest


class TestCase(unittest.TestCase):
    """Base test case for Python version compatibility."""

    if six.PY2:  # pragma: PY2
        # Avoid DeprecationWarning for assertRaisesRegexp on Python 3 while
        # coping with Python 2 not having the Regex spelling variant
        assertRaisesRegex = unittest.TestCase.assertRaisesRegexp
