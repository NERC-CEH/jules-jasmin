"""
header
"""

import datetime

from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, SmallInteger, ForeignKey, Float
from joj.model.meta import Base
from joj.utils import constants, utils
from joj.model import ModelRunStatus


class ModelRun(Base):
    """ A single run of a model """

    __tablename__ = 'model_runs'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))
    description = Column(String(constants.DB_LONG_STRING_SIZE))
    error_message = Column(String(constants.DB_LONG_STRING_SIZE))
    user_id = Column(Integer, ForeignKey('users.id'))
    date_created = Column(DateTime)
    date_submitted = Column(DateTime)
    date_started = Column(DateTime)
    last_status_change = Column(DateTime)
    time_elapsed_secs = Column(BigInteger)
    status_id = Column(SmallInteger, ForeignKey('model_run_statuses.id'))
    code_version_id = Column(SmallInteger, ForeignKey('code_versions.id'))
    science_configuration_id = Column(Integer, ForeignKey('model_runs.id'))
    driving_dataset_id = Column(Integer, ForeignKey('driving_datasets.id'))
    driving_data_lat = Column(Float)
    driving_data_lon = Column(Float)
    driving_data_rows = Column(Integer)
    land_cover_frac = Column(String(constants.DB_STRING_SIZE))

    # amount of storage the run takes up excluding the common driving data sets,
    # only set when a run is failed or complete
    storage_in_mb = Column(BigInteger, default=0)

    user = relationship("User", backref=backref('model_runs', order_by=id))
    code_version = relationship("CodeVersion", backref=backref('model_runs', order_by=id))
    parameter_values = relationship("ParameterValue", backref=backref('model_run', order_by=id))
    status = relationship("ModelRunStatus", backref=backref('model_runs', order_by=id), lazy="joined")
    driving_dataset = relationship("DrivingDataset", backref=backref('model_runs', order_by=id), lazy="joined")

    def change_status(self, session, new_status, error_message=""):
        """
        Change the status of the model run object. Will also update dates
        :param session: session used to get the staus id
        :param new_status: the name of the status
        :param error_message: the error message associated with the new status default to blank
        :return: the new status object
        """
        status = session.query(ModelRunStatus) \
            .filter(ModelRunStatus.name == new_status) \
            .one()
        if self.status is None or self.status.id != status.id:
            self.last_status_change = datetime.datetime.now()
            self.status = status
        self.error_message = error_message[:constants.DB_LONG_STRING_SIZE]
        if new_status == constants.MODEL_RUN_STATUS_SUBMITTED:
            self.date_submitted = datetime.datetime.now()
        elif new_status == constants.MODEL_RUN_STATUS_CREATED:
            self.date_created = datetime.datetime.now()
        return status

    def get_parameter_values(self, parameter_namelist_name):
        """
        Gets all matching values of a specified parameter, sorted by group id and then Python value
        :param parameter_namelist_name: list containing [namelist, name] of parameter to find
        """
        param_vals = []
        for param_val in self.parameter_values:
            if param_val.parameter.name == parameter_namelist_name[1]:
                if param_val.parameter.namelist.name == parameter_namelist_name[0]:
                    param_vals.append(param_val)
        param_vals.sort(key=lambda pv: pv.get_value_as_python())
        param_vals.sort(key=lambda pv: pv.group_id)
        return param_vals

    def get_python_parameter_value(self, parameter_namelist_name, is_list=None):
        """
        Gets the value of the first matching parameter value as a python object
        :param parameter_namelist_name: list containing [namelist, name, is_list] of parameter to find
            if is_list is not present defaults to false
        :param is_list: Indicates whether the value is a list, overrides constant
        :return parameter value as python or None
        """
        return utils.find_parameter_values(self.parameter_values, parameter_namelist_name, is_list)

    def __repr__(self):
        """ String representation of the model run """

        return "<ModelRun(name=%s, date submitted=%s)>" % (self.name, self.date_submitted)
