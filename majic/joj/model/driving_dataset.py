"""
# header
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
from joj.model.meta import Base
from joj.utils import constants, utils


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
    view_order_index = Column(Integer)
    usage_order_index = Column(Integer)

    driving_data_lat = None
    driving_data_lon = None
    driving_data_rows = None

    def get_python_parameter_value(self, parameter_namelist_name, is_list=None):
        """
        Gets the value of the first matching parameter value as a python object
        :param parameter_namelist_name: list containing [namelist, name, is_list] of parameter to find
            if is_list is not present defaults to false
        :param is_list: Indicates whether the value is a list, overrides constant
        :return parameter value as python or None
        """
        return utils.find_parameter_values(self.parameter_values, parameter_namelist_name, is_list)

    def __repr__(self):
        return "<DrivingDataset(name=%s)>" % self.name
