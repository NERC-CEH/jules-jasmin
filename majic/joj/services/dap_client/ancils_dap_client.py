"""
#    Majic
#    Copyright (C) 2014  CEH
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
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