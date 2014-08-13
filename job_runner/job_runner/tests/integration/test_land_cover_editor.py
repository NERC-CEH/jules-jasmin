"""
header
"""
from netCDF4 import Dataset
from hamcrest import assert_that, is_
import os
from pylons import config
import shutil
from job_runner.tests import TestController
from job_runner.utils.land_cover_editor import LandCoverEditor
from job_runner.services.service_exception import ServiceException


class TestLandCoverEditor(TestController):
    def setUp(self):
        self.files_dir = config['test_files_dir'] + '/land_cover'
        self.test_dir = config['test_files_dir'] + '/test'
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        shutil.copytree(self.files_dir, self.test_dir)
        self.land_cover_service = LandCoverEditor()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_GIVEN_one_mask_WHEN_edit_THEN_land_points_inside_mask_are_edited(self):
        mask_path = self.test_dir + '/equator-20-degree-horizontal-strip.nc'
        frac_path = self.test_dir + '/frac.nc'

        # Apply a strip of ice across the equator
        self.land_cover_service.apply_land_cover_action(frac_path, mask_path, 9)

        val1 = self._get_frac_values_at_point(frac_path, 0, 30)
        val2 = self._get_frac_values_at_point(frac_path, -7, -65)
        assert_that(val1, is_(8 * [0] + [1]))
        assert_that(val2, is_(8 * [0] + [1]))

    def test_GIVEN_one_mask_WHEN_edit_THEN_land_points_outside_mask_are_unchanged(self):
        mask_path = self.test_dir + '/equator-20-degree-horizontal-strip.nc'
        frac_path = self.test_dir + '/frac.nc'
        val1_pre = self._get_frac_values_at_point(frac_path, 78, 37)
        val2_pre = self._get_frac_values_at_point(frac_path, 170, -45)

        # Apply a strip of ice across the equator
        self.land_cover_service.apply_land_cover_action(frac_path, mask_path, 9)

        val1_post = self._get_frac_values_at_point(frac_path, 78, 37)
        val2_post = self._get_frac_values_at_point(frac_path, 170, -45)

        assert_that(val1_pre, is_(val1_post))
        assert_that(val2_pre, is_(val2_post))

    def test_GIVEN_one_mask_WHEN_edit_THEN_sea_points_remain_masked(self):
        mask_path = self.test_dir + '/equator-20-degree-horizontal-strip.nc'
        frac_path = self.test_dir + '/frac.nc'

        # Apply a strip of ice across the equator
        self.land_cover_service.apply_land_cover_action(frac_path, mask_path, 9)

        val1 = self._get_frac_values_at_point(frac_path, -25, 0)  # Inside mask
        val2 = self._get_frac_values_at_point(frac_path, -0, 75)  # Outside mask
        assert_that(val1, is_(9 * [None]))
        assert_that(val2, is_(9 * [None]))

    def test_GIVEN_two_masks_not_overlapping_WHEN_edit_THEN_first_edit_unchanged(self):
        mask_path1 = self.test_dir + '/equator-20-degree-horizontal-strip.nc'
        mask_path2 = self.test_dir + '/russia-square-small.nc'
        frac_path = self.test_dir + '/frac.nc'

        # Apply a strip of ice across the equator
        self.land_cover_service.apply_land_cover_action(frac_path, mask_path1, 9)
        # Then a small square of shrubs inside Russia
        self.land_cover_service.apply_land_cover_action(frac_path, mask_path2, 5)

        val_equator = self._get_frac_values_at_point(frac_path, 0, 30)
        assert_that(val_equator, is_(8 * [0] + [1]))

    def test_GIVEN_two_masks_not_overlapping_WHEN_edit_THEN_second_edit_applied(self):
        mask_path1 = self.test_dir + '/equator-20-degree-horizontal-strip.nc'
        mask_path2 = self.test_dir + '/russia-square-small.nc'
        frac_path = self.test_dir + '/frac.nc'

        # Apply a strip of ice across the equator
        self.land_cover_service.apply_land_cover_action(frac_path, mask_path1, 9)
        # Then a small square of shrubs inside Russia
        self.land_cover_service.apply_land_cover_action(frac_path, mask_path2, 5)

        val_russia = self._get_frac_values_at_point(frac_path, 55, 105)
        assert_that(val_russia, is_(4 * [0] + [1] + 4 * [0]))

    def test_GIVEN_two_masks_overlapping_WHEN_edit_THEN_overlap_is_updated(self):
        mask_path1 = self.test_dir + '/equator-20-degree-horizontal-strip.nc'
        mask_path2 = self.test_dir + '/meridian-30-degree-vertical-strip.nc'
        frac_path = self.test_dir + '/frac.nc'

        # Apply a strip of ice across the equator
        self.land_cover_service.apply_land_cover_action(frac_path, mask_path1, 9)
        # Then a vertical strip of urban
        self.land_cover_service.apply_land_cover_action(frac_path, mask_path2, 6)

        val_overlap = self._get_frac_values_at_point(frac_path, 12, 0)
        assert_that(val_overlap, is_(5 * [0] + [1] + 3 * [0]))

    def test_GIVEN_two_masks_nested_WHEN_edit_THEN_inner_updated_outer_unchanged(self):
        mask_path_big = self.test_dir + '/russia-square-big.nc'
        mask_path_small = self.test_dir + '/russia-square-small.nc'
        frac_path = self.test_dir + '/frac.nc'

        # Apply a large square of broad-leaved trees to russia
        self.land_cover_service.apply_land_cover_action(frac_path, mask_path_big, 1)
        # Then a small square of shrubs inside that
        self.land_cover_service.apply_land_cover_action(frac_path, mask_path_small, 5)

        val_inner = self._get_frac_values_at_point(frac_path, 55, 105)
        val_outer = self._get_frac_values_at_point(frac_path, 40, 80)
        assert_that(val_inner, is_(4 * [0] + [1] + 4 * [0]))
        assert_that(val_outer, is_([1] + 8 * [0]))

    def test_GIVEN_mask_wrong_shape_for_grid_WHEN_edit_THEN_ServiceException_raised(self):
        mask_path = self.test_dir + '/wrong-shape.nc'
        frac_path = self.test_dir + '/frac.nc'
        with self.assertRaises(ServiceException):
            self.land_cover_service.apply_land_cover_action(frac_path, mask_path, 1)

    def _get_frac_values_at_point(self, file_path, lat, lon):
        ds = Dataset(file_path, 'r')
        frac = ds.variables['frac']
        lat_vals = ds.variables['Latitude']
        lat_index = min(range(len(lat_vals)), key=lambda i: abs(lat_vals[i] - lat))
        lon_vals = ds.variables['Longitude']
        lon_index = min(range(len(lon_vals)), key=lambda i: abs(lon_vals[i] - lon))
        lon = ds.variables['Latitude']
        vals = frac[:, lat_index, lon_index]
        ds.close()
        return vals.tolist()
