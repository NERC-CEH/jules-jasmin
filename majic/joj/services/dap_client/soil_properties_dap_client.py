"""
header
"""
import logging
from urllib2 import HTTPError
from pylons import config
from joj.services.dap_client.base_dap_client import BaseDapClient
from joj.services.general import ServiceException

log = logging.getLogger(__name__)


class SoilPropertiesDapClient(BaseDapClient):
    """
    Specialised DAP Client class for accessing soil properties via THREDDS
    """

    def __init__(self, url):
        if 'run_in_test_mode' in config and config['run_in_test_mode'].lower() == 'true':
            return
        super(SoilPropertiesDapClient, self).__init__(url)

    def get_soil_properties(self, lat, lon, var_names_in_file, use_file_list, const_vals):
        """
        Get the soil properties at a point
        :param lat: Latitude
        :param lon: Longitude
        :param var_names_in_file: variable names in the soil properties file
        :param use_file_list: whether a file is used for the variable
        :param const_vals: the contant values if used
        :return: Dictionary of soil property values for each of the soil property variables
        """
        if 'run_in_test_mode' in config and config['run_in_test_mode'].lower() == 'true':
            return {'bexp': 0.9, 'sathh': 0.0, 'satcon': 0.0, 'vsat': 50.0, 'vcrit': 275.0, 'vwilt': 300.0,
                    'hcap': 10.0, 'hcon': 0.0, 'albsoil': 0.5}
        try:
            lat_index, lon_index = self._get_lat_lon_index(lat, lon)
            soil_props = {}
            use_files_or_default = use_file_list
            if use_file_list is None:
                use_files_or_default = [True] * len(var_names_in_file)
            const_vals_or_default = const_vals
            if const_vals is None:
                const_vals_or_default = [None] * len(var_names_in_file)
            for var_name, use_file, const_value in zip(var_names_in_file, use_files_or_default, const_vals_or_default):
                if use_file:
                    variable = self._dataset[var_name]
                    missing_value = variable.attributes.get('missing_value', None)
                    fill_value = variable.attributes.get('_FillValue', None)
                    if len(variable.shape) == 3:
                        value_as_grid = variable[0, lat_index, lon_index]
                        value = value_as_grid.flat[0]
                    else:
                        value_as_grid = variable[lat_index, lon_index]
                        value = value_as_grid[var_name][0][0]
                    if value == missing_value or value == fill_value:
                        return None
                    soil_props[var_name] = value
                else:
                    soil_props[var_name] = const_value
            return soil_props
        except HTTPError:
            log.exception("Trouble reading soil properties from the file")
            raise ServiceException("Trouble reading soil properties from the file")