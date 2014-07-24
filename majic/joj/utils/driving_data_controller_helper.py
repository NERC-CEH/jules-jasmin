"""
header
"""
import datetime
from joj.utils import constants
from joj.model import DrivingDataset, ParameterValue
from joj.services.dataset import DatasetService

INPUT_DATE_FORMAT = "%Y-%m-%d %H:%M"


def create_values_dict_from_database(model_run):
    """

    :param model_run:
    """
    values = {}
    values['driving_dataset'] = model_run.driving_dataset_id
    # If this isn't the user uploaded driving dataset, then this is the only value we want to show:
    if model_run.driving_dataset_id != DatasetService().get_id_for_user_upload_driving_dataset():
        return values

    start_date = model_run.get_python_parameter_value(constants.JULES_PARAM_DRIVE_DATA_START)
    end_date = model_run.get_python_parameter_value(constants.JULES_PARAM_DRIVE_DATA_END)

    values['lat'] = model_run.driving_data_lat
    values['lon'] = model_run.driving_data_lon
    if start_date is not None:
        values['dt_start'] = start_date.strftime(INPUT_DATE_FORMAT)
    if end_date is not None:
        values['dt_end'] = end_date.strftime(INPUT_DATE_FORMAT)
    return values


def save_uploaded_driving_data(values, model_run_service, old_driving_dataset, user):
    """
    Save the uploaded driving data against the model run being created. Note that you should validate these values
    before calling this function
    :param user: Currently logged in user
    :param model_run_service: Service to access model run database operations
    :param old_driving_dataset: Old driving dataset to replace
    :param values: POST values dictionary
    """
    start_date = datetime.datetime.strptime(values['dt_start'], INPUT_DATE_FORMAT)
    end_date = datetime.datetime.strptime(values['dt_end'], INPUT_DATE_FORMAT)
    lat = values['lat']
    lon = values['lon']
    file = values['driving-file']
    # TODO put file in correct place here I suppose (before DB stuff) - think about delete old file etc.
    new_driving_dataset = _create_uploaded_driving_dataset(start_date, end_date, lat, lon,
                                                           file, model_run_service)
    model_run_service.save_driving_dataset_for_new_model(new_driving_dataset, old_driving_dataset, user)


def _create_uploaded_driving_dataset(start_date, end_date, lat, lon, file, model_run_service):

    rows = _get_file_number_lines(file)

    class UploadedDrivingDataset(object):
        """
        An uploaded driving dataset
        """
        def __init__(self):
            self.id = DatasetService().get_id_for_user_upload_driving_dataset()
            self.driving_data_lat = None
            self.driving_data_lon = None
            self.driving_data_rows = None
            self.parameter_values = []

    driving_dataset = UploadedDrivingDataset()
    driving_dataset.driving_data_lat = lat
    driving_dataset.driving_data_lon = lon
    driving_dataset.driving_data_rows = rows
    driving_dataset.parameter_values = []

    period = _get_file_period(file, start_date, end_date)
    filename = constants.USER_UPLOAD_FILE_NAME
    file_vars = _get_file_vars(file)
    interp_list = _get_interp_list(file)
    params_to_save = [[constants.JULES_PARAM_DRIVE_DATA_START, start_date],
                      [constants.JULES_PARAM_DRIVE_DATA_END, end_date],
                      [constants.JULES_PARAM_DRIVE_DATA_PERIOD, period],
                      [constants.JULES_PARAM_DRIVE_FILE, filename],
                      [constants.JULES_PARAM_DRIVE_NVARS, len(file_vars)],
                      [constants.JULES_PARAM_DRIVE_VAR, file_vars],
                      [constants.JULES_PARAM_DRIVE_INTERP, interp_list]]
    param_values = []
    for param in params_to_save:
        parameter = model_run_service.get_parameter_by_constant(param[0])
        param_val = ParameterValue()
        param_val.set_value_from_python(param[1])
        param_val.parameter_id = parameter.id

        param_values.append(param_val)
    driving_dataset.parameter_values = param_values
    return driving_dataset


def _get_file_number_lines(file):
    #TODO read from file
    return 3


def _get_file_period(file, start_date, end_date):
    seconds = (end_date - start_date).total_seconds()
    lines = _get_file_number_lines(file)
    period = seconds / (lines - 1)
    return int(period)


def _get_file_vars(file):
    #TODO read file
    return ['sw_down', 'lw_down', 'tot_rain', 'tot_snow', 't', 'wind', 'pstar', 'q']


def _get_interp_list(file):
    # TODO read from file
    n = len(_get_file_vars(file))
    interp = ['i']
    return n * interp


def validate_uploaded_driving_data(values, errors):
    """
    Validate uploaded driving data and add any errors to an errors object
    :param values: POST values dictionary
    :param errors: Object to add errors to
    """
    # TODO disable these fields unless the user upload driving data is selected - otherwise you could submit
    # TODO to this controller with another driving dataset selected

    # Validate the dates

    start_date = _validate_date(errors, 'dt_start', values)
    end_date = _validate_date(errors, 'dt_end', values)

    if end_date is not None and start_date is not None:
        if start_date > end_date:
            errors['dt_end'] = 'End date must not be before the start date'

    # Validate the lat lon:
    lat = values['lat']
    lon = values['lon']
    _validate_lat_lon(errors, lat, lon)

    file = values['driving-file']
    _validate_driving_file(errors, file)


def _validate_date(errors, key, values):
    date_str = values[key]
    try:
        return datetime.datetime.strptime(date_str, INPUT_DATE_FORMAT)
    except ValueError:
        errors[key] = 'Please enter a date in the format YYYY-MM-DD HH:MM'
    return None


def _validate_lat_lon(errors, lat, lon):
    # FormEncode should have already converted these to floats
    if not (-90 < lat < 90):
        errors['lat'] = "Latitude must be between -90 and 90"
    if not (-180 < lon < 180):
        errors['lon'] = "Longitude must be between -180 and 180"


def _validate_driving_file(errors, file):
    if file == u'':
        errors['driving-file'] = "You must select a driving data file"
        #TODO apply validation rules here