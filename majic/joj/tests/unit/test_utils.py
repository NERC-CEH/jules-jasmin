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

from joj.tests.base import BaseTest
from joj.utils.utils import insert_before_file_extension
from joj.utils.utils import extract_error_message_from_response

class TestUtils(BaseTest):

    def test_insert_before_file_extension(self):
        path = "/home/user/data/file.name.here.nc"
        string_to_insert = "_INSERTED_STRING"
        modified_path = insert_before_file_extension(path, string_to_insert)
        expected_result = "/home/user/data/file.name.here_INSERTED_STRING.nc"
        assert_that(modified_path, is_(expected_result))

    def test_extract_error_message_from_response(self):
        error_message = ("Error: <html> <head> <title>400 Bad Request</title> </head> <body> <h1>400 Bad Request</h1> "
                        "The server could not comply with the request since it is either malformed or otherwise "
                        "incorrect.<br /><br /> Problem submitting job, unrecognised format. </body> </html>")
        extracted_message = extract_error_message_from_response(error_message)
        expected_result = "Problem submitting job, unrecognised format."
        assert_that(extracted_message, is_(expected_result))

    def test_extract_error_message_from_response_with_unexpected_message(self):
        # The extract_error_message_from_response searches for a particular set of tags when filtering for the output.
        # This test looks at the case when those tags aren't present, and ensures that a sensible error message
        # is returned.
        error_message = ("Error: <html> <head> <title>400 Bad Request</title> </head> <body> "
                         " Problem submitting job, unrecognised format. </body> </html>")
        extracted_message = extract_error_message_from_response(error_message)
        expected_result = "Unknown error."
        assert_that(extracted_message, is_(expected_result))
