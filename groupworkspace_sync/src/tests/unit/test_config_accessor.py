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
import ConfigParser

from hamcrest import *
import unittest
from sync.utils.config_accessor import ConfigAccessor


class TestConfigAccessor(unittest.TestCase):

    def setUp(self):
        self.config = ConfigParser.SafeConfigParser()
        self.accessor = ConfigAccessor(self.config)
        self.section = "section"
        self.option = "option"
        self.value = "value"
        self.config.add_section(self.section)
        self.config.set(self.section, self.option, self.value)

    def test_GIVEN_valid_value_and_section_WHEN_get_THEN_value_returned(self):
        result = self.accessor.get(self.option, self.section)

        assert_that(result, is_(self.value))

    def test_GIVEN_valid_value_and_invalid_section_WHEN_get_THEN_exception(self):

        assert_that(
            calling(self.accessor.get).with_args(self.value, "blah"),
            raises(ConfigParser.NoSectionError))

    def test_GIVEN_invalid_value_and_valid_section_WHEN_get_THEN_exception(self):

        assert_that(
            calling(self.accessor.get).with_args("blah", self.section),
            raises(ConfigParser.NoOptionError))

    def test_GIVEN_invalid_section_WHEN_set_section_THEN_raise_error(self):
        assert_that(
            calling(self.accessor.set_section).with_args("blah"),
            raises(ConfigParser.NoSectionError))

    def test_GIVEN_no_value_and_default_specified_WHEN_get_THEN_default(self):

        result = self.accessor.get("blah", self.section, default=self.value)

        assert_that(result, is_(self.value))

    def test_GIVEN_no_section_specified_but_section_set_WHEN_get_THEN_value(self):
        self.accessor.set_section(self.section)

        result = self.accessor.get(self.option)

        assert_that(result, is_(self.value))

    def test_GIVEN_no_section_specified_and_section_not_set_WHEN_get_THEN_error(self):

        assert_that(
            calling(self.accessor.get).with_args(self.option),
            raises(ConfigParser.NoSectionError))

    def test_GIVEN_no_section_specified_and_section_not_set_but_has_default_WHEN_get_THEN_error(self):

        assert_that(
            calling(self.accessor.get).with_args(self.option, default=self.value),
            raises(ConfigParser.NoSectionError))


if __name__ == '__main__':
    unittest.main()
