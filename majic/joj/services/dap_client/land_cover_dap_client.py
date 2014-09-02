"""
header
"""
from pylons import config
from joj.services.dap_client.base_dap_client import BaseDapClient


class LandCoverDapClient(BaseDapClient):
    """
    Specialised DAP Client class for accessing land cover data via THREDDS
    """

    def __init__(self, url, key):
        if 'run_in_test_mode' in config and config['run_in_test_mode'].lower() == 'true':
            return
        super(LandCoverDapClient, self).__init__(url)
        self._frac = self._dataset[key]

    def get_fractional_cover(self, lat, lon):
        """
        Get the fractional land cover at a point
        :param lat: Latitude
        :param lon: Longitude
        :return: List of land cover fractional values for each of the land cover types
        """
        if 'run_in_test_mode' in config and config['run_in_test_mode'].lower() == 'true':
            return 8 * [0.125] + [0.0]
        lat_index = self._get_closest_value_index(self._lat, lat)
        lon_index = self._get_closest_value_index(self._lon, lon)
        frac_array = self._frac[:, lat_index, lon_index].tolist()
        return [val[0][0] for val in frac_array]
