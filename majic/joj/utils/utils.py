"""
header
"""
from joj.utils import constants


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
    if value_in_mb is not None:
        return round(int(value_in_mb) / 1024.0, 1)
    else:
        return 0


def convert_time_period_to_name(time_in_seconds):
    """
    Convert time period from seconds to english if possible
    :param time_in_seconds: the time in seconds (-1 is monthly, and -2 is yearly)
    :return: description of time period e.g. Hourly or every x seconds
    """

    if time_in_seconds is None or time_in_seconds == 0:
        return 'Unknown time period'
    if time_in_seconds == constants.JULES_MONTHLY_PERIOD:
        return 'Monthly'
    if time_in_seconds == constants.JULES_YEARLY_PERIOD:
        return 'Yearly'
    if time_in_seconds == constants.JULES_DAILY_PERIOD:
        return 'Daily'
    if time_in_seconds == 60*60:
        return 'Hourly'
    if time_in_seconds % 60 == 0:
        minutes = time_in_seconds / 60
        return 'Every {} minutes'.format(minutes)
    return 'Every {} seconds'.format(time_in_seconds)