"""
header
"""
import numpy as np
import logging
from pydap.client import open_url
from pylons import config
from joj.lib.wmc_util import create_request_and_open_url
from joj.utils import constants

log = logging.getLogger(__name__)


class DapClientException(Exception):
    """
    Exception for when there is a problem in the dap client
    """
    pass


class BaseDapClient(object):
    """
    A basic DAP Client for accessing datasets on a THREDDS Server
    """

    def __init__(self, url):
        if 'run_in_test_mode' in config and config['run_in_test_mode'].lower() == 'true':
            return

        def new_request(url):
            """
            Create a new dap request
            :param url: the url
            :return: headers and body tuple
            """
            log = logging.getLogger('pydap')
            log.info('Opening %s' % url)

            f = create_request_and_open_url(url.rstrip('?&'))
            headers = dict(f.info().items())
            body = f.read()
            return headers, body

        from pydap import client

        client.request = new_request
        from pydap import proxy

        proxy.request = new_request
        try:
            # this is a modified open url. See pydap factory
            self._dataset = open_url(url)
            self.url = url
        except Exception:
            log.exception("Can not open the dataset URL '%s'." % url)
            raise DapClientException("Can not open the dataset URL.")

        try:
            self._lat = np.array(self._dataset[self._get_key(constants.NETCDF_LATITUDE)][:])
            self._lon = np.array(self._dataset[self._get_key(constants.NETCDF_LONGITUDE)][:])
        except Exception:
            log.exception("Can not read dataset '%s'." % url)
            raise DapClientException("Problems reading the dataset.")

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

    def _get_closest_value_index(self, data, value):
        """
        Utility method to identify the closest data point in a list for a given value
        :param data: List of data points
        :param value: Value to search close to
        :return: The index of the closest point in the list
        """
        # Won't always get the one we expect but will always be equally close (e.g. 6.5 might go to 6 not 7)
        return min(range(len(data)), key=lambda i: abs(data[i] - value))

    def _get_lat_lon_index(self, lat_to_find, lon_to_find):
        """
        Get the lat and lon indexes for the poin closest to the given values
        :param lat_to_find: latitude to find
        :param lon_to_find: longitude to find
        :return: tuple of lat and lon indexes
        """

        lat_index, lon_index = self._get_lat_lon_flattened_index(lat_to_find, lon_to_find)

        if self._lat.ndim > 1:
            lat_index = np.unravel_index(lat_index, self._lat.shape)[0]
            lon_index = np.unravel_index(lon_index, self._lon.shape)[1]

        return lat_index, lon_index

    def get_closest_lat_lon(self, lat_to_find, lon_to_find):
        """
        Get the closest latitude / longitude coordinates in the driving data grid
        :param lat_to_find: Latitude
        :param lon_to_find: Longitude
        :return: Lat, lon
        """
        if 'run_in_test_mode' in config and config['run_in_test_mode'].lower() == 'true':
            return lat_to_find, lon_to_find

        lat_ind, lon_ind = self._get_lat_lon_flattened_index(lat_to_find, lon_to_find)
        lat = self._lat.flat[lat_ind]
        lon = self._lon.flat[lon_ind]

        return lat, lon

    def _get_lat_lon_flattened_index(self, lat_to_find, lon_to_find):
        """
        Get the lat and lon indexes for the point closest to the given values
        :param lat_to_find: latitude to find
        :param lon_to_find: longitude to find
        :return: tuple of lat and lon indexes (if arrays are 2D this is the flatterned index)
        """

        if self._lat.ndim == 1:
            lat_index = self._get_closest_value_index(self._lat, lat_to_find)
            lon_index = self._get_closest_value_index(self._lon, lon_to_find)

        else:
            lat_diff = self._lat - lat_to_find
            lon_diff = self._lon - lon_to_find

            lat_index = lon_index = np.argmin(lon_diff * lon_diff + lat_diff * lat_diff)

        return lat_index, lon_index