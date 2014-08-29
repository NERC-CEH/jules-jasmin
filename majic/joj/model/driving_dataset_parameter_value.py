"""
# header
"""
from sqlalchemy import Integer, Column, ForeignKey, String
from sqlalchemy.orm import relationship, backref
from joj.model import Base
from joj.utils import constants, f90_helper


class DrivingDatasetParameterValue(Base):
    """
    The model class for parameter values stored against a driving dataset
    """

    __tablename__ = 'driving_dataset_parameter_values'

    id = Column(Integer, primary_key=True)
    parameter_id = Column(Integer, ForeignKey('parameters.id'))
    value = Column(String(constants.DB_PARAMETER_VALUE_STRING_SIZE))
    driving_dataset_id = Column(Integer, ForeignKey('driving_datasets.id'))
    driving_dataset = relationship("DrivingDataset", backref=backref('parameter_values', order_by=id))

    def __init__(self, model_run_service,  driving_dataset, jules_param_constant, value):
        """
        Initialise
        :param model_run_service: model run service
        :param driving_dataset: driving data set to add parameter value to
        :param jules_param_constant: either constant tuple for a namelist parameter or the parameters id
        :param value: python value
        :return:nothing
        """
        super(DrivingDatasetParameterValue, self).__init__()
        if type(jules_param_constant) is int:
            self.parameter_id = jules_param_constant
        else:
            parameter = model_run_service.get_parameter_by_constant(jules_param_constant)
            self.parameter_id = parameter.id
        self.driving_dataset = driving_dataset
        self.value = value

    def __repr__(self):
        return "<DrivingDatasetParameterValue(parameter_id=%s, value=%s>" % self.parameter_id, self.value

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
        :return: Python type
        :param is_list: Indicates whether this value is a list
        """
        return f90_helper.f90_str_to_python(self.value, is_list)