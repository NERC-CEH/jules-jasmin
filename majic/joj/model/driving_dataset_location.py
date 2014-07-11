"""
# Header
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from joj.model.meta import Base


class DrivingDatasetLocation(Base):
    """Metadata from a map dataset"""

    __tablename__ = 'driving_dataset_locations'

    column_names = []

    id = Column(Integer, primary_key=True)
    base_url = Column(String(255))
    driving_dataset_id = Column(Integer, ForeignKey('driving_datasets.id'))
    driving_dataset = relationship("DrivingDataset", backref=backref('locations', order_by=id))

    def __repr__(self):
        """String representation of the Dataset class"""

        return "<DrivingDatasetLocation(base_url=%s)>" \
            % (
                self.base_url
            )
