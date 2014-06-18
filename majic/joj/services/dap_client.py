# header
import datetime
import re
from pydap.client import open_url
from joj.utils.constants import NETCDF_LATITUDE, NETCDF_LONGITUDE, NETCDF_TIME


class DapClient():
    """
    Client for communicating with the OpenDAP server to extract time series data for a particular latitude / longitude
    """

    def __init__(self, url):
        """
        Create a new DapClient for a specified dataset
        :param url: The URL of the OpenDAP dataset to look for
        """
        self._dataset = open_url(url)
        self._lat = self._dataset[NETCDF_LATITUDE][:]
        self._lon = self._dataset[NETCDF_LONGITUDE][:]
        self._time = self._dataset[NETCDF_TIME][:]
        self._variable = self._get_variable_to_plot()

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
            # Time should be in millis after 1970 epoch
            t = self._get_millis_since_epoch(timestamps[i])
            data.append([t, variable_data[i][0][0]])
        return {'data': data,
                'label': "%s (%s) @ %s, %s" % (self._variable.long_name, self._variable.units, lat, lon),
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
            if key not in [NETCDF_LATITUDE, NETCDF_LONGITUDE, NETCDF_TIME]:
                variables.append(self._dataset[key])
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

    def _get_millis_since_epoch(self, secs):
        """
        Convert a timestamp into milliseconds since the Unix epoch
        :param secs: The time to convert
        :return: milliseconds since the Unix epoch
        """
        epoch = datetime.datetime.utcfromtimestamp(0)
        time_units = self._dataset[NETCDF_TIME].units
        # The time axis does not start from the Unix epoch but from some other datetime specified
        # in the units which we find with a regex.
        start_date = re.findall(r'(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)', time_units)[0]
        date = datetime.datetime.strptime(start_date, "%Y-%m-%d %X")
        delta = date - epoch
        return (secs + delta.total_seconds()) * 1000
