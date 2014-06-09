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
        """initialise
           -- name the name for the status
        """
        self.name = name

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))

    def is_published(self):
        return self.name == constants.MODEL_RUN_STATUS_PUBLISHED

    def allow_publish(self):
        return self.name == constants.MODEL_RUN_STATUS_COMPLETED

    def allow_visualise(self):
        return self.name == constants.MODEL_RUN_STATUS_COMPLETED or self.name == constants.MODEL_RUN_STATUS_PUBLISHED

    def get_display_color(self):
        return {
            constants.MODEL_RUN_STATUS_COMPLETED: '#38761d',
            constants.MODEL_RUN_STATUS_PUBLISHED: '#711780',
            constants.MODEL_RUN_STATUS_RUNNING: '#f6b26b',
            constants.MODEL_RUN_STATUS_FAILED: '#990000'
        }.get(self.name, '#000000')


    def __repr__(self):
        """String representation"""

        return "<ModelRunStatus(name=%s)>" % self.name
