##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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

from setuptools import setup, find_packages

setup(name='zope.tales',
      version = '3.4.0b1',

      url='http://svn.zope.org/zope.tales',
      license='ZPL 2.1',
      description='Zope 3 Template Application Language Expression Syntax '
                  '(TALES)',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',

      packages=find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages=['zope',],
      install_requires=['setuptools',
                        'zope.interface',
                        'zope.tal'],
      include_package_data = True,

      zip_safe = False,
      )
    
