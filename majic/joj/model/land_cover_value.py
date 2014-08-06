"""
header
"""
from sqlalchemy import Column, Integer, String
from joj.model.meta import Base
from joj.utils import constants


class LandCoverValue(Base):
    """
    Represents the different possible land cover types (ice, urban etc).
    """

    __tablename__ = 'land_cover_values'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_LONG_STRING_SIZE))
    index = Column(Integer)

    def __repr__(self):
        return "<LandCoverValue(name=%s)>" % self.name