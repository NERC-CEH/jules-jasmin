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
from formencode import Invalid


from hamcrest import *
import netCDF4
from job_runner.tests import TestController
from job_runner.post_processing_scripts.postProcessBNG import PostProcessBNG, ProcessingError
import numpy as np


class TestPostProcessBNG(TestController):

    def assert_that_arrays_almost_the_same(self, expected_values, resulting_values, message=""):
        assert_that(resulting_values.shape, is_(expected_values.shape), "Array shapes for {}".format(message))
        assert_that(np.ma.allclose(expected_values[:], resulting_values[:], atol=1.0e-15),
                    is_(True),
                    "{} arrays not almost the same. Expected\n {}\n was\n {}"
                    .format(message, expected_values[:], resulting_values[:]))
        assert_that(np.array_equal(np.ma.getmaskarray(expected_values[:]), np.ma.getmaskarray(resulting_values[:])),
                    is_(True),
                    "{} arrays have the same mask. Expected\n {}\n was\n {}"
                    .format(message, expected_values[:], resulting_values[:]))

    def assert_that_var_meta_data(self, actual_variable, long_name, standard_name, units, message):
        assert_that(actual_variable.long_name, is_(long_name), "long name of {}".format(message))
        assert_that(actual_variable.standard_name, is_(standard_name), "standard name of {}".format(message))
        assert_that(actual_variable.units, is_(units), "units of {}".format(message))

    def create_reference_file(self, expected_lats, expected_lons, expected_x, expected_y):

        reference_file = netCDF4.Dataset("ref", mode="w", diskless=True)
        reference_file.createDimension('x', len(expected_x))
        reference_file.createDimension('y', len(expected_y))
        reference_file.createVariable('lat', 'f4', ('y', 'x'))
        reference_file.createVariable('lon', 'f4', ('y', 'x'))
        reference_file.createVariable('x', 'f4', ('x',))
        reference_file.createVariable('y', 'f4', ('y',))
        reference_file.variables['lat'][:] = expected_lats
        reference_file.variables['lon'][:] = expected_lons
        reference_file.variables['x'][:] = expected_x
        reference_file.variables['y'][:] = expected_y
        return reference_file

    def create_input_file(self, in_lats, in_lons, in_values, in_time=None, in_pusedo=None):
        file_in_handle = netCDF4.Dataset("input", mode="w", diskless=True)

        file_in_handle.createDimension('x', in_lats.shape[0])
        file_in_handle.createDimension('y', in_lats.shape[1])
        if in_time is not None:
            file_in_handle.createDimension('time', in_time.shape[0])
        if in_pusedo is not None:
            file_in_handle.createDimension('pusedo', in_pusedo.shape[0])

        lat_var = file_in_handle.createVariable('latitude', 'f4', ('y', 'x'))
        lat_var[:] = in_lats

        lon_var = file_in_handle.createVariable('longitude', 'f4', ('y', 'x'))
        lon_var[:] = in_lons

        if in_time is None:
            values_var = file_in_handle.createVariable('values', 'f4', ('y', 'x'), fill_value=-99999.0)
        else:
            time_var = file_in_handle.createVariable('time', 'f4', ('time',))
            time_var[:] = in_time
            if in_pusedo is None:
                values_var = file_in_handle.createVariable('values', 'f4', ('time', 'y', 'x'), fill_value=-99999.0)
            else:
                pusedo_var = file_in_handle.createVariable('pusedo', 'f4', ('pusedo',))
                pusedo_var[:] = in_pusedo
                values_var = file_in_handle.createVariable('values', 'f4', ('pusedo', 'time', 'y', 'x'), fill_value=-99999.0)

        values_var[:] = in_values

        return file_in_handle

    def assert_that_variables_are_as_expected(self, expected_lats, expected_lons, expected_values, expected_x,
                                              expected_y, expected_t=None, expected_pusedo=None):
        out_variables = self.process.output_file_handle.variables
        self.assert_that_arrays_almost_the_same(expected_values, out_variables['values'], "values")
        assert_that(out_variables['values'].getncattr('_FillValue'), is_(-99999.0), "fill value for values")
        self.assert_that_arrays_almost_the_same(expected_lats, out_variables['latitude'], "latitudes")
        self.assert_that_var_meta_data(out_variables['latitude'], 'latitude', 'latitude', 'degrees_north', "latitude")
        self.assert_that_arrays_almost_the_same(expected_lons, out_variables['longitude'], "longitudes")
        self.assert_that_arrays_almost_the_same(expected_x, out_variables['x'], "x variable")
        self.assert_that_arrays_almost_the_same(expected_y, out_variables['y'], "y variable")
        if expected_t is not None:
            # deliberate upper case of T for time
            assert_that(self.process.output_file_handle.dimensions, has_key('Time'), "Time is in dimensions")
            self.assert_that_arrays_almost_the_same(expected_t, out_variables['Time'], "Time variable")
        if expected_pusedo is not None:
            self.assert_that_arrays_almost_the_same(expected_pusedo, out_variables['pusedo'], "pusedo variable")

        assert_that(self.process.output_file_handle.variables, has_key('crs'), "crs is in variable")



    def test_GIVEN_file_with_3x2_points_in_WHEN_convert_THEN_return_file_with_all_3x2_points_populated(self):
        expected_x = np.array([0, 1000, 2000])
        expected_y = np.array([0, 1000])
        expected_lats = np.array(
            [[49.766807231896, 49.7674713664211, 49.768133858763],
            [49.775759046806, 49.7764233904388, 49.7770860913769]])
        expected_lons = np.array(
            [[-7.5571598420827, -7.54333897801594, -7.52951760137346],
             [-7.55818671478591, -7.54436332897671, -7.53053943025975]])

        in_lats = np.array(
            [[49.766807231896, 49.7674713664211, 49.768133858763, 49.775759046806, 49.7764233904388, 49.7770860913769]])
        in_lons = np.array(
            [[-7.5571598, -7.54333898, -7.529518, -7.5581867, -7.544363, -7.53054]])
        expected_values = np.array([[0.0, 1.0, 2.0],
                                    [1.0, 1.1, 2.1]])
        in_values = [expected_values.flatten()]

        self.process.input_file_handle = self.create_input_file(in_lats, in_lons, in_values)
        self.process.reference_file_handle = self.create_reference_file(expected_lats, expected_lons, expected_x, expected_y)
        self.process.output_file_handle = netCDF4.Dataset("output", mode="w", diskless=True)

        self.process.convert_jules_1d_to_thredds_2d_for_chess()

        self.assert_that_variables_are_as_expected(expected_lats, expected_lons, expected_values, expected_x,
                                                   expected_y)

    def setUp(self):
        self.process = PostProcessBNG()

    def tearDown(self):
        self.process.close()

    def test_GIVEN_file_with_3x2_points_and_points_missing_WHEN_convert_THEN_return_file_with_all_3x2_points_populated_and_missing_values_for_non_populated(self):
        expected_x = np.array([0, 1000, 2000])
        expected_y = np.array([0, 1000])
        expected_lats = np.array(
            [[49.766807231896, 49.7674713664211, 49.768133858763],
             [49.775759046806, 49.7764233904388, 49.7770860913769]])
        expected_lons = np.array(
            [[-7.5571598420827, -7.54333897801594, -7.52951760137346],
             [-7.55818671478591, -7.54436332897671, -7.53053943025975]])

        in_lats = np.array(
            [[49.766807231896, 49.7674713664211, 49.768133858763, 49.7764233904388, 49.7770860913769]])
        in_lons = np.array(
            [[-7.5571598, -7.54333898, -7.529518, -7.544363, -7.53054]])
        expected_values = np.ma.array([[0.0, 1.0, 2.0],
                                       [1.0, 1.1, 2.1]],
                                      mask=[[False, False, False],
                                            [True, False, False]])
        in_values = [[0.0, 1.0, 2.0, 1.1, 2.1]]

        self.process.input_file_handle = self.create_input_file(in_lats, in_lons, in_values)
        self.process.reference_file_handle = self.create_reference_file(expected_lats, expected_lons, expected_x, expected_y)
        self.process.output_file_handle = netCDF4.Dataset("output", mode="w", diskless=True)

        self.process.convert_jules_1d_to_thredds_2d_for_chess()

        self.assert_that_variables_are_as_expected(expected_lats, expected_lons, expected_values, expected_x,
                                                   expected_y)

    def test_GIVEN_file_with_1x1_point_WHEN_convert_THEN_return_file_with_all_1x1_points_populated(self):
        ref_x = np.array([0, 1000, 2000])
        ref_y = np.array([1, 1001, 2001])
        ref_lats = np.array(
            [[49.11, 49.21, 49.31],
             [49.12, 49.22, 49.32],
             [49.13, 49.23, 49.33]])
        ref_lons = np.array(
            [[7.11, 7.21, 7.31],
             [7.12, 7.22, 7.32],
             [7.13, 7.23, 7.33]])

        in_lats = np.array([[49.22]])
        in_lons = np.array([[7.22]])
        expected_x = np.array([1000])
        expected_y = np.array([1001])
        expected_lats = np.array([[49.22]])
        expected_lons = np.array([[7.22]])
        expected_values = np.array([[6]])

        self.process.input_file_handle = self.create_input_file(in_lats, in_lons, expected_values)
        self.process.reference_file_handle = self.create_reference_file(ref_lats, ref_lons, ref_x, ref_y)
        self.process.output_file_handle = netCDF4.Dataset("output", mode="w", diskless=True)

        self.process.convert_jules_1d_to_thredds_2d_for_chess()

        self.assert_that_variables_are_as_expected(expected_lats, expected_lons, expected_values, expected_x,
                                                   expected_y)

    def test_GIVEN_file_with_3x2x1_points_in_WHEN_convert_THEN_return_file_with_all_3x2x1_points_populated_and_time_var_is_Time(self):
        ref_x = np.array([0, 1000, 2000])
        ref_y = np.array([1, 1001, 2001])
        ref_lats = np.array(
            [[49.11, 49.21, 49.31],
             [49.12, 49.22, 49.32],
             [49.13, 49.23, 49.33]])
        ref_lons = np.array(
            [[7.11, 7.21, 7.31],
             [7.12, 7.22, 7.32],
             [7.13, 7.23, 7.33]])

        expected_x = np.array([1000, 2000])
        expected_y = np.array([1001])
        expected_time = np.array([4.0, 5.0, 6.0])
        expected_lats = np.array([[49.22, 49.32]])
        expected_lons = np.array([[7.22, 7.32]])
        expected_values = np.array([[[6, 7]], [[8, 9]], [[9, 10]]])

        in_lats = expected_lats
        in_lons = expected_lons
        in_time = expected_time
        in_values = [expected_values.flatten()]

        self.process.input_file_handle = self.create_input_file(in_lats, in_lons, in_values, in_time)
        self.process.reference_file_handle = self.create_reference_file(ref_lats, ref_lons, ref_x, ref_y)
        self.process.output_file_handle = netCDF4.Dataset("output", mode="w", diskless=True)

        self.process.convert_jules_1d_to_thredds_2d_for_chess()

        self.assert_that_variables_are_as_expected(expected_lats, expected_lons, expected_values, expected_x,
                                                   expected_y, expected_time)

    def test_GIVEN_file_with_4x3x2x1_points_in_WHEN_convert_THEN_return_file_with_all_4x3x2x1_points_populated_and_time_var_is_Time(self):
        ref_x = np.array([1000, 2000])
        ref_y = np.array([1001])
        ref_lats = np.array(
            [[49.22, 49.32]])
        ref_lons = np.array(
            [[7.22, 7.32]])

        expected_x = np.array([1000, 2000])
        expected_y = np.array([1001])
        expected_pusedo = np.array([10.0, 11.0, 12.0, 13.0])
        expected_time = np.array([4.0, 5.0, 6.0])
        expected_lats = np.array([[49.22, 49.32]])
        expected_lons = np.array([[7.22, 7.32]])
        expected_values = np.arange(24).reshape((4, 3, 1, 2))

        in_lats = expected_lats
        in_lons = expected_lons
        in_time = expected_time
        in_pusedo = expected_pusedo
        in_values = [expected_values.flatten()]

        self.process.input_file_handle = self.create_input_file(in_lats, in_lons, in_values, in_time, in_pusedo)
        self.process.reference_file_handle = self.create_reference_file(ref_lats, ref_lons, ref_x, ref_y)
        self.process.output_file_handle = netCDF4.Dataset("output", mode="w", diskless=True)

        self.process.convert_jules_1d_to_thredds_2d_for_chess()

        self.assert_that_variables_are_as_expected(expected_lats, expected_lons, expected_values, expected_x,
                                                   expected_y, expected_time, expected_pusedo)

    def test_GIVEN_file_with_no_points_WHEN_convert_THEN_return_file_with_no_points_populated(self):
        ref_x = np.array([0, 1000, 2000])
        ref_y = np.array([1, 1001, 2001])
        ref_lats = np.array(
            [[49.11, 49.21, 49.31],
             [49.12, 49.22, 49.32],
             [49.13, 49.23, 49.33]])
        ref_lons = np.array(
            [[7.11, 7.21, 7.31],
             [7.12, 7.22, 7.32],
             [7.13, 7.23, 7.33]])

        in_lats = np.array([[]])
        in_lons = np.array([[]])
        in_values = np.array([[]])

        self.process.input_file_handle = self.create_input_file(in_lats, in_lons, in_values)
        self.process.reference_file_handle = self.create_reference_file(ref_lats, ref_lons, ref_x, ref_y)
        self.process.output_file_handle = netCDF4.Dataset("output", mode="w", diskless=True)

        assert_that(self.process.convert_jules_1d_to_thredds_2d_for_chess, raises(ProcessingError))

    def test_GIVEN_file_with_meta_data_WHEN_convert_THEN_meta_data_transfered_and_crs_mapping_added(self):
        ref_x = np.array([0, 1000, 2000])
        ref_y = np.array([1, 1001, 2001])
        ref_lats = np.array(
            [[49.11, 49.21, 49.31],
             [49.12, 49.22, 49.32],
             [49.13, 49.23, 49.33]])
        ref_lons = np.array(
            [[7.11, 7.21, 7.31],
             [7.12, 7.22, 7.32],
             [7.13, 7.23, 7.33]])

        in_lats = np.array([[49.22]])
        in_lons = np.array([[7.22]])
        in_values = np.array([[6]])
        expected_metadata_value = "some metadata"
        expected_global_metadata_value = "some globalmetadata"

        self.process.input_file_handle = self.create_input_file(in_lats, in_lons, in_values)
        self.process.input_file_handle.variables['values'].metadata_value = expected_metadata_value
        self.process.input_file_handle.metadata_value = expected_global_metadata_value

        self.process.reference_file_handle = self.create_reference_file(ref_lats, ref_lons, ref_x, ref_y)
        self.process.output_file_handle = netCDF4.Dataset("output", mode="w", diskless=True)

        self.process.convert_jules_1d_to_thredds_2d_for_chess(verbose=True)

        assert_that(self.process.output_file_handle.variables['values'].ncattrs(), has_item('metadata_value'), "variable meta data items exists")
        assert_that(self.process.output_file_handle.variables['values'].metadata_value, is_(expected_metadata_value), "variable metadata is set correctly")

        assert_that(self.process.output_file_handle.ncattrs(), has_item('metadata_value'), "global meta data items exists")
        assert_that(self.process.output_file_handle.metadata_value, is_(expected_global_metadata_value), "global metadata is set correctly")

        assert_that(self.process.output_file_handle.ncattrs(), has_item('grid_mapping'), "grid_mapping items exists")
        assert_that(self.process.output_file_handle.grid_mapping, is_('crs'), "grid mapping is set to crs")

    def test_GIVEN_file_with_time_bounds_in_WHEN_convert_THEN_return_file_with_time_bound_in(self):
        ref_x = np.array([1000, 2000])
        ref_y = np.array([1001])
        ref_lats = np.array(
            [[49.22, 49.32]])
        ref_lons = np.array(
            [[7.22, 7.32]])

        expected_x = np.array([1000, 2000])
        expected_y = np.array([1001])
        expected_time = np.array([4.0, 5.0, 6.0])
        expected_lats = np.array([[49.22, 49.32]])
        expected_lons = np.array([[7.22, 7.32]])
        expected_values = np.arange(6).reshape((3, 1, 2))

        in_lats = expected_lats
        in_lons = expected_lons
        in_time = expected_time
        in_values = [expected_values.flatten()]

        self.process.input_file_handle = self.create_input_file(in_lats, in_lons, in_values, in_time)
        self.process.reference_file_handle = self.create_reference_file(ref_lats, ref_lons, ref_x, ref_y)
        self.process.output_file_handle = netCDF4.Dataset("output", mode="w", diskless=True)

        self.process.input_file_handle.createDimension('nt', 2)
        bnds = self.process.input_file_handle.createVariable('time_bounds', 'f4', ('time', 'nt'))
        expected_bnds = np.arange(2 * 3).reshape((3, 2))
        bnds[:] = expected_bnds

        self.process.convert_jules_1d_to_thredds_2d_for_chess()

        self.assert_that_variables_are_as_expected(expected_lats, expected_lons, expected_values, expected_x,
                                                   expected_y, expected_time)
        self.assert_that_arrays_almost_the_same(bnds,
                                                self.process.output_file_handle.variables['time_bounds'],
                                                "time bounds")