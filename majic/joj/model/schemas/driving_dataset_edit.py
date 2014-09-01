"""
header
"""

from joj.utils import constants
from formencode import Schema, validators


class DrivingDatasetEdit(Schema):
    """Used to validate data for the model run create form"""

    allow_extra_fields = True
    filter_extra_fields = True

    name = validators.String(not_empty=True, max=constants.DB_STRING_SIZE)
    description = validators.String(not_empty=True, max=constants.DB_LONG_STRING_SIZE)
    geographic_region = validators.String(not_empty=True, max=constants.DB_STRING_SIZE)
    spatial_resolution = validators.String(not_empty=True, max=constants.DB_STRING_SIZE)
    temporal_resolution = validators.String(not_empty=True, max=constants.DB_STRING_SIZE)

    boundary_lat_north = validators.Number(not_empty=True, min=-90, max=90)
    boundary_lat_south = validators.Number(not_empty=True, min=-90, max=90)

    boundary_lon_east = validators.Number(not_empty=True, min=-180, max=180)
    boundary_lon_west = validators.Number(not_empty=True, min=-180, max=180)

    driving_data_start = validators.String(not_empty=True, max=constants.DB_STRING_SIZE)
    driving_data_end = validators.String(not_empty=True, max=constants.DB_STRING_SIZE)
