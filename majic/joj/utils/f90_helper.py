"""
header
"""
import datetime
from f90nml import to_f90str
from numpy import float64
import re

DATE_TIME_FORMAT = "%Y-%m-%d %X"


def python_to_f90_str(value):
    """
    Convert a python object to a Fortran 90 string
    :param value: Python object to convert
    :return: Fortran string
    """
    if type(value) == list:
        return '    '.join([python_to_f90_str(v) for v in value])
    elif type(value) == datetime.datetime:
        return to_f90str(value.strftime(DATE_TIME_FORMAT))
    elif type(value) == float64:
        return to_f90str(float(value))
    elif type(value) == unicode:
        return to_f90str(str(value))
    else:
        return to_f90str(value)


def f90_str_to_python(value, is_list=False):
    """
    Convert a Fortran 90 namelist value to a Python object
    :param value: F90 value string to convert
    :param is_list: Indicates whether the value is a list
    :return: Corresponding Python object
    """
    if value is None:
        return None
    if type(value) == unicode:
        value = str(value)
    if is_list:
        return _from_list(value)
    if _is_datetime(value):
        return _from_datetime(value)
    if _is_string(value):
        return _from_string(value)
    if _is_bool(value):
        return _from_bool(value)
    if _is_int(value):
        return _from_int(value)
    if _is_float(value):
        return _from_float(value)


def _from_list(f_list):
    """
    Convert a namelist list into a Python list
    :param f_list: Fortran list to convert
    :return: Python list
    """
    #First try a string list (includes datetimes)
    py_list = re.findall("('.*?')", f_list)
    if len(py_list) == 0:
        #Finally try booleans
        py_list = re.findall("((?:\.false\.)|(?:\.true\.)|(?:false)|(?:true)|(?:t)|(?:f))", f_list.lower())
    if len(py_list) == 0:
        # Then try numbers
        py_list = re.findall("([\deE+-\.]+)", f_list)
    return [f90_str_to_python(v) for v in py_list]


def _is_string(value):
    """
    Determine if a fortran namelist string represents a Python string
    :param value: Value to test
    :return: True if a Python string, false otherwise
    """
    # This case would pass the test below but is not a valid string
    if value == "'":
        return False
    return value[0] == "'" and value[len(value) - 1] == "'"


def _from_string(f_string):
    """
    Convert a namelist string into a Python string
    :param f_string: Fortran string to convert
    :return: Python string
    """
    if f_string == "''":
        return None
    return f_string[1:len(f_string) - 1]


def _is_bool(value):
    """
    Determine if a fortran namelist string represents a Python string
    :param value: Value to test
    :return: True if a Python string, false otherwise
    """
    return _from_bool(value) is not None


def _from_bool(f_bool):
    """
    Convert a namelist bool into a Python boolean
    :param f_bool: Fortran bool to convert
    :return: Python boolean
    """
    if f_bool.lower() in [".false.", "f", "false"]:
        return False
    elif f_bool.lower() in [".true.", "t", "true"]:
        return True
    return None


def _is_int(value):
    """
    Determine if a fortran namelist string represents a Python int
    :param value: Value to test
    :return: True if a Python int, false otherwise
    """
    try:
        int(value)
    except ValueError:
        return False
    return True


def _from_int(f_int):
    """
    Convert a namelist int into a Python int
    :param f_int: Fortran int to convert
    :return: Python int
    """
    return int(f_int)


def _is_float(value):
    """
    Determine if a fortran namelist string represents a Python float
    :param value: Value to test
    :return: True if a Python float, false otherwise
    """
    try:
        float(value)
    except ValueError:
        return False
    return True


def _from_float(f_float):
    """
    Convert a namelist float into a Python float
    :param f_float: Fortran float to convert
    :return: Python float
    """
    return float(f_float)


def _is_datetime(value):
    """
    Determine if a fortran namelist string represents a Python float
    :param value: Value to test
    :return: True if a Python float, false otherwise
    """
    # Need to deconvert from string first
    if not _is_string(value):
        return False
    value = _from_string(value)
    try:
        datetime.datetime.strptime(value, DATE_TIME_FORMAT)
    except ValueError:
        return False
    return True


def _from_datetime(f_datetime):
    """
    Convert a namelist datetime into a Python datetime
    :param f_datetime: Fortran datetime to convert
    :return: Python datetime
    """
    if not _is_string(f_datetime):
        return False
    f_datetime = _from_string(f_datetime)
    return datetime.datetime.strptime(f_datetime, DATE_TIME_FORMAT)