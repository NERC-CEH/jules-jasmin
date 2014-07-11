# header
from sqlalchemy import Column, Integer, String, Float, DateTime, Interval
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
    geographic_region = Column(String(constants.DB_LONG_STRING_SIZE))
    spatial_resolution = Column(String(constants.DB_LONG_STRING_SIZE))
    temporal_resolution = Column(String(constants.DB_LONG_STRING_SIZE))
    boundary_lat_north = Column(Float)
    boundary_lat_south = Column(Float)
    boundary_lon_east = Column(Float)
    boundary_lon_west = Column(Float)
    time_start = Column(DateTime)
    time_end = Column(DateTime)

    def __repr__(self):
        return "<DrivingDataset(name=%s)>" % self.name
