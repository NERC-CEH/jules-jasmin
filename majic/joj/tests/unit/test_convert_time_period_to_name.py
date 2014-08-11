"""
#header
"""
from joj.services.tests.base import BaseTest
from joj.utils import utils
from hamcrest import *


class TestTimPeriodToName(BaseTest):

    def setUp(self):
        pass

    def test_GIVEN_Yearly_constant_WHEN_convert_THEN_show_yearly(self):

        result = utils.convert_time_period_to_name(-2)

        assert_that(result, is_('Yearly'))

    def test_GIVEN_Monthly_constant_WHEN_convert_THEN_show_monthly(self):

        result = utils.convert_time_period_to_name(-1)

        assert_that(result, is_('Monthly'))

    def test_GIVEN_Daily_time_period_WHEN_convert_THEN_show_daily(self):

        result = utils.convert_time_period_to_name(24*60*60)

        assert_that(result, is_('Daily'))

    def test_GIVEN_Hourly_time_period_WHEN_convert_THEN_show_hourly(self):

        result = utils.convert_time_period_to_name(60*60)

        assert_that(result, is_('Hourly'))

    def test_GIVEN_Round_number_of_minutes_WHEN_convert_THEN_XX_minutes(self):
        minutes = 30
        result = utils.convert_time_period_to_name(minutes*60)

        assert_that(result, is_('Every {} minutes'.format(minutes)))

    def test_GIVEN_Round_number_of_second_not_minutes_WHEN_convert_THEN_XX_seconds(self):
        seconds = 100
        result = utils.convert_time_period_to_name(seconds)

        assert_that(result, is_('Every {} seconds'.format(seconds)))

    def test_GIVEN_0_WHEN_convert_THEN_unknown_time_period(self):
        seconds = 0
        result = utils.convert_time_period_to_name(seconds)

        assert_that(result, is_('Unknown time period'))

    def test_GIVEN_none_WHEN_convert_THEN_unknown_time_period(self):
        seconds = None
        result = utils.convert_time_period_to_name(seconds)

        assert_that(result, is_('Unknown time period'))