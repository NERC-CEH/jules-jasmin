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

import numpy as np


class NetCdfHelper(object):
    """
    Helper class for NetCDF files
    """

    def look_for_key(self, keys, keys_to_look_for):
        """
        Search a list of keys for any key belonging to a set of keys to look for and return the first matching
        key (case-insensitive)
        :param keys: Keys to search through
        :param keys_to_look_for: List of keys to match against
        :return: First matching key
        """
        for possible_key in keys_to_look_for:
            for key in keys:
                if possible_key.lower() == key.lower():
                    return key

    def get_closest_value_index(self, list, value):
        """
        Get the 0-based index of the closest value in a list to a given value
        :param list: List to search
        :param value: Value to get closest to
        :return: Index of closest value
        """
        return min(range(len(list)), key=lambda i: abs(list[i] - value))

    def get_lat_lon_index(self, variables, lat_key, lon_key, lat_to_find, lon_to_find):
        """
        Get the lat and lon indexes for the poin closest to the given values
        :param variables: variables in the file
        :param lat_key: name of latitude in the dataset
        :param lon_key: name of longitude in the dataset
        :param lat_to_find: latitude to find
        :param lon_to_find: longitude to find
        :return: tuple of lat and lon indexes
        """

        if variables[lat_key].ndim == 1:
            lat_index = self.get_closest_value_index(variables[lat_key][:], lat_to_find)
            lon_index = self.get_closest_value_index(variables[lon_key][:], lon_to_find)

        else:
            lat_diff = np.array(variables[lat_key]) - lat_to_find
            lon_diff = np.array(variables[lon_key]) - lon_to_find

            indexes = np.argmin(lon_diff * lon_diff + lat_diff * lat_diff)
            lat_index = np.unravel_index(indexes, variables[lat_key].shape)[0]
            lon_index = np.unravel_index(indexes, variables[lat_key].shape)[1]

        return lat_index, lon_index