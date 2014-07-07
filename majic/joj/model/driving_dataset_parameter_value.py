"""
# header
"""
from sqlalchemy import Integer, Column, ForeignKey, String
from sqlalchemy.orm import relationship, backref
from joj.model import Base
from joj.utils import constants


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
        super(DrivingDatasetParameterValue, self).__init__()
        parameter = model_run_service.get_parameter_by_constant(jules_param_constant)
        self.driving_dataset=driving_dataset
        self.parameter_id=parameter.id
        self.value=value

    def __repr__(self):
        return "<DrivingDatasetParameterValue(parameter_id=%s, value=%s>" % self.parameter_id, self.value
