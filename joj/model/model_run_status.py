# Header


from joj.model.meta import Base
from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship, backref
from joj.utils import constants


class ModelRunStatus(Base):
    """The status of the model run
    """

    __tablename__ = 'model_run_statuses'

    def __init__(self, name):
        """initiaise
           -- name the name for the status
        """
        self.name = name

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))

    def __repr__(self):
        """String representation"""

        return "<ModelRunStatus(name=%s)>" % self.name
