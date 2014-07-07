#header
from joj.model.non_database.spatial_extent import SpatialExtent, InvalidSpatialExtent
from joj.services.tests.base import BaseTest


class TestSpatialExtentLongitude(BaseTest):

    def setUp(self):
        pass

    def test_GIVEN_global_bounds_WHEN_longitude_greater_than_180_THEN_raise_InvalidSpatialExtent(self):
        spatial_extent = SpatialExtent(90, -90, -180, 180)
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent.set_lon(10, 500)
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent.set_lon(360.0000000001, 90)

    def test_GIVEN_global_bounds_WHEN_longitude_less_than_minus_180_THEN_raise_InvalidSpatialExtent(self):
        spatial_extent = SpatialExtent(90, -90, -180, 180)
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent.set_lon(150, -180.0000000001)
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent.set_lon(-220, 90)

    def test_GIVEN_global_bounds_WHEN_longitude_equal_to_bounds_THEN_accepted(self):
        spatial_extent = SpatialExtent(90, -90, -180, 180)
        spatial_extent.set_lon(-180, 180)

    def test_GIVEN_limited_bounds_WHEN_eastern_longitude_east_of_bounds_THEN_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(45, -45, 50, 70)
            spatial_extent.set_lon(55, 71)

    def test_GIVEN_limited_bounds_WHEN_western_longitude_west_of_bounds_THEN_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(45, -45, 50, 70)
            spatial_extent.set_lon(45, 65)

    def test_GIVEN_limited_bounds_WHEN_both_longitudes_outside_bounds_THEN_raise_InvaldSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(45, -45, 50, 70)
            spatial_extent.set_lon(-100, 160)

    def test_GIVEN_limited_bounds_WHEN_both_longitudes_inside_bounds_THEN_accepted(self):
        spatial_extent = SpatialExtent(45, -45, 50, 70)
        spatial_extent.set_lon(55, 65)

    def test_GIVEN_limited_bounds_crossing_meridian_WHEN_extent_in_bounds_THEN_accepted(self):
        spatial_extent = SpatialExtent(45, -45, -1, 4)
        spatial_extent.set_lon(1, 2)
        spatial_extent = SpatialExtent(45, -45, -2, 4)
        spatial_extent.set_lon(-1, 2)

    def test_GIVEN_global_bounds_WHEN_longitudes_enclose_dateline_THEN_accepted(self):
        spatial_extent = SpatialExtent(90, -90, -180, 180)
        spatial_extent.set_lon(150, -150)

    def test_GIVEN_limited_bounds_WHEN_longitudes_enclose_dateline_THEN_accepted(self):
        spatial_extent = SpatialExtent(45, -45, 150, -150)
        spatial_extent.set_lon(160, -160)

    def test_GIVEN_limited_bounds_enclosing_dateline_WHEN_longitude_outside_extent_THEN_raises_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(45, -45, 150, -150)
            spatial_extent.set_lon(145, -145)

    def test_GIVEN_limited_bounds_enclosing_dateline_WHEN_longitude_doesnt_enclose_meridian_THEN_accepted(self):
        spatial_extent = SpatialExtent(45, -45, 45, -170)
        spatial_extent.set_lon(110, 160)
        spatial_extent = SpatialExtent(45, -45, 45, -170)
        spatial_extent.set_lon(-179, -171)

    def test_GIVEN_limited_bounds_not_enclosing_dateline_WHEN_longitude_does_enclose_meridian_THEN_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(45, -45, 30, 150)
            spatial_extent.set_lon(40, -170)

    def test_GIVEN_limited_bounds_WHEN_longitude_wraps_around_earth_THEN_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(45, -45, 150, -150)
            spatial_extent.set_lon(-160, 160)
            spatial_extent = SpatialExtent(45, -45, -30, 30)
            spatial_extent.set_lon(25, -25)


class TestSpatialExtentLatitude(BaseTest):

    def test_GIVEN_global_bounds_WHEN_given_latitude_greater_than_90_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(90, -90, -180, 180)
            spatial_extent.set_lat(90.00000001, -45)
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(90, -90, -180, 180)
            spatial_extent.set_lat(135, -5)

    def test_GIVEN_global_bounds_WHEN_given_latitude_less_than_minus_90_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(90, -90, -180, 180)
            spatial_extent.set_lat(45, -90.000001)
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(90, -90, -180, 180)
            spatial_extent.set_lat(5, -180)

    def test_GIVEN_global_bounds_WHEN_given_latitude_equal_to_bounds_THEN_accepted(self):
        spatial_extent = SpatialExtent(90, -90, -180, 180)
        spatial_extent.set_lat(90, -90)

    def test_GIVEN_limited_bounds_WHEN_given_northern_latitude_north_of_bounds_THEN_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(50, 40, -50, 50)
            spatial_extent.set_lat(55, 45)

    def test_GIVEN_limited_bounds_WHEN_given_southern_latitude_south_of_bounds_THEN_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(30, -10, -50, 50)
            spatial_extent.set_lat(10, -15)

    def test_GIVEN_limited_bounds_WHEN_given_both_latitudes_outside_bounds_THEN_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(45, -45, -50, 50)
            spatial_extent.set_lat(50, 50)

    def test_GIVEN_limited_bounds_WHEN_given_latitudes_in_bounds_THEN_accepted(self):
            spatial_extent = SpatialExtent(45, -45, -50, 50)
            spatial_extent.set_lat(30, 1)

    def test_GIVEN_limited_bounds_WHEN_given_northern_latitude_below_southern_latitude_THEN_raise_InvalidSpatialExtent(self):
        with self.assertRaises(InvalidSpatialExtent, msg="Should have thrown an InvalidSpatialExtent exception"):
            spatial_extent = SpatialExtent(-45, 45, -50, 50)
            spatial_extent.set_lat(1, 30)
