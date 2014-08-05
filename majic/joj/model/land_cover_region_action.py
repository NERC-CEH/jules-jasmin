"""
header
"""
from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from joj.model.meta import Base
from joj.utils import constants


class LandCoverRegionAction(Base):
    """
    Represents an action to be carried out on a land cover region with a mask and
    land cover value
    """

    __tablename__ = 'land_cover_region_actions'

    id = Column(Integer, primary_key=True)
    value = Column(Integer, ForeignKey('land_cover_types.id'))
    order = Column(Integer)
    region_id = Column(Integer, ForeignKey("land_cover_regions.id"))
    model_run_id = Column(Integer, ForeignKey("model_runs.id"))

    land_cover_region = relationship("LandCoverRegion", backref=backref("actions", order_by=id))
    model_run = relationship("ModelRun", backref=backref("land_cover_region_actions", order_by=order))

    def __repr__(self):
        return "<LandCoverRegionAction(region=%s, value=%s)>" % self.region_id, self.value