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
import datetime as dt

from hamcrest import assert_that, is_

from joj.model import ModelRun
from joj.tests.base import BaseTest
from joj.utils import constants
from joj.utils import output_controller_helper


class TestOutputControllerHelper(BaseTest):

    def setUp(self):
        self.run_start = None
        self.run_end = None

        def _mock_get_python_parameter_value(param_namelist_name):
            if param_namelist_name == constants.JULES_PARAM_RUN_START:
                return self.run_start
            if param_namelist_name == constants.JULES_PARAM_RUN_END:
                return self.run_end

        self.model_run = ModelRun()
        self.model_run.get_python_parameter_value = _mock_get_python_parameter_value

    def test_GIVEN_run_with_no_jan_first_WHEN_is_yearly_allowed_THEN_False(self):
        self.run_start = dt.datetime(1901, 1, 5)
        self.run_end = dt.datetime(1901, 10, 1)

        yearly_allowed = output_controller_helper.yearly_output_allowed(self.model_run)
        assert_that(yearly_allowed, is_(False))

    def test_GIVEN_run_with_jan_first_WHEN_is_yearly_allowed_THEN_True(self):
        self.run_start = dt.datetime(1901, 12, 3)
        self.run_end = dt.datetime(1902, 10, 1)

        yearly_allowed = output_controller_helper.yearly_output_allowed(self.model_run)
        assert_that(yearly_allowed, is_(True))

    def test_GIVEN_run_with_no_first_of_month_WHEN_is_monthly_allowed_THEN_False(self):
        self.run_start = dt.datetime(1901, 1, 5)
        self.run_end = dt.datetime(1901, 1, 31)

        yearly_allowed = output_controller_helper.yearly_output_allowed(self.model_run)
        assert_that(yearly_allowed, is_(False))

    def test_GIVEN_run_with_first_of_month_WHEN_is_yearly_allowed_THEN_True(self):
        self.run_start = dt.datetime(1901, 12, 4)
        self.run_end = dt.datetime(1902, 1, 1)

        yearly_allowed = output_controller_helper.yearly_output_allowed(self.model_run)
        assert_that(yearly_allowed, is_(True))
