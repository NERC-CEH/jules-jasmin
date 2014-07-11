"""
# Header
"""
from sqlalchemy import Column, Integer, String
from joj.model.meta import Base


class DatasetType(Base):
    """Used to distinguish between the different types of map dataset we're dealing with"""

    __tablename__ = 'dataset_types'

    id = Column(Integer, primary_key=True)
    type = Column(String(30))

    def __repr__(self):
        """String representation of the dataset type"""

        return "<DatasetType(type=%s)>" % self.type
