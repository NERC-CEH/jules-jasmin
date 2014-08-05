"""
header
"""
from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from joj.model.meta import Base
from joj.utils import constants


class LandCoverRegion(Base):
    """
    Represents a land cover mask for a specific region, e.g. 'Wales' or
    'River Thames catchment area'
    """

    __tablename__ = 'land_cover_regions'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_LONG_STRING_SIZE))
    mask_file = Column(String(constants.DB_LONG_STRING_SIZE))
    type_id = Column(Integer, ForeignKey('land_cover_region_types.id'))

    type = relationship("LandCoverRegionType", backref=backref("land_cover_regions", order_by=id))

    def __repr__(self):
        return "<LandCoverRegion(name=%s)>" % self.name
