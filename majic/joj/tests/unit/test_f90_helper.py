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
import datetime

from hamcrest import assert_that, is_
import numpy

from joj.tests.base import BaseTest
from joj.utils import f90_helper


class TestF90HelperToPython(BaseTest):

    def test_GIVEN_string_WHEN_convert_THEN_string_returned(self):
        input = "'text string here'"
        output = f90_helper.f90_str_to_python(input)
        expected_output = 'text string here'
        assert_that(output, is_(expected_output))

    def test_GIVEN_string_list_WHEN_convert_THEN_string_returned(self):
        input = "'text string here'  'more string'"
        output = f90_helper.f90_str_to_python(input)
        expected_output = "text string here'  'more string"
        assert_that(output, is_(expected_output))

    def test_GIVEN_string_with_comma_WHEN_convert_THEN_string_returned(self):
        input = "'text string here', 'more string'"
        output = f90_helper.f90_str_to_python(input)
        expected_output = "text string here', 'more string"
        assert_that(output, is_(expected_output))

    def test_GIVEN_date_WHEN_convert_THEN_date_returned(self):
        date = datetime.datetime(2012, 1, 1, 0, 0, 0)
        datestr = date.strftime("%Y-%m-%d %X")
        input = "'" + datestr + "'"
        output = f90_helper.f90_str_to_python(input)
        expected_output = date
        assert_that(output, is_(expected_output))

    def test_GIVEN_bool_true_WHEN_convert_THEN_true_returned(self):
        input = '.true.'
        output = f90_helper.f90_str_to_python(input)
        assert isinstance(output, bool)
        assert output

    def test_GIVEN_bool_false_WHEN_convert_THEN_false_returned(self):
        input = '.false.'
        output = f90_helper.f90_str_to_python(input)
        assert isinstance(output, bool)
        assert (not output)

    def test_GIVEN_int_WHEN_convert_THEN_int_returned(self):
        input = '3600'
        output = f90_helper.f90_str_to_python(input)
        expected_output = 3600
        assert_that(output, is_(expected_output))
        assert isinstance(output, int)

    def test_GIVEN_float_WHEN_convert_THEN_float_returned(self):
        input = '3600.0'
        output = f90_helper.f90_str_to_python(input)
        expected_output = 3600.0
        assert_that(output, is_(expected_output))
        assert isinstance(output, float)

    def test_GIVEN_scientific_WHEN_convert_THEN_float_returned(self):
        input = '3E-4'
        output = f90_helper.f90_str_to_python(input)
        expected_output = 0.0003
        assert_that(output, is_(expected_output))
        assert isinstance(output, float)

    def test_GIVEN_list_of_ints_WHEN_convert_to_list_THEN_list_of_ints_returned(self):
        input = '2 4 6 8 10'
        output = f90_helper.f90_str_to_python(input, True)
        expected_output = [2, 4, 6, 8, 10]
        assert_that(output, is_(expected_output))

    def test_GIVEN_list_of_strings_WHEN_convert_to_list_THEN_list_of_strings_returned(self):
        input = "'str1'  'str2'  'str3'"
        output = f90_helper.f90_str_to_python(input, True)
        expected_output = ["str1", "str2", "str3"]
        assert_that(output, is_(expected_output))

    def test_GIVEN_list_of_bools_WHEN_convert_to_list_THEN_list_of_bools_returned(self):
        input = ".false.  F f FALSE .true.  T t TRUE"
        output = f90_helper.f90_str_to_python(input, True)
        expected_output = [False, False, False, False, True, True, True, True]
        assert_that(output, is_(expected_output))


class TestF90HelperToFortran(BaseTest):

    def test_GIVEN_string_WHEN_convert_THEN_string_returned(self):
        input = 'text string here'
        output = f90_helper.python_to_f90_str(input)
        expected_output = "'text string here'"
        assert_that(output, is_(expected_output))

    def test_GIVEN_date_WHEN_convert_THEN_date_returned(self):
        input = datetime.datetime(2012, 1, 1, 0, 0, 0)
        output = f90_helper.python_to_f90_str(input)
        expected_output = "'" + input.strftime("%Y-%m-%d %X") + "'"
        assert_that(output, is_(expected_output))

    def test_GIVEN_true_WHEN_convert_THEN_true_returned(self):
        input = True
        output = f90_helper.python_to_f90_str(input)
        expected_output = '.true.'
        assert_that(output, is_(expected_output))

    def test_GIVEN_false_WHEN_convert_THEN_false_returned(self):
        input = False
        output = f90_helper.python_to_f90_str(input)
        expected_output = '.false.'
        assert_that(output, is_(expected_output))

    def test_GIVEN_int_WHEN_convert_THEN_int_returned(self):
        input = 3600
        output = f90_helper.python_to_f90_str(input)
        expected_output = '3600'
        assert_that(output, is_(expected_output))

    def test_GIVEN_float_WHEN_convert_THEN_float_returned(self):
        input = 3600.0
        output = f90_helper.python_to_f90_str(input)
        expected_output = '3600.0'
        assert_that(output, is_(expected_output))

    def test_GIVEN_list_of_ints_WHEN_convert_to_list_THEN_list_of_ints_returned(self):
        input = [2, 4, 6, 8, 10]
        output = f90_helper.python_to_f90_str(input)
        expected_output = '2    4    6    8    10'
        assert_that(output, is_(expected_output))

    def test_GIVEN_list_of_strings_WHEN_convert_to_list_THEN_list_of_strings_returned(self):
        input = ["str1", "str2", "str3"]
        output = f90_helper.python_to_f90_str(input)
        expected_output = "'str1'    'str2'    'str3'"
        assert_that(output, is_(expected_output))

    def test_GIVEN_float32_WHEN_convert_THEN_float_returned(self):
        input = numpy.float32(3600.0)
        output = f90_helper.python_to_f90_str(input)
        expected_output = '3600.0'
        assert_that(output, is_(expected_output))
