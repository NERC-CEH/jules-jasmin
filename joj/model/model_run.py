# Header

from sqlalchemy import Column, Integer, String, DateTime, BigInteger, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship, backref
from joj.model.meta import Base
from joj.utils import constants


class ModelRun(Base):
    """ A single run of a model """

    __tablename__ = 'model_runs'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))
    user_id = Column(Integer, ForeignKey('users.id'))
    date_submitted = Column(DateTime)
    date_started = Column(DateTime)
    time_elapsed_secs = Column(BigInteger)
    status_id = Column(SmallInteger, ForeignKey('model_run_statuses.id'))
    code_version_id = Column(SmallInteger, ForeignKey('code_versions.id'))

    code_version = relationship("CodeVersion", backref=backref('model_runs', order_by=id))
    files = relationship("ModelFile", backref=backref('model_files', order_by=id))
    parameter_values = relationship("ParameterValue", backref=backref('model_run', order_by=id))
    status = relationship("ModelRunStatus", backref=backref('model_runs', order_by=id))

    def __repr__(self):
        """ String representation of the model run """

        return "<ModelRun(name=%s, date submitted=%s)>" % (self.name, self.date_submitted)

