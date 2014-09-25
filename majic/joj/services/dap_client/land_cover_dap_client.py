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
        lat_index, lon_index = self._get_lat_lon_index(lat, lon)
        frac_array = self._frac[:, lat_index, lon_index].tolist()
        return [val[0][0] for val in frac_array]
