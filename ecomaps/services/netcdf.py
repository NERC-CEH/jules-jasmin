from netCDF4 import Dataset
import datetime
import numpy
import os
from pydap.client import open_url
import paste
import pylons
from coards import parse
import shutil
from ecomaps.lib.ecomaps_utils import WorkingDirectory, working_directory, find_closest

__author__ = 'Phil Jenkins (Tessella)'


class DatasetConversionWorkingDirectory(WorkingDirectory):
    """Encapsulates the aspects of a directory containing the files required for a dataset conversion"""

    _working_dir = None

    def __init__(self):
        """Constructor for our temporary directory
            Params:
                working_dir: The directory we're going to use as our base
        """

        super(DatasetConversionWorkingDirectory, self).__init__()

    @property
    def coverage_map(self):

        return os.path.join(self.root_folder, "coverage.nc")


class EcoMapsNetCdfFile(object):
    """ Houses the metadata around a NetCDF file that EcoMaps is interested in
    """

    attributes = {}
    columns = []
    time_values = []
    url = None

    def __init__(self, url):
        """ Constructor, reads in a file from the url provided
        @param url: OpenNDAP url for the NetCDF file
        """

        self.url = url

        # Let's open the file using OpenNDAP
        f = open_url(url)

        # Pull out the attributes, and column names
        self.attributes = f.attributes['NC_GLOBAL']
        self.columns = f.keys()

        if 'time' in f:
            # There's a time dimension in this dataset, so let's grab the possible
            # values out
            try:
                time_units = f['time'].attributes['units']
                self.time_values = [parse(t, time_units) for t in f['time']]
            except IndexError:

                # Not a parseable time format
                pass
        del f

    def get_preview_data(self, no_of_rows):
        """ Gets a data structure containing the first ten rows of a given point dataset

            @param no_of_rows: Restrict to a particular number of rows
        """

        points = open_url(self.url)
        column_dictionary = {}
        for column in points.keys():

            if points[column].shape:

                ##column_dictionary[column.upper()] = points[column][:]
                # Data may have been created on a machine with a different byte order to the one on which you are running
                # Python.  To deal with this issue should convert to the native system byte order BEFORE passing it to a
                # Series/DataFrame/Panel constructor.
                # see:  http://pandas.pydata.org/pandas-docs/dev/gotchas.html#byte-ordering-issues
                column_dictionary[column] = points[column][:no_of_rows].byteswap().newbyteorder()

        del points
        return column_dictionary

class NetCdfService(object):
    """ Provides operations to read elements of NetCDF files stored in our associcated THREDDS server
    """

    _config = None

    def __init__(self, config=None):

        if not config:
            from pylons import config as cfg

            self._config = cfg
        else:
            self._config = config


    def get_attributes(self, netcdf_url, column_filter=None):
        """Gets a dictionary of attributes stored on the file, optionally filtered
            by a list of column names
            @param netcdf_url: OpenNDAP url for the NetCDF file
            @param column_filter: Optional list of attribute names to return

            @returns Dictionary of attribute name/value pairs
        """

        ds = EcoMapsNetCdfFile(netcdf_url)

        if column_filter:
            return dict([(key, ds.attributes[key]) for key in column_filter if key in ds.attributes])
        else:
            return ds.attributes


    def get_variable_column_names(self, netcdf_url):
        """ Gets a list of column names that are part of a particular dataset, but
            not the standard column names (x, y, transverse_mercator)
        """

        ds = EcoMapsNetCdfFile(netcdf_url)

        columns_to_ignore = ['x', 'y', 'transverse_mercator', 'time']

        return [col for col in ds.columns if col not in columns_to_ignore]


    def get_point_data_preview(self, netcdf_url, no_of_rows=10):
        """ Gets a 2D preview of the point dataset at the given NetCDF url
            @param netcdf_url: URL to the point dataset
        """

        ds = EcoMapsNetCdfFile(netcdf_url)

        return ds.get_preview_data(no_of_rows)


    def get_time_points(self, netcdf_url):
        """ Returns a list of datetime objects corresponding to the
            possible time points in a temporal dataset

            @param netcdf_url: URL to the netCDF dataset to interrogate
            @returns : A list of datetimes, or empty list if no temporal dimension
        """

        ds = EcoMapsNetCdfFile(netcdf_url)
        return ds.time_values

    def overlay_point_data(self, point_url):
        """ Using the land cover map, overlays the point dataset passed in
            in such a way to enable it to be viewed over WMS

            @param point_url: OpenDAP URL pointing to the dataset
            @returns: The WMS URL for the duplicate point dataset
        """

        # First let's create a temporary directory
        with working_directory(DatasetConversionWorkingDirectory(),
                               os.path.join(os.path.dirname(__file__),"grid_data")) as working_dir:

            points = coverage = None

            try:
                # Open the points data
                points = open_url(point_url)

                # Coverage data needs to be opened from file,
                # as we'll be writing to it
                coverage = Dataset(working_dir.coverage_map, 'a', format='NETCDF4')

                # This map has a Land cover variable that we can
                # abuse to write a maximum value against for any
                # point whose x,y match up

                # First, get the x and y's out for the points
                north_list = points['northing'][:]
                east_list = points['easting'][:]

                coverage_north = coverage.variables['y'][:]
                coverage_east = coverage.variables['x'][:]

                # Rename the variable, and set the max value
                # to the default max (50)
                coverage.variables['LandCover'].long_name = "Point Data"
                coverage.variables['LandCover'].valid_max = 50

                # Now pull out the Land Cover variable, and reset
                # to below 0, so the points are invisible
                value = coverage.variables['LandCover'][:,:]

                for (y,x), _ in numpy.ndenumerate(value):
                    value[y,x] = -1

                # Now look for the points in the coverage map, and set the value
                # to the maximum when found
                for x,y in zip(east_list, north_list):

                    index_x = numpy.where(coverage_east==find_closest(coverage_east, x))[0][0]
                    index_y = numpy.where(coverage_north==find_closest(coverage_north, y))[0][0]

                    value[index_y,index_x] = 50

                coverage.variables['LandCover'][:,:] = value

                # OK, now we need to copy the coverage map to
                # the map server location defined in the config
                # Read the config

                file_name = "%s_%s.nc" % ("points", str(datetime.datetime.now().isoformat()).replace(':', '-'))
                file_destination = os.path.join(self._config['netcdf_file_location'], file_name)
                shutil.copyfile(working_dir.coverage_map, file_destination)
                wms_url = self._config['thredds_wms_format'] % file_name

                return wms_url

            finally:

                if points:
                    del points

                if coverage:
                    coverage.close()