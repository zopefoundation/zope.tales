##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Setup for zope.tales package

$Id$
"""

import os


try:
    from setuptools import setup, Extension
    
except ImportError, e:
    from distutils.core import setup, Extension

setup(name='zope.tales',
      version='3.3.2',

      url='http://svn.zope.org/zope.tales/tags/3.3.2',
      license='ZPL 2.1',
      description='Zope 3 Template Application Language Expression Syntax '
                  '(TALES)',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',

      packages=['zope', 'zope.tales'],
      package_dir = {'': 'src'},

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=['zope.interface', 'zope.tal'],
      include_package_data = True,

      zip_safe = False,
      )
    
