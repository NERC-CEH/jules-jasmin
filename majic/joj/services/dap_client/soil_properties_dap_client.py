"""
header
"""
from pylons import config
from joj.services.dap_client.base_dap_client import BaseDapClient
from joj.utils import constants


class SoilPropertiesDapClient(BaseDapClient):
    """
    Specialised DAP Client class for accessing soil properties via THREDDS
    """

    def __init__(self, url):
        if 'run_in_test_mode' in config and config['run_in_test_mode'].lower() == 'true':
            return
        super(SoilPropertiesDapClient, self).__init__(url)

    def get_soil_properties(self, lat, lon):
        """
        Get the soil properties at a point
        :param lat: Latitude
        :param lon: Longitude
        :return: Dictionary of soil property values for each of the soil property variables
        """
        if 'run_in_test_mode' in config and config['run_in_test_mode'].lower() == 'true':
            return {'bexp': 0.9, 'sathh': 0.0, 'satcon': 0.0, 'vsat': 50.0, 'vcrit': 275.0, 'vwilt': 300.0,
                    'hcap': 10.0, 'hcon': 0.0, 'albsoil': 0.5}
        lat_index = self._get_closest_value_index(self._lat, lat)
        lon_index = self._get_closest_value_index(self._lon, lon)
        soil_props = {}
        for key in self._dataset.keys():
            if key not in (self._get_key(constants.NETCDF_LATITUDE), self._get_key(constants.NETCDF_LONGITUDE)):
                variable = self._dataset[key]
                missing_value = variable.missing_value
                value_as_grid = variable[lat_index, lon_index]
                value = value_as_grid[key][0][0]
                if value == missing_value:
                    return None
                soil_props[key] = value
        return soil_props