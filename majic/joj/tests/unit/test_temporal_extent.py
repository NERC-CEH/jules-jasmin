"""
#header
"""
import datetime

from joj.model.non_database.temporal_extent import TemporalExtent, InvalidTemporalExtent
from joj.tests.base import BaseTest


class TestTemporalExtent(BaseTest):

    def setUp(self):
        pass

    def test_GIVEN_bounds_WHEN_set_start_too_early_THEN_raise_InvalidTemporalExtent(self):
        start_bounds = datetime.datetime(2010, 1, 1, 0, 0, 0)
        end_bounds = datetime.datetime(2014, 1, 1, 0, 0, 0)
        temporal_extent = TemporalExtent(start_bounds, end_bounds)
        with self.assertRaises(InvalidTemporalExtent):
            start_time = datetime.datetime(2009, 1, 1, 0, 0, 0)
            temporal_extent.set_start(start_time)

    def test_GIVEN_bounds_WHEN_set_end_too_late_THEN_raise_InvalidTemporalExtent(self):
        start_bounds = datetime.datetime(2010, 1, 1, 0, 0, 0)
        end_bounds = datetime.datetime(2014, 1, 1, 0, 0, 0)
        temporal_extent = TemporalExtent(start_bounds, end_bounds)
        with self.assertRaises(InvalidTemporalExtent):
            end_time = datetime.datetime(2015, 1, 1, 0, 0, 0)
            temporal_extent.set_end(end_time)

    def test_GIVEN_bounds_WHEN_set_start_too_late_THEN_raise_InvalidTemporalExtent(self):
        start_bounds = datetime.datetime(2010, 1, 1, 0, 0, 0)
        end_bounds = datetime.datetime(2014, 1, 1, 0, 0, 0)
        temporal_extent = TemporalExtent(start_bounds, end_bounds)
        with self.assertRaises(InvalidTemporalExtent):
            end_time = datetime.datetime(2015, 1, 1, 0, 0, 0)
            temporal_extent.set_start(end_time)

    def test_GIVEN_bounds_WHEN_set_end_too_early_THEN_raise_InvalidTemporalExtent(self):
        start_bounds = datetime.datetime(2010, 1, 1, 0, 0, 0)
        end_bounds = datetime.datetime(2014, 1, 1, 0, 0, 0)
        temporal_extent = TemporalExtent(start_bounds, end_bounds)
        with self.assertRaises(InvalidTemporalExtent):
            start_time = datetime.datetime(2009, 1, 1, 0, 0, 0)
            temporal_extent.set_end(start_time)

    def test_GIVEN_bounds_WHEN_start_after_end_THEN_raise_InvalidTemporalExtent(self):
        start_bounds = datetime.datetime(2010, 1, 1, 0, 0, 0)
        end_bounds = datetime.datetime(2014, 1, 1, 0, 0, 0)
        temporal_extent = TemporalExtent(start_bounds, end_bounds)
        with self.assertRaises(InvalidTemporalExtent):
            start_time = datetime.datetime(2013, 1, 1, 0, 0, 0)
            end_time = datetime.datetime(2012, 1, 1, 0, 0, 0)
            temporal_extent.set_start(start_time)
            temporal_extent.set_end(end_time)

    def test_GIVEN_bounds_WHEN_both_extents_in_range_THEN_accepted(self):
        start_bounds = datetime.datetime(2010, 1, 1, 0, 0, 0)
        end_bounds = datetime.datetime(2014, 1, 1, 0, 0, 0)
        temporal_extent = TemporalExtent(start_bounds, end_bounds)
        start_time = datetime.datetime(2012, 1, 1, 0, 0, 0)
        end_time = datetime.datetime(2013, 1, 1, 0, 0, 0)
        temporal_extent.set_start(start_time)
        temporal_extent.set_end(end_time)