"""
header
"""
import datetime
from coards import parse
import math
from pylons import config
from joj.services.dap_client.dap_client import DapClient
from joj.utils import constants


class GraphingDapClient(DapClient):
    """
    Dap Client class for providing data for the Flot visualisation graphs.
    """

    def __init__(self, url):
        if 'run_in_test_mode' in config and config['run_in_test_mode'].lower() == 'true':
            return
        super(GraphingDapClient, self).__init__(url)
        self.gse_lat_n = self._dataset.attributes['NC_GLOBAL']['geospatial_lat_max']
        self.gse_lat_s = self._dataset.attributes['NC_GLOBAL']['geospatial_lat_min']
        self.gse_lon_w = self._dataset.attributes['NC_GLOBAL']['geospatial_lon_min']
        self.gse_lon_e = self._dataset.attributes['NC_GLOBAL']['geospatial_lon_max']

    def get_graph_data(self, lat, lon, time, npoints=constants.GRAPH_NPOINTS):
        """
        Get the time series graphing data for a given point
        :param lat: Latitude of point to graph
        :param lon: Longitude of point to graph
        :param time: Time to graph around
        :param npoints: Max number of points to plot
        :return: JSON-like dictionary of data and metadata
        """
        # First we identify the closest positions we can use (by index):
        is_inside_grid = (self.gse_lat_s <= lat <= self.gse_lat_n) and (self.gse_lon_w <= lon <= self.gse_lon_e)

        lat_index, lon_index = self._get_lat_lon_index(lat, lon)
        if time is None:
            plot_point_time_index = 0
        else:
            time_elapsed = self._get_seconds_elapsed(time)
            plot_point_time_index = self._get_closest_value_index(self._time, time_elapsed)
        time_index_start = int(max(plot_point_time_index - math.floor((npoints - 1) / 2.0), 0))
        time_index_end = int(min(plot_point_time_index + math.ceil((npoints - 1) / 2.0), len(self._time) - 1))

        # Assumes that dimensions are time, lat, long.
        data_slice = self._variable.array[time_index_start:time_index_end + 1, lat_index, lon_index]
        variable_data = [data[0][0] for data in data_slice.tolist()]
        timestamps = self._time.tolist()
        data = []
        missing_value = self._variable.missing_value
        fill_value = self._variable._FillValue
        for i in range(len(variable_data)):
            time_index = time_index_start + i
            # Time should be in millis after 1970 epoch for FLOT
            t = self._get_millis_since_epoch(timestamps[time_index])
            if is_inside_grid:
                data_value = variable_data[i]
                if data_value == missing_value or data_value == fill_value or math.isnan(data_value):
                    data_value = None
            else:
                data_value = None
            data.append([t, data_value])
        min_data_value = min(variable_data)
        max_data_value = max(variable_data)
        return {'data': data,
                'label': "%s (%s)" % (self.get_longname(), self._variable.units),
                'lat': lat,
                'lon': lon,
                'xmin': self._get_millis_since_epoch(min(timestamps)),
                'xmax': self._get_millis_since_epoch(max(timestamps)),
                'ymin': min_data_value,
                'ymax': max_data_value
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