"""
# header
"""
import datetime
import re
from pydap.client import open_url
from joj.utils.constants import NETCDF_LATITUDE, NETCDF_LONGITUDE, NETCDF_TIME, NETCDF_TIME_BOUNDS
from joj.utils import constants


class DapClient(object):
    """
    Client for communicating with the OpenDAP server to extract time series data for a particular latitude / longitude
    """

    def __init__(self, url):
        """
        Create a new DapClient for a specified dataset
        :param url: The URL of the OpenDAP dataset to look for
        """
        self._dataset = open_url(url)

        self._lat = self._dataset[self._get_key(NETCDF_LATITUDE)][:]
        self._lon = self._dataset[self._get_key(NETCDF_LONGITUDE)][:]
        self._time = self._dataset[self._get_key(NETCDF_TIME)][:]
        self.start_date = self.get_data_start_date()
        self.variable_names = []
        self._variable = self._get_variable_to_plot()
        self.cache_dict = {}
        self.cache_lat = None
        self.cache_lon = None

    def get_graph_data(self, lat, lon):
        """
        Get the time series graphing data for a given point
        :param lat: Latitude of point to graph
        :param lon: Longitude of point to graph
        :return: JSON-like dictionary of data and metadata
        """
        # First we identify the closest positions we can use (by index):
        lat_index = self._get_closest_value_index(self._lat, lat)
        lon_index = self._get_closest_value_index(self._lon, lon)

        # Assumes that dimensions are time, lat, long.
        variable_data = self._variable.array[:, lat_index, lon_index].tolist()
        timestamps = self._time.tolist()
        data = []
        for i in range(len(variable_data)):
            # Time should be in millis after 1970 epoch for FLOT
            t = self._get_millis_since_epoch(timestamps[i])
            data.append([t, variable_data[i][0][0]])
        return {'data': data,
                'label': "%s (%s) @ %s, %s" % (self.get_longname(), self._variable.units, lat, lon),
                'lat': lat,
                'lon': lon,
                'xmin': self._get_millis_since_epoch(min(timestamps)),
                'xmax': self._get_millis_since_epoch(max(timestamps)),
                'ymin': min(variable_data),
                'ymax': max(variable_data)
        }

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
                self._get_key(NETCDF_TIME_BOUNDS)]:
                variables.append(self._dataset[key])
                self.variable_names.append(key)
        return variables[0]  # Do we want to only return the first variable?

    def _get_closest_value_index(self, data, value):
        """
        Utility method to identify the closest data point in a list for a given value
        :param data: List of data points
        :param value: Value to search close to
        :return: The index of the closest point in the list
        """
        # Won't always get the one we expect but will always be equally close (e.g. 6.5 might go to 6 not 7)
        return min(range(len(data)), key=lambda i: abs(data[i] - value))

    def get_data_start_date(self):
        """
        Get the start date of the data as a datetime (rather than as seconds after some arbitrary time)
        :return: Datetime representing the data start date
        """
        time_units = self._dataset[self._get_key(NETCDF_TIME)].units
        # The time axis does not start from the Unix epoch but from some other datetime specified
        # in the units which we find with a regex.
        start_date = re.findall(r'(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)', time_units)[0]
        date = datetime.datetime.strptime(start_date, "%Y-%m-%d %X")
        return date

    def _get_millis_since_epoch(self, secs):
        """
        Convert a timestamp into milliseconds since the Unix epoch
        :param secs: The time to convert
        :return: milliseconds since the Unix epoch
        """
        epoch = datetime.datetime.utcfromtimestamp(0)
        delta = self.start_date - epoch
        return (secs + delta.total_seconds()) * 1000

    def get_longname(self):
        """
        The longname of the variable in this dataset
        :return: the long name
        """
        try:
            return self._variable.attributes['long_name']
        except KeyError:
            return self.variable_names[0]

    def get_data_range(self):
        """
        Gets the datarange of the variable in this dataset
        :return: min and max tuple for the range
        """
        try:
            return [self._variable.attributes['valid_min'], self._variable.attributes['valid_max']]
        except KeyError:
            return [0, 100]

    def _get_key(self, var_names):
        """
        Try to find the key in the list of variables (make it case insensitive)
        :param var_names: list of possible variable name
        :return: the key
        """
        for key in self._dataset.keys():
            for possible_var_name in var_names:
                if key.lower() == possible_var_name.lower():
                    return key
        return var_names[0]

    def get_variable_units(self):
        """
        Get the units for the independent variable
        :return:
        """
        return self._dataset[self.variable_names[0]].units

    def get_time_immediately_after(self, time):
        """
        Get the timestamp of the next data point after a specified time
        :param time: Datetime to search after
        :return: Datetime of next data point
        """
        time_secs_elapsed = self.get_seconds_elapsed(time)
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
        return self.start_date + delta

    def get_time_immediately_before(self, time):
        """
        Get the timestamp of the previous data point before a specified time
        :param time: Datetime to search before
        :return: Datetime of previous data point
        """
        time_secs_elapsed = self.get_seconds_elapsed(time)
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
        return self.start_date + delta

    def get_seconds_elapsed(self, datetime):
        """
        Converts a datetime into seconds since the dataset started
        :param datetime:
        :return:
        """
        time_secs_elapsed = (datetime - self.start_date).total_seconds()
        return time_secs_elapsed

    def get_data_at(self, lat, lon, date):
        """
        Get the value of the independent variable at a specified location and datetime
        :param lat: Latitude to get at
        :param lon: Longitude to get at
        :param date: Datetime to get at
        :return: The data value at that time/space
        """
        # First we identify the closest positions we can use (by index):
        lat_index = self._get_closest_value_index(self._lat, lat)
        lon_index = self._get_closest_value_index(self._lon, lon)
        time_secs_elapsed = self.get_seconds_elapsed(date)
        time_index = self._get_closest_value_index(self._time, time_secs_elapsed)

        # try and use cache:
        if time_index in self.cache_dict:
            return self.cache_dict[time_index]

        ## Save cache
        if time_index + constants.USER_DOWNLOAD_CACHE_SIZE < len(self._time):
            vals_array = self._variable.array[time_index: time_index + constants.USER_DOWNLOAD_CACHE_SIZE,
                                              lat_index, lon_index].tolist()
        else:
            vals_array = self._variable.array[time_index:, lat_index, lon_index].tolist()
        vals = [val[0][0] for val in vals_array]
        time_indices = [time_index + i for i in range(0, constants.USER_DOWNLOAD_CACHE_SIZE)]

        self.cache_dict = {time: val for time, val in zip(time_indices, vals)}

        return self.cache_dict[time_index]

    def get_closest_lat_lon(self, lat, lon):
        """
        Get the closest latitude / longitude coordinates in the driving data grid
        :param lat: Latitude
        :param lon: Longitude
        :return: Lat, lon
        """
        lat_index = self._get_closest_value_index(self._lat, lat)
        lon_index = self._get_closest_value_index(self._lon, lon)

        lat = float(self._lat[lat_index])
        lon = float(self._lon[lon_index])

        return lat, lon
