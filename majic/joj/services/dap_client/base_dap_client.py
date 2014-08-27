"""
header
"""
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
        except Exception:
            log.exception("Can not open the dataset URL '%s'." % url)
            raise DapClientException("Can not open the dataset URL.")

        try:
            self._lat = self._dataset[self._get_key(constants.NETCDF_LATITUDE)][:]
            self._lon = self._dataset[self._get_key(constants.NETCDF_LONGITUDE)][:]
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
