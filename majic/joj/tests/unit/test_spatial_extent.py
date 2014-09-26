"""
#header
"""
from joj.model.non_database.spatial_extent import SpatialExtent, InvalidSpatialExtent
from joj.tests.base import BaseTest


class TestSpatialExtentLongitude(BaseTest):

    def setUp(self):
        pass

    def test_GIVEN_global_bounds_WHEN_longitude_greater_than_180_THEN_raise_InvalidSpatialExtent(self):
        spatial_extent = SpatialExtent(90, -90, -180, 180)
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent.set_lon_w(10)
            spatial_extent.set_lon_e(500)
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent.set_lon_w(180.0000000001)
            spatial_extent.set_lon_e(90)

    def test_GIVEN_global_bounds_WHEN_longitude_less_than_minus_180_THEN_raise_InvalidSpatialExtent(self):
        spatial_extent = SpatialExtent(90, -90, -180, 180)
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent.set_lon_w(150)
            spatial_extent.set_lon_e(-180.0000000001)
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent.set_lon_w(-220)
            spatial_extent.set_lon_e(90)

    def test_GIVEN_global_bounds_WHEN_longitude_equal_to_bounds_THEN_accepted(self):
        spatial_extent = SpatialExtent(90, -90, -180, 180)
        spatial_extent.set_lon_w(-180)
        spatial_extent.set_lon_e(180)

    def test_GIVEN_limited_bounds_WHEN_eastern_longitude_east_of_bounds_THEN_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(45, -45, 50, 70)
            spatial_extent.set_lon_w(55)
            spatial_extent.set_lon_e(71)

    def test_GIVEN_limited_bounds_WHEN_western_longitude_west_of_bounds_THEN_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(45, -45, 50, 70)
            spatial_extent.set_lon_w(45)
            spatial_extent.set_lon_e(65)

    def test_GIVEN_limited_bounds_WHEN_both_longitudes_outside_bounds_THEN_raise_InvaldSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(45, -45, 50, 70)
            spatial_extent.set_lon_w(-100)
            spatial_extent.set_lon_e(160)

    def test_GIVEN_limited_bounds_WHEN_both_longitudes_inside_bounds_THEN_accepted(self):
        spatial_extent = SpatialExtent(45, -45, 50, 70)
        spatial_extent.set_lon_w(55)
        spatial_extent.set_lon_e(65)

    def test_GIVEN_limited_bounds_crossing_meridian_WHEN_extent_in_bounds_THEN_accepted(self):
        spatial_extent = SpatialExtent(45, -45, -1, 4)
        spatial_extent.set_lon_w(1)
        spatial_extent.set_lon_e(2)
        spatial_extent = SpatialExtent(45, -45, -2, 4)
        spatial_extent.set_lon_w(-1)
        spatial_extent.set_lon_e(2)

    def test_GIVEN_global_bounds_WHEN_longitudes_enclose_dateline_THEN_rejected(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(90, -90, -180, 180)
            spatial_extent.set_lon_w(150)
            spatial_extent.set_lon_e(-150)

    def test_GIVEN_limited_bounds_WHEN_eastern_longitude_west_of_western_latitude_THEN_raises_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(45, -45, -120, 120)
            spatial_extent.set_lon_e(10)
            spatial_extent.set_lon_w(20)

    def test_GIVEN_limited_bounds_enclosing_dateline_WHEN_created_THEN_raise_InvaldSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(45, -45, 150, -150)

    def test_GIVEN_limited_bounds_not_enclosing_dateline_WHEN_longitude_does_enclose_dateline_THEN_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(45, -45, 30, 150)
            spatial_extent.set_lon_w(40)
            spatial_extent.set_lon_e(-170)

    def test_GIVEN_limited_bounds_WHEN_longitude_wraps_around_earth_THEN_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(45, -45, 150, -150)
            spatial_extent.set_lon_w(-160)
            spatial_extent.set_lon_e(160)
            spatial_extent = SpatialExtent(45, -45, -30, 30)
            spatial_extent.set_lon_w(25)
            spatial_extent.set_lon_e(-25)


class TestSpatialExtentLatitude(BaseTest):

    def test_GIVEN_global_bounds_WHEN_given_latitude_greater_than_90_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(90, -90, -180, 180)
            spatial_extent.set_lat_n(90.00000001)
            spatial_extent.set_lat_s(-45)
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(90, -90, -180, 180)
            spatial_extent.set_lat_n(135)
            spatial_extent.set_lat_s(-5)

    def test_GIVEN_global_bounds_WHEN_given_latitude_less_than_minus_90_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(90, -90, -180, 180)
            spatial_extent.set_lat_n(45)
            spatial_extent.set_lat_s(-90.000001)
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(90, -90, -180, 180)
            spatial_extent.set_lat_n(5)
            spatial_extent.set_lat_s(-180)

    def test_GIVEN_global_bounds_WHEN_given_latitude_equal_to_bounds_THEN_accepted(self):
        spatial_extent = SpatialExtent(90, -90, -180, 180)
        spatial_extent.set_lat_n(90)
        spatial_extent.set_lat_s(-90)

    def test_GIVEN_limited_bounds_WHEN_given_northern_latitude_north_of_bounds_THEN_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(50, 40, -50, 50)
            spatial_extent.set_lat_n(55)
            spatial_extent.set_lat_s(45)

    def test_GIVEN_limited_bounds_WHEN_given_southern_latitude_south_of_bounds_THEN_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(30, -10, -50, 50)
            spatial_extent.set_lat_n(10)
            spatial_extent.set_lat_s(-15)

    def test_GIVEN_limited_bounds_WHEN_given_both_latitudes_outside_bounds_THEN_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(45, -45, -50, 50)
            spatial_extent.set_lat_n(50)
            spatial_extent.set_lat_s(50)

    def test_GIVEN_limited_bounds_WHEN_given_latitudes_in_bounds_THEN_accepted(self):
            spatial_extent = SpatialExtent(45, -45, -50, 50)
            spatial_extent.set_lat_n(30)
            spatial_extent.set_lat_s(1)

    def test_GIVEN_limited_bounds_WHEN_given_northern_latitude_below_southern_latitude_THEN_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(45, -45, -50, 50)
            spatial_extent.set_lat_n(1)
            spatial_extent.set_lat_s(30)
