"""
header
"""


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
