"""
header
"""
from pylons import config
from joj.services.dap_client.base_dap_client import BaseDapClient


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
        :return: List of soil property values for each of the soil property variables
        """
        if 'run_in_test_mode' in config and config['run_in_test_mode'].lower() == 'true':
            return
        #todo
        pass