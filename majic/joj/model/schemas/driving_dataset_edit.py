"""
header
"""

from joj.utils import constants
from formencode import Schema, validators, NestedVariables, ForEach


class Region(Schema):
    """
    Region mask schema for validation (line in masks table)
    """

    allow_extra_fields = False
    filter_extra_fields = True
    id = validators.Int()
    name = validators.String(not_empty=True, max=constants.DB_LONG_STRING_SIZE, strip=True)
    category = validators.String(not_empty=True, max=constants.DB_LONG_STRING_SIZE, strip=True)
    path = validators.String(not_empty=True, max=constants.DB_PATH_SIZE, strip=True)


class DriveVar(Schema):
    """
    Driving data variables validation schema
    """
    allow_extra_fields = False
    filter_extra_fields = True
    vars = validators.String(not_empty=True, max=constants.DB_STRING_SIZE, strip=True)
    names = validators.String(not_empty=True, max=constants.DB_STRING_SIZE, strip=True)
    templates = validators.String(not_empty=True, max=constants.DB_STRING_SIZE, strip=True)
    interps = validators.String(not_empty=True, max=constants.DB_STRING_SIZE, strip=True)


class DrivingDatasetEdit(Schema):
    """Used to validate data for the model run create form"""

    pre_validators = [NestedVariables()]
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

    view_order_index = validators.Int(not_empty=True, min=0)
    usage_order_index = validators.Int(not_empty=True, min=0)

    driving_data_period = validators.Int(not_empty=True, min=1)
    driving_data_start = validators.String(not_empty=True, max=constants.DB_STRING_SIZE)
    driving_data_end = validators.String(not_empty=True, max=constants.DB_STRING_SIZE)
    drive_file = validators.String(not_empty=True, max=constants.DB_PARAMETER_VALUE_STRING_SIZE)
    drive_nvars = validators.Int(not_empty=True, min=1, messages={'tooLow': 'Please enter at least one variable'})
    drive_nx = validators.Int(not_empty=True, min=1)
    drive_ny = validators.Int(not_empty=True, min=1)
    drive_x_dim_name = validators.String(not_empty=True, max=constants.DB_PARAMETER_VALUE_STRING_SIZE)
    drive_y_dim_name = validators.String(not_empty=True, max=constants.DB_PARAMETER_VALUE_STRING_SIZE)
    drive_time_dim_name = validators.String(not_empty=True, max=constants.DB_PARAMETER_VALUE_STRING_SIZE)
    latlon_file = validators.String(not_empty=True, max=constants.DB_PARAMETER_VALUE_STRING_SIZE)
    latlon_lat_name = validators.String(not_empty=True, max=constants.DB_PARAMETER_VALUE_STRING_SIZE)
    latlon_lon_name = validators.String(not_empty=True, max=constants.DB_PARAMETER_VALUE_STRING_SIZE)
    frac_file = validators.String(not_empty=True, max=constants.DB_PARAMETER_VALUE_STRING_SIZE)
    frac_frac_name = validators.String(not_empty=True, max=constants.DB_PARAMETER_VALUE_STRING_SIZE)
    frac_type_dim_name = validators.String(not_empty=True, max=constants.DB_PARAMETER_VALUE_STRING_SIZE)
    land_frac_file = validators.String(not_empty=True, max=constants.DB_PARAMETER_VALUE_STRING_SIZE)
    land_frac_frac_name = validators.String(not_empty=True, max=constants.DB_PARAMETER_VALUE_STRING_SIZE)
    soil_props_file = validators.String(not_empty=True, max=constants.DB_PARAMETER_VALUE_STRING_SIZE)

    region = ForEach(Region())
    drive_var_ = ForEach(DriveVar())