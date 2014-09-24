"""
header
"""
from hamcrest import assert_that, is_
from services.tests.base import BaseTest
import datetime as dt
from joj.utils.spinup_helper import SpinupHelper


class TestSpinupHelper(BaseTest):

    def setUp(self):
        self.spinup_helper = SpinupHelper()

    def test_GIVEN_run_starts_in_middle_of_driving_data_WHEN_calculate_start_THEN_start_5_years_before_run(self):
        driving_start = dt.datetime(1901, 1, 1)
        run_start = dt.datetime(1950, 1, 1)
        spin_start = self.spinup_helper.calculate_spinup_start(driving_start, run_start, 5)
        expected_spin_start = dt.datetime(1945, 1, 1)
        assert_that(spin_start, is_(expected_spin_start))

    def test_GIVEN_run_starts_at_beginning_of_driving_data_WHEN_calculate_start_THEN_start_is_driving_data_start(self):
        driving_start = dt.datetime(1901, 1, 1)
        run_start = dt.datetime(1901, 1, 1)
        spin_start = self.spinup_helper.calculate_spinup_start(driving_start, run_start, 5)
        assert_that(spin_start, is_(driving_start))

    def test_GIVEN_run_start_near_beginning_of_driving_data_WHEN_calculate_start_THEN_start_is_driving_data_start(self):
        driving_start = dt.datetime(1901, 1, 1)
        run_start = dt.datetime(1902, 1, 1)
        spin_start = self.spinup_helper.calculate_spinup_start(driving_start, run_start, 5)
        assert_that(spin_start, is_(driving_start))

    def test_GIVEN_driving_data_less_than_5_years_WHEN_calculate_start_THEN_start_is_driving_data_start(self):
        driving_start = dt.datetime(1901, 1, 1)
        run_start = dt.datetime(1901, 1, 1)
        spin_start = self.spinup_helper.calculate_spinup_start(driving_start, run_start, 5)
        assert_that(spin_start, is_(driving_start))

    def test_GIVEN_spin_start_in_middle_of_driving_data_WHEN_calculate_end_THEN_end_is_5_years_after_duration(self):
        spin_start = dt.datetime(1945, 1, 1)
        driving_end = dt.datetime(2001, 1, 1)
        spin_end = self.spinup_helper.calculate_spinup_end(spin_start, driving_end, 5)
        expected_end = dt.datetime(1950, 1, 1)
        assert_that(spin_end, is_(expected_end))

    def test_GIVEN_spin_start_near_end_of_driving_data_WHEN_calculate_end_THEN_end_is_driving_data_end(self):
        spin_start = dt.datetime(1999, 1, 1)
        driving_end = dt.datetime(2001, 1, 1)
        spin_end = self.spinup_helper.calculate_spinup_end(spin_start, driving_end, 5)
        assert_that(spin_end, is_(driving_end))

    def test_5_year_spinup_WHEN_get_number_cycles_THEN_returns_1(self):
        spin_start = dt.datetime(1945, 1, 1)
        spin_end = dt.datetime(1950, 1, 1)
        spin_cycles = self.spinup_helper.calculate_spinup_cycles(spin_start, spin_end, 5)
        assert_that(spin_cycles, is_(1))

    def test_1_year_spinup_WHEN_get_number_cycles_THEN_returns_5(self):
        spin_start = dt.datetime(1901, 1, 1)
        spin_end = dt.datetime(1902, 1, 1)
        spin_cycles = self.spinup_helper.calculate_spinup_cycles(spin_start, spin_end, 5)
        assert_that(spin_cycles, is_(5))

    def test_2_year_spinup_WHEN_get_number_cycles_THEN_returns_3(self):
        spin_start = dt.datetime(1901, 1, 1)
        spin_end = dt.datetime(1903, 1, 1)
        spin_cycles = self.spinup_helper.calculate_spinup_cycles(spin_start, spin_end, 5)
        assert_that(spin_cycles, is_(3))

    def test_2_and_half_year_spinup_WHEN_get_number_cycles_THEN_returns_2(self):
        spin_start = dt.datetime(1901, 1, 1)
        spin_end = dt.datetime(1903, 7, 3)
        spin_cycles = self.spinup_helper.calculate_spinup_cycles(spin_start, spin_end, 5)
        assert_that(spin_cycles, is_(2))

    def test_one_month_spinup_WHEN_get_number_cycles_THEN_returns_60(self):
        spin_start = dt.datetime(1901, 1, 1)
        spin_end = dt.datetime(1901, 1, 31, 21, 0)
        spin_cycles = self.spinup_helper.calculate_spinup_cycles(spin_start, spin_end, 5)
        assert_that(spin_cycles, is_(60))