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
from stat import S_IRUSR, S_IWUSR, S_IRGRP, S_IROTH
from hamcrest import *
import unittest
import os
import getpass
from sync.file_system_comparer import FileProperties


class TestFileProperties(unittest.TestCase):

    def setUp(self):
        self.filename = "test_file"
        f = open(self.filename, 'w')
        f.write("testing")
        f.close()

    def tearDown(self):
        try:
            os.remove(self.filename)
        except OSError as e:
            if e.errno != 2:  # file doesn't exist
                raise e

    def test_GIVEN_file_WHEN_from_path_THEN_properties_set(self):
        props = FileProperties.from_path(self.filename, '')

        assert_that(props.file_path, is_(self.filename), "file path")
        assert_that(props.owner, is_(getpass.getuser()), "file path")

    def test_GIVEN_file_is_group_read_WHEN_from_path_THEN_properties_is_published_butnot_public(self):
        os.chmod(self.filename,  S_IRUSR | S_IWUSR | S_IRGRP)

        props = FileProperties.from_path(self.filename, os.curdir)

        assert_that(props.is_published, is_(True), "published")
        assert_that(props.is_public, is_(False), "public")

    def test_GIVEN_file_is_other_read_WHEN_from_path_THEN_properties_is_not_published_but_is_public(self):
        # this is a funny situation to be in
        os.chmod(self.filename,  S_IRUSR | S_IWUSR | S_IROTH)

        props = FileProperties.from_path(self.filename, '')

        assert_that(props.is_published, is_(False), "published")
        assert_that(props.is_public, is_(True), "public")

    def test_GIVEN_file_is_group_read_and_other_read_WHEN_from_path_THEN_properties_is_published_and_is_public(self):
        os.chmod(self.filename,  S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH)

        props = FileProperties.from_path(self.filename, None)

        assert_that(props.is_published, is_(True), "published")
        assert_that(props.is_public, is_(True), "public")

    def test_GIVEN_file_is_not_read_WHEN_from_path_THEN_properties_is_not_published_but_is_not_public(self):
        os.chmod(self.filename,  S_IRUSR | S_IWUSR)

        props = FileProperties.from_path(self.filename)

        assert_that(props.is_published, is_(False), "published")
        assert_that(props.is_public, is_(False), "public")
