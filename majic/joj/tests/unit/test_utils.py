"""
#    Majic
#    Copyright (C) 2014  CEH
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
from hamcrest import is_, assert_that
from joj.services.tests.base import BaseTest
from joj.utils.utils import insert_before_file_extension


class TestUtils(BaseTest):

    def test_insert_before_file_extension(self):
        path = "/home/user/data/file.name.here.nc"
        string_to_insert = "_INSERTED_STRING"
        modified_path = insert_before_file_extension(path, string_to_insert)
        expected_result = "/home/user/data/file.name.here_INSERTED_STRING.nc"
        assert_that(modified_path, is_(expected_result))
