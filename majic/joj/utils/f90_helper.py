#header
from f90nml import to_f90str


def python_to_f90_str(value):
    """
    Convert a python object to a Fortran 90 string
    :param value: Python object to convert
    :return: Fortran string
    """
    if type(value) == list:
        return ', '.join([to_f90str(v) for v in value])
    else:
        return to_f90str(value)
