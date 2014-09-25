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


def insert_before_file_extension(path, string):
    """
    Add a string to a path immediately before the file extension
    :param path: File path to modify
    :param string: String to add
    :return:
    """
    file_extens_idx = path.rfind('.')
    return "".join((path[0:file_extens_idx], string, path[file_extens_idx:]))


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


def _is_list(is_list, parameter_namelist_name):
    is_list_local = is_list
    if is_list is None:
        if len(parameter_namelist_name) >= 3:
            is_list_local = parameter_namelist_name[2]
        else:
            is_list_local = False
    return is_list_local


def find_first_parameter_value_in_param_vals_list(parameter_values, parameter_namelist_name, is_list=None):
    """
        Gets the value of the first matching parameter value as a python object
        :param parameter_values: parameter value to search through
        :param parameter_namelist_name: list containing [namelist, name, is_list] of parameter to find
            if is_list is not present defaults to false
        :param is_list: Indicates whether the value is a list, overrides constant
        :return parameter value as python or None
        """
    is_list_local = _is_list(is_list, parameter_namelist_name)
    for param_val in parameter_values:
        if param_val.parameter.name == parameter_namelist_name[1]:
            if param_val.parameter.namelist.name == parameter_namelist_name[0]:
                return param_val.get_value_as_python(is_list=is_list_local)
    return None


def get_first_parameter_value_from_parameter_list(parameters, parameter_namelist_name, is_list=False, group_id=None):
    """
    Get a parameter value from a list of parameters
    :param parameters: List of parameters
    :param parameter_namelist_name: namelist and name of parameter to get
    :param is_list: Return as list
    :return: First matching parameter value as Python
    """
    is_list_local = _is_list(is_list, parameter_namelist_name)
    for parameter in parameters:
        if parameter.namelist.name == parameter_namelist_name[0]:
            if parameter.name == parameter_namelist_name[1]:
                if len(parameter.parameter_values) > 0:
                    if group_id is None:
                        return parameter.parameter_values[0].get_value_as_python(is_list=is_list_local)
                    else:
                        group_params = [param for param in parameter.parameter_values if param.group_id == group_id]
                        if len(group_params) > 0:
                            return group_params[0].get_value_as_python(is_list=is_list_local)
    return None


def set_parameter_value_in_parameter_list(parameters, parameter_namelist_name, python_value):
    """
    Set a parameter value in a list of parameters
    :param parameters: List of parameters
    :param parameter_namelist_name: namelist and name of parameter to set
    :param python_value: value to set
    :return:
    """
    for parameter in parameters:
        if parameter.namelist.name == parameter_namelist_name[0]:
            if parameter.name == parameter_namelist_name[1]:
                if len(parameter.parameter_values) > 0:
                    parameter.parameter_values[0].set_value_from_python(python_value)