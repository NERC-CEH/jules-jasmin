"""
header
"""

from joj.utils import constants
from formencode import Schema, validators, NestedVariables, ForEach


def create_string_error_dictionary(field_name):
    """
    Create a string error dictionary specific to a field name
    :param field_name: the field name
    :return: the dictionary
    """
    return {
        'empty': 'Please enter a {}'.format(field_name),
        'tooLong': 'Enter a {} not more than %(max)i characters long'.format(field_name),
        'tooShort': 'Enter a {} %(min)i characters long or more'.format(field_name)}


class Region(Schema):
    """
    Region mask schema for validation (line in masks table)
    """

    allow_extra_fields = False
    filter_extra_fields = True
    id = validators.Int()
    name = validators.String(not_empty=True,
                             max=constants.DB_LONG_STRING_SIZE,
                             strip=True,
                             messages=create_string_error_dictionary('name'))
    category = validators.String(not_empty=True,
                                 max=constants.DB_LONG_STRING_SIZE,
                                 strip=True,
                                 messages=create_string_error_dictionary('category'))
    path = validators.String(not_empty=True,
                             max=constants.DB_PATH_SIZE,
                             strip=True,
                             messages=create_string_error_dictionary('path'))


class DriveVar(Schema):
    """
    Driving data variables validation schema
    """
    allow_extra_fields = False
    filter_extra_fields = True
    vars = validators.String(not_empty=True,
                             max=constants.DB_STRING_SIZE,
                             strip=True,
                             messages=create_string_error_dictionary('variable'))
    names = validators.String(not_empty=True,
                              max=constants.DB_STRING_SIZE,
                              strip=True,
                              messages=create_string_error_dictionary('name'))
    templates = validators.String(not_empty=True,
                                  max=constants.DB_STRING_SIZE,
                                  strip=True,
                                  messages=create_string_error_dictionary('template'))
    interps = validators.String(not_empty=True,
                                max=constants.DB_STRING_SIZE,
                                strip=True,
                                messages=create_string_error_dictionary('interpolation'))


class ExtraParameter(Schema):
    """
    Extra parameters validation schema
    """
    allow_extra_fields = False
    filter_extra_fields = True
    id = validators.Int()
    value = validators.String(not_empty=True,
                              max=constants.DB_PARAMETER_VALUE_STRING_SIZE,
                              strip=True,
                              messages=create_string_error_dictionary('value'))


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

    post_processing_script_id = validators.Int(not_empty=True, min=0)
    is_restricted_to_admins = validators.StringBoolean(if_missing=False)

    region = ForEach(Region())
    drive_var_ = ForEach(DriveVar())
    param = ForEach(ExtraParameter())