"""
header
"""
from joj.model.non_database.spatial_extent import InvalidSpatialExtent
from joj.model.non_database.temporal_extent import InvalidTemporalExtent
from joj.utils import constants


def add_selected_extents_to_template_context(template_context, model_run, driving_data):
    """
    Get the extents from the database if already set or default them to dataset boundaries if not
    :param template_context: Pylons template context to add selected output variable lists to
    :param model_run: The model run currently being used
    :param driving_data: The driving data selected for the model_run
    """
    template_context.lat_s, template_context.lat_n = model_run.get_python_parameter_value(
        constants.JULES_PARAM_LAT_BOUNDS) \
        or (driving_data.boundary_lat_south, driving_data.boundary_lat_north)
    template_context.lon_w, template_context.lon_e = model_run.get_python_parameter_value(
        constants.JULES_PARAM_LON_BOUNDS) \
        or (driving_data.boundary_lon_west, driving_data.boundary_lon_east)
    template_context.run_start = model_run.get_python_parameter_value(constants.JULES_PARAM_RUN_START) \
        or driving_data.time_start
    template_context.run_end = model_run.get_python_parameter_value(constants.JULES_PARAM_RUN_END) \
        or driving_data.time_end


def validate_spatial_extents(spatial_extent, errors, lat_n, lat_s, lon_e, lon_w):
    """
    Validate spatial extents and add errors to an errors object if needed
    :param spatial_extent: Driving data spatial extent object
    :param errors: Object to add errors to
    :param lat_n: Northern latitude
    :param lat_s: Southern latitude
    :param lon_e: Eastern longitude
    :param lon_w: Western longitude
    :return: nothing
    """
    try:
        spatial_extent.set_lat_n(lat_n)
    except InvalidSpatialExtent as e:
        errors['lat_n'] = e.message
    try:
        spatial_extent.set_lat_s(lat_s)
    except InvalidSpatialExtent as e:
        errors['lat_s'] = e.message
    try:
        spatial_extent.set_lon_w(lon_w)
    except InvalidSpatialExtent as e:
        errors['lon_w'] = e.message
    try:
        spatial_extent.set_lon_e(lon_e)
    except InvalidSpatialExtent as e:
        errors['lon_e'] = e.message


def validate_temporal_extents(temporal_extent, errors, run_start, run_end):
    """
    Validate temporal extents and add errors to an errors object if needed
    :param temporal_extent: Driving data temporal extent object
    :param errors: Object to add errors to
    :param run_start: Model run start datetime
    :param run_end:  Model run end datetime
    :return: nothing
    """
    if run_start is not None:
        try:
            temporal_extent.set_start(run_start)
        except InvalidTemporalExtent as e:
            errors['start_date'] = e.message
    if run_end is not None:
        try:
            temporal_extent.set_end(run_end)
        except InvalidTemporalExtent as e:
            errors['end_date'] = e.message