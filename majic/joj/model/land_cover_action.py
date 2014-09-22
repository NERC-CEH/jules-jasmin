"""
header
"""
from sqlalchemy import Integer, Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from joj.model.meta import Base


class LandCoverAction(Base):
    """
    Represents an action to be carried out on a land cover region with a mask and
    land cover value
    """

    __tablename__ = 'land_cover_actions'

    id = Column(Integer, primary_key=True)
    value_id = Column(Integer, ForeignKey('land_cover_values.id'))
    order = Column(Integer)
    region_id = Column(Integer, ForeignKey("land_cover_regions.id"))
    model_run_id = Column(Integer, ForeignKey("model_runs.id"))

    value = relationship("LandCoverValue", backref=backref("actions", order_by=id))
    region = relationship("LandCoverRegion", backref=backref("actions", order_by=id))
    model_run = relationship("ModelRun", backref=backref("land_cover_actions", order_by=order))

    def duplicate_from(self, other):
        """
        Duplicate land cover action from other
        :param other: land cover action to copy
        :return: self
        """
        self.value_id = other.value_id
        self.order = other.order
        self.region_id = other.region_id
        return self

    def __repr__(self):
        return "<LandCoverAction(region=%s, value=%s)>" % (self.region_id, self.value_id)