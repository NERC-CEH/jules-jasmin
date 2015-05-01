"""
#    Majic
#    Copyright (C) 2015  CEH
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import os
from setuptools import setup, find_packages


def read(fname):
    """
    # Utility function to read the README file.
    # Used for the long_description.  It's nice, because now 1) we have a top level
    # README file and 2) it's easier to type in the README file than to put a raw
    # string in below ...
    :param fname:
    :return: readme text
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="sync",
    version="0.0.1",
    author="Tessella Ltd.",
    author_email="majic@ceh.ac.uk",
    description="A utility to synchronise majic files onto an NFS server.",
    long_description=read('README'),
    classifiers=[
    ],
    install_requires=['requests', 'BeautifulSoup4'],
    tests_require=[
        "PyHamcrest",
        "Mock"
    ],
    setup_requires=[],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
)
