"""
#header
"""
import datetime

from hamcrest import assert_that, is_

from joj.model import ParameterValue
from joj.tests.base import BaseTest


class TestParameterValue(BaseTest):

    def setUp(self):
        self.param_val = ParameterValue()

    def test_GIVEN_nothing_WHEN_set_python_datetime_THEN_value_set_to_fortran_datetime(self):
        value_py = datetime.datetime(1969, 7, 21, 20, 17, 0)
        value_ft = "'1969-07-21 20:17:00'"
        self.param_val.set_value_from_python(value_py)
        assert_that(self.param_val.value, is_(value_ft))

    def test_GIVEN_value_is_fortran_datetime_WHEN_get_value_THEN_returns_python_datetime(self):
        value_py = datetime.datetime(1969, 7, 21, 20, 17, 0)
        value_ft = "'1969-07-21 20:17:00'"
        self.param_val.value = value_ft
        assert_that(self.param_val.get_value_as_python(), is_(value_py))

    def test_GIVEN_nothing_WHEN_set_python_string_THEN_value_set_to_fortran_string(self):
        value_py = "String text"
        value_ft = "'String text'"
        self.param_val.set_value_from_python(value_py)
        assert_that(self.param_val.value, is_(value_ft))

    def test_GIVEN_value_is_fortran_string_WHEN_get_value_THEN_returns_python_string(self):
        value_py = "String text"
        value_ft = "'String text'"
        self.param_val.set_value_from_python(value_py)
        assert_that(self.param_val.value, is_(value_ft))

    def test_GIVEN_nothing_WHEN_set_python_list_THEN_value_set_to_fortran_list(self):
        value_py = [123.4, True, 100, datetime.datetime(1969, 7, 21, 20, 17, 0)]
        value_ft = "123.4    .true.    100    '1969-07-21 20:17:00'"
        self.param_val.set_value_from_python(value_py)
        assert_that(self.param_val.value, is_(value_ft))

    def test_GIVEN_value_is_fortran_list_WHEN_get_value_THEN_return_python_list(self):
        value_py = [123.4, 3e4, 100]
        value_ft = "123.4 3e4 100"
        self.param_val.value = value_ft
        assert_that(self.param_val.get_value_as_python(True), is_(value_py))