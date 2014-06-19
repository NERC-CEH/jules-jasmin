"""
header
"""

import datetime

from sqlalchemy import Column, Integer, String, DateTime, BigInteger, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship, backref
from joj.model.meta import Base
from joj.utils import constants
from joj.model import ModelRunStatus


class ModelRun(Base):
    """ A single run of a model """

    __tablename__ = 'model_runs'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))
    description = Column(String(constants.DB_LONG_STRING_SIZE))
    user_id = Column(Integer, ForeignKey('users.id'))
    date_created = Column(DateTime)
    date_submitted = Column(DateTime)
    date_started = Column(DateTime)
    last_status_change = Column(DateTime)
    time_elapsed_secs = Column(BigInteger)
    status_id = Column(SmallInteger, ForeignKey('model_run_statuses.id'))
    code_version_id = Column(SmallInteger, ForeignKey('code_versions.id'))
    science_configuration_id = Column(Integer, ForeignKey('model_runs.id'))

    user = relationship("User", backref=backref('model_runs', order_by=id))
    code_version = relationship("CodeVersion", backref=backref('model_runs', order_by=id))
    datasets = relationship("Dataset", backref=backref('model_run', order_by=id), lazy="joined")
    parameter_values = relationship("ParameterValue", backref=backref('model_run', order_by=id))
    status = relationship("ModelRunStatus", backref=backref('model_runs', order_by=id), lazy="joined")

    def change_status(self, session, new_status):
        """
        Change the status of the model run object. Will also update dates
        :param session: session used to get the staus id
        :param new_status: the name of the status
        :return: the new status object
        """
        status = session.query(ModelRunStatus) \
            .filter(ModelRunStatus.name == new_status) \
            .one()
        self.status = status
        self.last_status_change = datetime.datetime.now()
        if new_status == constants.MODEL_RUN_STATUS_PENDING:
            self.date_submitted = datetime.datetime.now()
        elif new_status == constants.MODEL_RUN_STATUS_CREATED:
            self.date_created = datetime.datetime.now()
        return status

    def get_parameter_value(self, param_name, param_namelist):
        """
        Gets the value of a specified parameter
        :param param_namelist: name of namelist parameter belongs to
        :param param_name: name of parameter to find
        """
        for param_val in self.parameter_values:
            if param_val.parameter.name == param_name:
                if param_val.parameter.namelist.name == param_namelist:
                    return param_val.value

    def __repr__(self):
        """ String representation of the model run """

        return "<ModelRun(name=%s, date submitted=%s)>" % (self.name, self.date_submitted)
