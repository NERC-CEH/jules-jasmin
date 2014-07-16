"""
header
"""


class KeyNotFound(Exception):
    """
    Thrown when a key is not found in a list
    """

    def __init__(self, id_to_match=None):
        self.message = "Key not found in list. Key was %s", str(id_to_match)


def find_by_id(values, id_to_match):
    """
    Find a value in values which has the id id_to_match
    :param values: the list of possible values
    :param id_to_match: the id to match
    :return: the matched value or thrown KeyNotFound exception if it is not in the list
    """
    for value in values:
        if value.id == id_to_match:
            return value

    raise KeyNotFound(id_to_match)


def find_by_id_in_dict(values, id_to_match):
    """
    Find a value in values which are dictionaries with the id id_to_match
    :param values: the list of possible values
    :param id_to_match: the id to match
    :return: the matched value or thrown KeyNotFound exception if it is not in the list
    """
    for value in values:
        if value['id'] == id_to_match:
            return value

    raise KeyNotFound(id_to_match)


def convert_mb_to_gb_and_round(value_in_mb):
    """
    Convert a value from MB to GB and round it to the nearest 1dp
    :param value_in_mb: value in MB
    :return: value in GB to 1dp
    """
    return round(int(value_in_mb) / 1024.0, 1)