"""
header
"""
from joj.services.dap_client.base_dap_client import BaseDapClient
from joj.utils import constants


class AncilsDapClient(BaseDapClient):
    """
    AncilsDapClient
    """

    def get_variable_names(self):
        """
        Get the names of all the (non-spatial) variables
        :return: List of names
        """
        variable_names = []
        for key in self._dataset.keys():
            if key not in constants.NETCDF_LATITUDE and key not in constants.NETCDF_LONGITUDE:
                variable_names.append(self._dataset[key].attributes['long_name'])
        return variable_names