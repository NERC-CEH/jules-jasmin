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
