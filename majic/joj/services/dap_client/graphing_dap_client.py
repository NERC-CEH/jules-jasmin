"""
header
"""
import datetime
from coards import parse
from joj.services.dap_client.dap_client import DapClient


class GraphingDapClient(DapClient):
    """
    Dap Client class for providing data for the Flot visualisation graphs.
    """

    def __init__(self, url):
        super(GraphingDapClient, self).__init__(url)

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
        variable_data = [data[0][0] for data in self._variable.array[:, lat_index, lon_index].tolist()]
        timestamps = self._time.tolist()
        data = []
        for i in range(len(variable_data)):
            # Time should be in millis after 1970 epoch for FLOT
            t = self._get_millis_since_epoch(timestamps[i])
            data.append([t, variable_data[i]])
        return {'data': data,
                'label': "%s (%s) @ %s, %s" % (self.get_longname(), self._variable.units, lat, lon),
                'lat': lat,
                'lon': lon,
                'xmin': self._get_millis_since_epoch(min(timestamps)),
                'xmax': self._get_millis_since_epoch(max(timestamps)),
                'ymin': min(variable_data),
                'ymax': max(variable_data)
                }

    def _get_millis_since_epoch(self, intervals):
        """
        Convert a timestamp into milliseconds since the Unix epoch (needed for Flot)
        :param intervals: The time interval to convert (eg number of seconds since)
        :return: milliseconds since the Unix epoch
        """
        epoch = datetime.datetime.utcfromtimestamp(0)
        time = parse(intervals, self._time_units)
        delta = time - epoch
        return delta.total_seconds() * 1000