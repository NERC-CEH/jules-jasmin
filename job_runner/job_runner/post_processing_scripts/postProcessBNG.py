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
import datetime
import netCDF4
import numpy as np
import os


class ProcessingError(Exception):
    """
    There is a processing error that the user should be alerted to
    """
    def __init__(self, message):
        """
        :param message: message for the user
        """
        super(ProcessingError, self).__init__()
        self.message = message


class PostProcessBNG(object):
    """
    Post process BNG data from JULES output to THREDDs output
    """

    def _add_global_file_attributes(self, verbose):
        """
        Add needed global metadata to the file (i.e. attributes) so THREDDS can read it
        :param verbose: true to output more information to the screen
        :return: nothing
        """
        if verbose:
            print "Adding global attributes"

        # Loops through existing global attributes
        for globAtt in self.input_file_handle.ncattrs():
            setattr(self.output_file_handle, globAtt, getattr(self.input_file_handle, globAtt))

        # Add metadata
        setattr(self.output_file_handle, 'title', 'CHESS output data')
        setattr(self.output_file_handle, 'institution', 'Centre for Ecology & Hydrology (CEH) Wallingford')
        setattr(self.output_file_handle, 'grid_mapping', 'crs')
        setattr(self.output_file_handle, 'source', 'run using MAJIC')
        setattr(self.output_file_handle, 'reference', '')
        setattr(self.output_file_handle, 'summary', 'Output data for JULES run with CHESS driving data for the UK')
        setattr(self.output_file_handle, 'keywords', 'CHESS, JULES')
        setattr(self.output_file_handle, 'date_created', str(datetime.datetime.now())[:10])
        setattr(self.output_file_handle, 'date_modified', str(datetime.datetime.now())[:10])
        setattr(self.output_file_handle, 'date_issued', str(datetime.datetime.now())[:10])
        setattr(self.output_file_handle, 'creator_name', 'MAJIC')
        setattr(self.output_file_handle, 'creator_url', 'https://majic.ceh.ac.uk/')
        setattr(self.output_file_handle, 'creator_email', 'majic@ceh.ac.uk')
        setattr(self.output_file_handle, 'geospatial_lat_min', 49.766808)
        setattr(self.output_file_handle, 'geospatial_lat_max', 61.026794)
        setattr(self.output_file_handle, 'geospatial_lon_min', -7.55716)
        setattr(self.output_file_handle, 'geospatial_lon_max', 3.554013)
        setattr(self.output_file_handle, 'licence', 'Licensing conditions apply (datalicensing@ceh.ac.uk)')
        setattr(self.output_file_handle, 'publisher_name', 'Centre for Ecology and Hydrology')
        setattr(self.output_file_handle, 'publisher_url', 'http://www.ceh.ac.uk')
        setattr(self.output_file_handle, 'publisher_email', 'enquiries@ceh.ac.uk')
        setattr(self.output_file_handle, 'conventions', 'CF-1.6')
        setattr(self.output_file_handle, 'version', 'unknown')
        setattr(self.output_file_handle, 'spatial_resolution_distance', 1000)
        setattr(self.output_file_handle, 'spatial_resolution_unit', 'urn:ogc:def:uom:EPSG::9001')
        setattr(self.output_file_handle, 'id', '')  # http://www.guidgenerator.com/
        setattr(self.output_file_handle, 'licence', 'https://majic.ceh.ac.uk/docs/majic_terms_and_conditions.pdf')
        setattr(self.output_file_handle, 'history', 'created on ' + str(datetime.datetime.now())[:10])

    def _locate_jules_points_in_lat_lon_file(self, verbose):
        """
        Find a list of indexes in the reference file for the points in the input file and store their indexes
        :param verbose: true to output more information to the screen
        :return: tuple of lat array and lon array of indexes
        """

        if verbose:
            print("Locating points in the input file in the reference file")

        file_in = self.input_file_handle

        if 'x' not in file_in.dimensions or 'y' not in file_in.dimensions:
            raise ProcessingError("Can not process the file it does not appear to be a BNG file. "
                                  "It doesn't have both an x and y dimension.")

        count_x_in = len(file_in.dimensions['x'])
        count_y_in = len(file_in.dimensions['y'])

        if count_x_in == 0 or count_y_in == 0:
            raise ProcessingError("Can not process the file it does not appear to be a BNG file. "
                                  "It doesn't have both an x and y variables of size >0.")

        lats_in = file_in.variables['latitude'][:].flatten()
        lons_in = file_in.variables['longitude'][:].flatten()

        if 'latitude' not in file_in.variables or 'longitude' not in file_in.variables:
            raise ProcessingError("Can not process the file it does not appear to be a BNG file. "
                                  "It doesn't have both an latitude and longitude variables.")

        lats_ref = self.reference_file_handle.variables['lat'][:]
        lons_ref = self.reference_file_handle.variables['lon'][:]

        # threshold for lats and lons to match
        thresh = 5e-5

        total_points = count_x_in * count_y_in
        x_ref_index = np.zeros(total_points, dtype='int')
        y_ref_index = np.zeros(total_points, dtype='int')

        for index in range(total_points):
            if verbose and index % 10000 == 0:
                print "{} points of {}".format(index, total_points)
            ref_indexes_found = np.where(
                np.logical_and(
                    np.abs(lats_ref-lats_in[index]) < thresh,
                    np.abs(lons_ref-lons_in[index]) < thresh))
            if len(ref_indexes_found[0]) == 1:
                # axises are in order y x in file
                x_ref_index[index] = ref_indexes_found[1]
                y_ref_index[index] = ref_indexes_found[0]
            else:
                if len(ref_indexes_found[0]) == 0:
                    raise ProcessingError("point %d (%s %s) not found" % (index, lats_in[index], lons_in[index]))
                elif len(ref_indexes_found[0]) > 1:
                    raise ProcessingError("point %d (%s %s) been found %d times"
                                          % (index, lats_in[index], lons_in[index], len(ref_indexes_found[0])))

        self.x_ref_index = x_ref_index
        self.y_ref_index = y_ref_index

    def _remap_variable_data(self, variable_in, variable_out):
        """
        Remap the data variable from 1D to 2D using the indexes
        :param variable_in: variable to remap
        :param variable_out: variable to output
        :return: nothing
        """
        if len(variable_in.shape) == 2:
            variable_out[self.y_ref_index, self.x_ref_index] = variable_in[:].flatten()
        elif len(variable_in.shape) == 3:
            for t in range(variable_in.shape[0]):
                variable_out[t, self.y_ref_index, self.x_ref_index] = variable_in[t, :, :].flatten()
        elif len(variable_in.shape) == 4:
            for t in range(variable_in.shape[0]):
                for z in range(variable_in.shape[1]):
                    variable_out[t, z, self.y_ref_index, self.x_ref_index] = variable_in[t, z, :, :].flatten()
        elif len(variable_in.shape) == 5:
            for i1 in range(variable_in.shape[0]):
                for i2 in range(variable_in.shape[1]):
                    for i3 in range(variable_in.shape[2]):
                        variable_out[i1, i2, i3, self.y_ref_index, self.x_ref_index] =\
                            variable_in[i1, i2, i3, :, :].flatten()
        elif len(variable_in.shape) == 6:
            for i1 in range(variable_in.shape[0]):
                for i2 in range(variable_in.shape[1]):
                    for i3 in range(variable_in.shape[2]):
                        for i4 in range(variable_in.shape[3]):
                            variable_out[i1, i2, i3, i4, self.y_ref_index, self.x_ref_index] =\
                                variable_in[i1, i2, i3, i4, :, :].flatten()
        elif len(variable_in.shape) == 7:
            for i1 in range(variable_in.shape[0]):
                for i2 in range(variable_in.shape[1]):
                    for i3 in range(variable_in.shape[2]):
                        for i4 in range(variable_in.shape[3]):
                            for i5 in range(variable_in.shape[3]):
                                variable_out[i1, i2, i3, i4, i5, self.y_ref_index, self.x_ref_index] =\
                                    variable_in[i1, i2, i3, i4, i5, :, :].flatten()
        else:
            raise ProcessingError("too many dimensions to remap")

    def _convert_variables_and_dimensions(self, verbose):
        """
        Convert all the variables and dimensions
        :param verbose: true to output more information to the screen
        :return: nothing
        """
        compress_netcdf_file = True

        file_in_handle = self.input_file_handle
        y_min = np.min(self.y_ref_index)
        y_max = np.max(self.y_ref_index)
        x_min = np.min(self.x_ref_index)
        x_max = np.max(self.x_ref_index)
        self.x_ref_index -= x_min
        self.y_ref_index -= y_min

        for dim in file_in_handle.dimensions:
            if verbose:
                print("converting dimension: {}".format(dim))
            if dim == 'y':
                dimlen = y_max - y_min + 1
            elif dim == 'x':
                dimlen = x_max - x_min + 1
            else:
                dimlen = len(file_in_handle.dimensions[dim])

            if dim == 'time':
                self.output_file_handle.createDimension('Time', dimlen)
            else:
                self.output_file_handle.createDimension(dim, dimlen)

        for variable_name in file_in_handle.variables:
            if variable_name not in ('latitude', 'longitude', 'x', 'y', 'crs'):
                if verbose:
                    print("converting variable: {}".format(variable_name))
                variable_in = file_in_handle.variables[variable_name]
                dimensions_in = variable_in.dimensions
                var_attributes_in = variable_in.ncattrs()

                fill_value_in = None
                if '_FillValue' in var_attributes_in:
                    fill_value_in = variable_in.getncattr('_FillValue')
                elif 'fill_value' in var_attributes_in:
                    fill_value_in = variable_in.fill_value
                elif 'missing_value' in var_attributes_in:
                    fill_value_in = variable_in.missing_value
                elif "x" in dimensions_in and "y" in dimensions_in:
                    fill_value_in = np.float_(-99999.0)

                dimensions_out = ['Time' if x == 'time' else x for x in dimensions_in]

                if variable_name == "time":
                    variable_name_out = "Time"
                else:
                    variable_name_out = variable_name

                if fill_value_in is None:
                    variable_out = self.output_file_handle.createVariable(
                        variable_name_out,
                        variable_in.dtype,
                        dimensions=dimensions_out,
                        zlib=compress_netcdf_file)
                else:
                    variable_out = self.output_file_handle.createVariable(
                        variable_name_out,
                        variable_in.dtype,
                        dimensions=dimensions_out,
                        fill_value=fill_value_in,
                        zlib=compress_netcdf_file)

                for attr in var_attributes_in:
                    if attr not in ('_FillValue', 'fill_value', 'missing_value'):
                        variable_out.setncattr(attr, variable_in.getncattr(attr))

                if "x" in dimensions_in and "y" in dimensions_in:
                    remapped_array = np.ma.masked_equal(
                        np.ones(self.output_file_handle.variables[variable_name].shape) * fill_value_in, fill_value_in)
                    self._remap_variable_data(variable_in, remapped_array)
                    variable_out[:] = remapped_array[:]
                    # as long one element is not masked then set the actual range
                    if not np.all(np.ma.getmaskarray(remapped_array)):
                        variable_out.actual_range = remapped_array.min(), remapped_array.max()
                else:
                    variable_out[:] = variable_in[:]

        # create variable x
        if verbose:
            print('Creating Variable: x')
        ref_x = self.reference_file_handle.variables['x']
        out_x = self.output_file_handle.createVariable("x", ref_x.dtype, ["x"], zlib=compress_netcdf_file)
        out_x.units = 'm'
        out_x.long_name = 'easting - OSGB36 grid reference'
        out_x.standard_name = 'projection_x_coordinate'
        out_x.point_spacing = "even"
        out_x[:] = ref_x[x_min:x_max+1]

        # create variable y
        if verbose:
            print('Creating Variable: y')
        ref_y = self.reference_file_handle.variables['y']
        out_y = self.output_file_handle.createVariable("y", ref_y.dtype, ["y"], zlib=compress_netcdf_file)
        out_y.units = 'm'
        out_y.long_name = 'northing - OSGB36 grid reference'
        out_y.standard_name = 'projection_x_coordinate'
        out_y.point_spacing = "even"
        out_y[:] = ref_y[y_min:y_max + 1]

        if verbose:
            print('Creating Variable: latitude')
        ref_lat = self.reference_file_handle.variables['lat']
        out_lat = self.output_file_handle.createVariable(
            "latitude",
            ref_lat.dtype,
            ["y", "x"],
            zlib=compress_netcdf_file)
        out_lat.long_name = 'latitude'
        out_lat.standard_name = 'latitude'
        out_lat.units = 'degrees_north'
        out_lat[:] = ref_lat[y_min:y_max + 1, x_min:x_max + 1]

        if verbose:
            print('Creating Variable: longitude')
        ref_lon = self.reference_file_handle.variables['lon']
        out_lon = self.output_file_handle.createVariable(
            "longitude",
            ref_lon.dtype,
            ["y", "x"],
            zlib=compress_netcdf_file)
        out_lon.long_name = 'longitude'
        out_lon.standard_name = 'longitude'
        out_lon.units = 'degrees_east'
        out_lon[:] = ref_lon[y_min:y_max + 1, x_min:x_max + 1]

        # create variable crs
        if verbose:
            print('Creating Variable: crs')
        coord = self.output_file_handle.createVariable("crs", np.int16, zlib=compress_netcdf_file)
        coord.long_name = 'coordinate_reference_system'
        coord.grid_mapping_name = "transverse_mercator"
        coord.semi_major_axis = np.float_(6377563.396)
        coord.semi_minor_axis = np.float_(6356256.910)
        coord.inverse_flattening = np.float_(299.3249646)
        coord.latitude_of_projection_origin = np.float_(49.0)
        coord.longitude_of_projection_origin = np.float_(-2.0)
        coord.false_easting = np.float_(400000.0)
        coord.false_northing = np.float_(-100000.0)
        coord.scale_factor_at_projection_origin = np.float_(0.9996012717)
        coord.EPSG_code = "EPSG:27700"

    def __init__(self):
        """
        Construct an object to perform a conversion.
        :return: nothing
        """
        self.output_file_handle = None
        self.input_file_handle = None
        self.output_file_path = None
        self.reference_file_handle = None

    def open(self, input_folder, output_folder, input_filename, ref_filepath='data/CHESS/ancils/chess_lat_lon.nc'):
        """
        Open the file needed for the processing
        :param input_folder: the input folder in which the input file exists
        :param output_folder: the output folder to write the file to
        :param input_filename: the filename of the file to read
        :param ref_filepath: the filepath for the reference file containing x,y and lats and lons
        :return: nothing
        """
        input_file_path = os.path.join(input_folder, input_filename)
        self.input_file_handle = netCDF4.Dataset(input_file_path, mode='r')
        output_file_path = os.path.join(output_folder, input_filename)
        self.output_file_handle = netCDF4.Dataset(output_file_path, 'w')
        self.reference_file_handle = netCDF4.Dataset(ref_filepath, 'r')

    def close(self):
        """
        Close the netcdf files
        :return:nothing
        """
        if self.input_file_handle is not None:
            self.input_file_handle.close()
        if self.output_file_handle is not None:
            self.output_file_handle.close()
        if self.reference_file_handle is not None:
            self.reference_file_handle.close()

    def convert_jules_1d_to_thredds_2d_for_chess(self, verbose=False):
        """
        Convert 1D data into a 2D grid.
        Before calling you need to open the various file handles and they need to be closed afterwards
        File handles needed:
            self.input_file_handle - netcdf file handle for input data
            self.output_file_handle -  netcdf file handle for output data
            self.reference_file_handle - netcdf containing reference data for lat and lon
        :param verbose: True to print more information on convert
        :return: nothing
        """

        self._locate_jules_points_in_lat_lon_file(verbose)
        self._convert_variables_and_dimensions(verbose)
        self._add_global_file_attributes(verbose)


if __name__ == '__main__':
    run_dir = "/home/matken/PycharmProjects/majic/jules-jasmin/job_runner/job_runner_test/run/chess_run"
    os.chdir(run_dir)
    inputFolder = os.path.join(run_dir, "output")
    outputFolder = os.path.join(run_dir, "processed")
    inputFileName = "majic.ftl_gb_hourly.1961.nc"

    p = PostProcessBNG()
    p.open(inputFolder, outputFolder, inputFileName)
    p.convert_jules_1d_to_thredds_2d_for_chess(verbose=True)
    p.close()
