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
from datetime import datetime
import pytz
from hamcrest import *

from majic_web_service.tests import TestController
from majic_web_service.utils.general import convert_time_to_standard_string


class TestGetRunPropertiesController(TestController):

    def test_GIVEN_none_WHEN_convert_THEN_empty_string_returned(self):

        result = convert_time_to_standard_string(None)

        assert_that(result, is_(""))

    def test_GIVEN_datetime_WHEN_convert_THEN_date_time_is_returned(self):
        datetime_to_convert = datetime(2001, 2, 3, 4, 5, 6, tzinfo=pytz.utc)
        result = convert_time_to_standard_string(datetime_to_convert)

        assert_that(result, is_("2001-02-03 04:05:06 +0000"))

    def test_GIVEN_datetime_with_no_time_zone_WHEN_convert_THEN_date_time_is_returned_as_if_utc(self):
        datetime_to_convert = datetime(2001, 2, 3, 4, 5, 6)
        result = convert_time_to_standard_string(datetime_to_convert)

        assert_that(result, is_("2001-02-03 04:05:06 +0000"))