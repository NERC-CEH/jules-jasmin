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
        """
        Is the ModelRunStatus published?
        :return: True if published, false otherwise
        """
        return self.name == constants.MODEL_RUN_STATUS_PUBLISHED

    def allow_publish(self):
        """
        Does the ModelRunStatus allow the ModelRun to be published?
        :return: True if a ModelRun can be published, false otherwise
        """
        return self.name == constants.MODEL_RUN_STATUS_COMPLETED

    def allow_visualise(self):
        """
        Does the ModelRunStatus allow the ModelRun to be visualised on the map?
        :return: True if the ModelRun can be visualised, false otherwise
        """
        return self.name == constants.MODEL_RUN_STATUS_COMPLETED or self.name == constants.MODEL_RUN_STATUS_PUBLISHED

    def get_display_color(self):
        """
        Gets the appropriate display color for the ModelRunStatus to be used on the User Interface
        :return: The ModelRunStatus display color as a hex string (#xxyyzz)
        """
        return {
            constants.MODEL_RUN_STATUS_COMPLETED: '#38761d',
            constants.MODEL_RUN_STATUS_PUBLISHED: '#711780',
            constants.MODEL_RUN_STATUS_RUNNING: '#f6b26b',
            constants.MODEL_RUN_STATUS_PENDING: '#f6b26b',
            constants.MODEL_RUN_STATUS_FAILED: '#990000',
            constants.MODEL_RUN_STATUS_SUBMIT_FAILED: '#990000'
        }.get(self.name, '#000000')


    def __repr__(self):
        """String representation"""

        return "<ModelRunStatus(name=%s)>" % self.name
