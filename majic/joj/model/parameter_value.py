"""
# Header
"""

from joj.model.meta import Base

from sqlalchemy import Column, Integer, String, ForeignKey
from joj.utils import constants
from joj.utils import f90_helper


class ParameterValue(Base):
    """A parameter value for a model run
    This is the definition of a parameter which is NOT the default value
    """

    __tablename__ = 'parameter_values'

    id = Column(Integer, primary_key=True)
    value = Column(String(constants.DB_PARAMETER_VALUE_STRING_SIZE))

    model_run_id = Column(Integer, ForeignKey('model_runs.id'))
    parameter_id = Column(Integer, ForeignKey('parameters.id'))
    group_id = Column(Integer)

    def duplicate_from(self, other):
        """
        Duplicate parameter value values from another instance of a parameter value
        :param other: the parameter value to copy
        :return: self
        """
        self.parameter_id = other.parameter_id
        self.value = other.value
        self.group_id = other.group_id
        return self

    def __repr__(self):
        """String representation"""

        return "<ParameterValue(value=%s)>" % self.value

    def set_value_from_python(self, value):
        """
        Set the Parameter value, converting a Python type to a Fortran namelist string
        :param value: Value to set (Python type)
        :return:
        """
        self.value = f90_helper.python_to_f90_str(value)

    def get_value_as_python(self, is_list=False):
        """
        Get the Parameter value, converting a Fortran namelist string to a Python type
        :param is_list: Indicates whether this value is a list
        :return: Python type
        """
        return f90_helper.f90_str_to_python(self.value, is_list)
