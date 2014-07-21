"""
header
"""
import datetime
from joj.model.non_database.spatial_extent import InvalidSpatialExtent, SpatialExtent
from joj.model.non_database.temporal_extent import InvalidTemporalExtent, TemporalExtent
from joj.utils import constants
from joj.services.lat_lon_service import LatLonService


def create_values_dict_from_database(model_run, driving_data):
    """
    Create a dictionary of values corresponding to the form elements on the page and the values they should have, based
    on either the values in the database or on appropriate defaults
    :param model_run: The model run currently being used
    :param driving_data: The driving data selected for the model_run
    :return: Dictionary of form input names -> values
    """
    values = {}
    multicell = model_run.get_python_parameter_value(constants.JULES_PARAM_LATLON_REGION)
    if multicell is None:
        multicell = True

    if multicell:
        values['site'] = 'multi'
    else:
        values['site'] = 'single'
    values['lat'], values['lon'] = model_run.get_python_parameter_value(constants.JULES_PARAM_POINTS_FILE) \
        or [None, None]
    point_value = model_run.get_python_parameter_value(constants.JULES_PARAM_SWITCHES_L_POINT_DATA)
    if point_value is None:
        point_value = False
    if not point_value:
        values['average_over_cell'] = 1

    values['lat_s'], values['lat_n'] = model_run.get_python_parameter_value(
        constants.JULES_PARAM_LAT_BOUNDS) \
        or (driving_data.boundary_lat_south, driving_data.boundary_lat_north)
    values['lon_w'], values['lon_e'] = model_run.get_python_parameter_value(
        constants.JULES_PARAM_LON_BOUNDS) \
        or (driving_data.boundary_lon_west, driving_data.boundary_lon_east)

    start_date = model_run.get_python_parameter_value(constants.JULES_PARAM_RUN_START)
    if start_date is not None:
        values['start_date'] = start_date.date()
    else:
        values['start_date'] = driving_data.time_start.date()

    end_date = model_run.get_python_parameter_value(constants.JULES_PARAM_RUN_END)
    if end_date is not None:
        values['end_date'] = end_date.date()
    else:
        values['end_date'] = driving_data.time_end.date()

    return values


def save_extents_against_model_run(values, driving_data, model_run_service, user):
    """
    Save spatial and temporal extents against the model run currently being created
    :param values: The extents page POST values
    :param driving_data: Chosen driving data
    :param model_run_service: Model run service to use
    :param user: Currently logged in user
    :return: Nothing
    """
    params_to_delete = [constants.JULES_PARAM_USE_SUBGRID,
                        constants.JULES_PARAM_LATLON_REGION,
                        constants.JULES_PARAM_LAT_BOUNDS,
                        constants.JULES_PARAM_LON_BOUNDS,
                        constants.JULES_PARAM_NPOINTS,
                        constants.JULES_PARAM_POINTS_FILE,
                        constants.JULES_PARAM_SWITCHES_L_POINT_DATA,
                        constants.JULES_PARAM_RUN_START,
                        constants.JULES_PARAM_RUN_END]

    params_to_save = [[constants.JULES_PARAM_USE_SUBGRID, True]]
    if values['site'] == 'multi':
        params_to_save.append([constants.JULES_PARAM_LATLON_REGION, True])
        params_to_save.append([constants.JULES_PARAM_LAT_BOUNDS, [values['lat_s'], values['lat_n']]])
        params_to_save.append([constants.JULES_PARAM_LON_BOUNDS, [values['lon_w'], values['lon_e']]])
    else:
        params_to_save.append([constants.JULES_PARAM_LATLON_REGION, False])
        params_to_save.append([constants.JULES_PARAM_NPOINTS, 1])
        lat_lon_service = LatLonService()
        lat, lon = lat_lon_service.get_nearest_cell_center(values['lat'], values['lon'], driving_data.id)
        params_to_save.append([constants.JULES_PARAM_POINTS_FILE, [lat, lon]])
        params_to_save.append([constants.JULES_PARAM_SWITCHES_L_POINT_DATA, 'average_over_cell' not in values])
    run_start = datetime.datetime.combine(values['start_date'], driving_data.time_start.time())
    run_end = datetime.datetime.combine(values['end_date'], driving_data.time_end.time())
    params_to_save.append([constants.JULES_PARAM_RUN_START, run_start])
    params_to_save.append([constants.JULES_PARAM_RUN_END, run_end])
    model_run_service.save_new_parameters(params_to_save, params_to_delete, user)


def validate_extents_form_values(values, driving_data, errors):
    """
    Validate extents values dictionary and add errors to an errors object if needed
    :param values: Dictionary of form element names : values
    :param driving_data: Chosen driving data
    :param errors: Object to add errors to
    :return: nothing
    """
    # Set the start and end times to be the times at which the driving data starts and ends.
    run_start = datetime.datetime.combine(values['start_date'], driving_data.time_start.time())
    run_end = datetime.datetime.combine(values['end_date'], driving_data.time_end.time())
    spatial_extent = SpatialExtent(driving_data.boundary_lat_north, driving_data.boundary_lat_south,
                                   driving_data.boundary_lon_west, driving_data.boundary_lon_east)
    temporal_extent = TemporalExtent(driving_data.time_start, driving_data.time_end)

    if values['site'] == 'multi':
        _validate_multicell_spatial_extents(spatial_extent, errors,
                                            values['lat_n'], values['lat_s'],
                                            values['lon_e'], values['lon_w'])
    else:
        _validate_singlecell_spatial_extents(spatial_extent, errors,
                                             values['lat'], values['lon'])

    validate_temporal_extents(temporal_extent, errors, run_start, run_end)


def _validate_multicell_spatial_extents(spatial_extent, errors, lat_n, lat_s, lon_e, lon_w):
    """
    Validate multi cell spatial extents and add errors to an errors object if needed
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


def _validate_singlecell_spatial_extents(spatial_extent, errors, lat, lon):
    """
    Validate single cell spatial extents and add errors to an errors object if needed
    :param spatial_extent: Driving data spatial extent object
    :param errors: Object to add errors to
    :param lat: Latitude
    :param lon: Longitude
    :return: nothing
    """
    lat_s, lat_n = spatial_extent.get_lat_bounds()
    if not (-90 <= lat <= 90):
        errors['lat'] = "Latitude must be between -90 and 90"
    elif lat < lat_s:
        errors['lat'] = "Latitude (%s deg N) cannot be south of %s deg N" % (lat, lat_s)
    elif lat > lat_n:
        errors['lat'] = "Latitude (%s deg N) cannot be north of %s deg N" % (lat, lat_n)

    lon_w, lon_e = spatial_extent.get_lon_bounds()
    if not (-180 <= lon <= 180):
        errors['lon'] = "Longitude must be between -180 and 180"
    elif lon < lon_w:
        errors['lon'] = "Longitude (%s deg E) cannot be west of %s deg E" % (lon, lon_w)
    elif lon > lon_e:
        errors['lon'] = "Longitude (%s deg E) cannot be east of %s deg E" % (lon, lon_e)


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
