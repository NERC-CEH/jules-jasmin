# header
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from joj.model.meta import Base
from joj.utils import constants


class DrivingDataset(Base):
    """
    A Dataset which can be used as driving data
    """

    __tablename__ = 'driving_datasets'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_LONG_STRING_SIZE))
    description = Column(String(constants.DB_LONG_STRING_SIZE))
    dataset_id = Column(Integer, ForeignKey('datasets.id'))

    dataset = relationship("Dataset")

    def __repr__(self):
        return "<DrivingDataset(name=%s)>" % self.name
