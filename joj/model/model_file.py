from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from joj.model.meta import Base
from joj.utils import constants


class ModelFile(Base):
    """ Represents an input or output file used in a model run """

    __tablename__ = 'model_files'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))
    path = Column(String(constants.DB_PATH_SIZE))
    is_input = Column(Boolean)
    model_run_id = Column(Integer, ForeignKey('model_runs.id'))

    def __repr__(self):
        """ String representation of the Model File"""

        return "<ModelFile(name=%s, path=%s)>" % (self.name, self.path)