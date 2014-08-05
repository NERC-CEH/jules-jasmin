"""
header
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from joj.model.meta import Base
from joj.utils import constants


class LandCoverRegionType(Base):
    """
    Represents a category of land cover regions e.g. 'River catchments' or 'Countries'
    """

    __tablename__ = 'land_cover_region_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_LONG_STRING_SIZE))
    driving_dataset_id = Column(Integer, ForeignKey('driving_datasets.id'))

    driving_dataset = relationship("DrivingDataset", backref=backref("land_cover_region_types", order_by=id))

    def __repr__(self):
        return "<LandCoverRegionType(name=%s)>" % self.name
