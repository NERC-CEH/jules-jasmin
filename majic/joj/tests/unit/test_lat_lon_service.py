"""
header
"""
from hamcrest import assert_that, is_
from joj.services.tests.base import BaseTest
from services.lat_lon_service import LatLonService


class TestLatLonService(BaseTest):

    def setUp(self):
        self.lat_lon_service = LatLonService()

    def test_GIVEN_fractional_nums_WHEN_get_nearest_cell_center_THEN_returns_correct_centers(self):
        results = self.lat_lon_service.get_nearest_cell_center(1.11, 53.7, 1)
        assert_that(results, is_((1.25, 53.75)))

    def test_GIVEN_whole_nums_WHEN_get_nearest_cell_center_THEN_returns_correct_centers(self):
        results = self.lat_lon_service.get_nearest_cell_center(1.00, 55, 1)
        assert_that(results, is_((1.25, 55.25)))

    def test_GIVEN_cell_centers_WHEN_get_nearest_cell_center_THEN_returns_same_centers(self):
        results = self.lat_lon_service.get_nearest_cell_center(-17.25, 11.25, 1)
        assert_that(results, is_((-17.25, 11.25)))