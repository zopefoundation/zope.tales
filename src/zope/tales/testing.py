import six
import unittest


class TestCase(unittest.TestCase):
    """Base test case for Python version compatibility."""

    if six.PY2:  # pragma: no cover
        # Avoid DeprecationWarning for assertRaisesRegexp on Python 3 while
        # coping with Python 2 not having the Regex spelling variant
        assertRaisesRegex = getattr(unittest.TestCase, 'assertRaisesRegex',
                                    unittest.TestCase.assertRaisesRegexp)
