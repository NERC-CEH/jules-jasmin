"""
# header
"""
import logging
import datetime
from coards import parse
import math
from numpy import amin, amax
from numpy.ma import masked_equal
from pylons import config
from joj.utils.constants import NETCDF_LATITUDE, NETCDF_LONGITUDE, NETCDF_TIME, NETCDF_TIME_BOUNDS, NETCDF_CRS, \
    NETCDF_CRS_X, NETCDF_CRS_Y
from joj.utils import constants
from joj.services.dap_client.base_dap_client import BaseDapClient, DapClientException

log = logging.getLogger(__name__)


class DapClient(BaseDapClient):
    """
    Client for communicating with the OpenDAP server to extract map data for a particular latitude / longitude
    """

    def __init__(self, url):
        """
        Create a new DapClient for a specified dataset
        :param url: The URL of the OpenDAP dataset to look for
        """
        if 'run_in_test_mode' in config and config['run_in_test_mode'].lower() == 'true':
            return
        super(DapClient, self).__init__(url)
        try:
            self._time = self._dataset[self._get_key(NETCDF_TIME)][:]
            self._time_units = self._dataset[self._get_key(NETCDF_TIME)].units
            self._start_date = self._get_data_start_date()
            self._variable_names = []
            self._variable = self._get_variable_to_plot()
            self._cache_dict = {}
            self._cache_lat_lon = None
        except Exception:
            log.exception("Can not read dataset '%s'." % url)
            raise DapClientException("Problems reading the dataset.")

    def get_longname(self):
        """
        The longname of the variable in this dataset
        :return: the long name
        """
        try:
            return self._variable.attributes['long_name']
        except KeyError:
            return self._variable_names[0]

    def get_data_range(self):
        """
        Gets the datarange of the variable in this dataset
        NOTE: This method might be time-consuming if called on a large dataset
        as it may have to iterate over every single data point.
        :return: min and max tuple for the range
        """
        try:
            return [float(self._variable.attributes['valid_min']), float(self._variable.attributes['valid_max'])]
        except (KeyError, ValueError):
            fill_value = self._variable._FillValue
            missing_value = self._variable.missing_value
            valid_array = masked_equal(masked_equal(self._variable.array, missing_value), fill_value)
            min = float(amin(valid_array))
            max = float(amax(valid_array))
            if math.isnan(min):
                min = 0
            if math.isnan(max):
                max = 100
            return [min, max]

    def get_variable_units(self):
        """
        Get the units for the independent variable
        :return:
        """
        return self._dataset[self._variable_names[0]].units

    def get_time_immediately_after(self, time):
        """
        Get the timestamp of the next data point after a specified time
        :param time: Datetime to search after
        :return: Datetime of next data point
        """
        time_secs_elapsed = self._get_seconds_elapsed(time)
        timestamps = self._time.tolist()
        next_time = None
        for time in timestamps:
            if time >= time_secs_elapsed:
                # Leave as soon as we find the first time value after this time
                next_time = time
                break
        if next_time is None:
            return None
        delta = datetime.timedelta(seconds=next_time)
        return self._start_date + delta

    def get_time_immediately_before(self, time):
        """
        Get the timestamp of the previous data point before a specified time
        :param time: Datetime to search before
        :return: Datetime of previous data point
        """
        time_secs_elapsed = self._get_seconds_elapsed(time)
        timestamps = self._time.tolist()
        prev_time = None
        for time in reversed(timestamps):
            if time <= time_secs_elapsed:
                # Leave as soon as we find the first time value before this time
                prev_time = time
                break
        if prev_time is None:
            return None
        delta = datetime.timedelta(seconds=prev_time)
        return self._start_date + delta

    def get_period(self):
        """
        Get the dataset period in seconds (assumes evenly spaced)
        :return: Dataset period in seconds or None if not calculable
        """
        total_time = self._time[-1] - self._time[0]
        npoints = self.get_number_of_times()
        if npoints > 0:
            return total_time / (npoints - 1)

    def get_number_of_times(self):
        """
        Get the number of timestamps
        :return: Number of timestamps
        """
        return len(self._time)

    def get_data_at(self, lat, lon, date):
        """
        Get the value of the independent variable at a specified location and datetime
        :param lat: Latitude to get at
        :param lon: Longitude to get at
        :param date: Datetime to get at
        :return: The data value at that time/space
        """
        # First we identify the closest positions we can use (by index):
        lat_index, lon_index = self._get_lat_lon_index(lat, lon)
        time_secs_elapsed = self._get_seconds_elapsed(date)
        time_index = self._get_closest_value_index(self._time, time_secs_elapsed)

        # try and use cache:
        if time_index in self._cache_dict and self._cache_lat_lon == (lat_index, lon_index):
            return self._cache_dict[time_index]

        # Save cache
        if time_index + constants.USER_DOWNLOAD_CACHE_SIZE < len(self._time):
            vals_array = self._variable.array[time_index: time_index + constants.USER_DOWNLOAD_CACHE_SIZE,
                                              lat_index, lon_index].tolist()
        else:
            vals_array = self._variable.array[time_index:, lat_index, lon_index].tolist()
        vals = [val[0][0] for val in vals_array]
        time_indices = [time_index + i for i in range(0, constants.USER_DOWNLOAD_CACHE_SIZE)]

        self._cache_dict = {time: val for time, val in zip(time_indices, vals)}
        self._cache_lat_lon = lat_index, lon_index

        return self._cache_dict[time_index]

    def _get_variable_to_plot(self):
        """
        Identify the independent variable we wish to plot
        :return: The first independent variable
        """
        keys = self._dataset.keys()
        variables = []
        for key in keys:
            if key not in [
                    self._get_key(NETCDF_LATITUDE),
                    self._get_key(NETCDF_LONGITUDE),
                    self._get_key(NETCDF_TIME),
                    self._get_key(NETCDF_TIME_BOUNDS),
                    self._get_key(NETCDF_CRS),
                    self._get_key(NETCDF_CRS_X),
                    self._get_key(NETCDF_CRS_Y)]:
                variables.append(self._dataset[key])
                self._variable_names.append(key)
        return variables[0]  # Do we want to only return the first variable?

    def _get_data_start_date(self):
        """
        Get the start date of the data as a datetime (rather than as seconds after some arbitrary time)
        :return: Datetime representing the data start date
        """
        return parse(0, self._time_units)

    def _get_seconds_elapsed(self, datetime):
        """
        Converts a datetime into seconds since the dataset started
        :param datetime:
        :return:
        """
        time_secs_elapsed = (datetime - self._start_date).total_seconds()
        return time_secs_elapsed

    def is_transect(self):
        """
        Determines if a given file is a transect (i.e. is only one cell wide or tall)
        :return: True if transect, False otherwise
        """
        height = len(self._lat)
        width = len(self._lon)
        return height == 1 or width == 1

    def get_timestamps(self):
        """
        Returns a list of all available timestamps for the dataset
        :return:
        """
        timevalues = self._time.tolist()
        return [self._start_date + datetime.timedelta(seconds=timeval) for timeval in timevalues]
