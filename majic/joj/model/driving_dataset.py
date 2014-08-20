"""
# header
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
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
    view_order_index = Column(Integer)
    usage_order_index = Column(Integer)

    driving_data_lat = None
    driving_data_lon = None
    driving_data_rows = None

    def get_python_parameter_value(self, parameter_namelist_name, is_list=False):
        """
        Gets the value of the first matching parameter value as a python object
        :param parameter_namelist_name: list containing [namelist, name] of parameter to find
        :param is_list: Indicates whether the value is a list
        """
        for param_val in self.parameter_values:
            if param_val.parameter.name == parameter_namelist_name[1]:
                if param_val.parameter.namelist.name == parameter_namelist_name[0]:
                    return param_val.get_value_as_python(is_list=is_list)

    def __repr__(self):
        return "<DrivingDataset(name=%s)>" % self.name
