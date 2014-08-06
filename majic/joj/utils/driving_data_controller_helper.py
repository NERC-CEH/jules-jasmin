"""
header
"""
import datetime
from pylons import config

from joj.utils import constants
from joj.model import ParameterValue
from joj.services.dataset import DatasetService
from joj.services.job_runner_client import JobRunnerClient
from joj.model.non_database.spatial_extent import SpatialExtent
from joj.utils.extents_controller_helper import ExtentsControllerHelper
from joj.utils.ascii_download_helper import AsciiDownloadHelper


class DrivingDataParsingException(Exception):
    """
    Represents an error parsing the user uploaded driving data file
    """
    pass


class DrivingDataControllerHelper(object):
    """
    Helper class for the driving data page
    """

    n_lines = None
    var_list = None
    n_vars = None
    interp_list = None
    period = None
    job_runner_client = None

    def __init__(self, job_runner_client=JobRunnerClient(config), dataset_service=DatasetService(),
                 ascii_download_helper=AsciiDownloadHelper(config['thredds.server_url'])):
        self.ascii_download_helper = ascii_download_helper
        self.job_runner_client = job_runner_client
        self.dataset_service = dataset_service

    def create_values_dict_from_database(self, model_run):
        """
        Create a form element values dictionary for rendering on page load
        :param model_run:
        :return a dictionary of form element names and values
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
            values['dt_start'] = start_date.strftime(constants.USER_UPLOAD_DATE_FORMAT)
        if end_date is not None:
            values['dt_end'] = end_date.strftime(constants.USER_UPLOAD_DATE_FORMAT)
        return values

    def save_uploaded_driving_data(self, values, errors, model_run_service, old_driving_dataset, user):
        """
        Save the uploaded driving data against the model run being created. Note that you should validate these values
        before calling this function
        :param values: POST values dictionary
        :param errors: Object to add errors to
        :param model_run_service: Service to access model run database operations
        :param old_driving_dataset: Old driving dataset to replace
        :param user: Currently logged in user
        """

        self._validate_upload_values(values, errors)

        # Only proceed if we have no errors up to this stage
        if len(errors) != 0:
            return

        model_run = model_run_service.get_model_being_created_with_non_default_parameter_values(user)
        model_run_id = model_run.id
        start_date = datetime.datetime.strptime(values['dt_start'], constants.USER_UPLOAD_DATE_FORMAT)
        end_date = datetime.datetime.strptime(values['dt_end'], constants.USER_UPLOAD_DATE_FORMAT)
        lat = float(values['lat'])
        lon = float(values['lon'])
        file = values['driving-file'].file

        try:
            self._process_driving_data_file(file, start_date, end_date, model_run_id)
        except DrivingDataParsingException as e:
            errors['driving-file'] = e.message
            self.job_runner_client.delete_file(model_run_id, constants.USER_UPLOAD_FILE_NAME)
            return

        # Save the fractional file
        self._save_fractional_file_to_job_runner(model_run, model_run_id)

        # Do database stuff
        new_driving_dataset = self._create_uploaded_driving_dataset(start_date, end_date, lat, lon, model_run_service)

        user_upload_id = self.dataset_service.get_id_for_user_upload_driving_dataset()
        if old_driving_dataset is not None and old_driving_dataset.id == user_upload_id:
            old_driving_dataset = self._create_uploaded_driving_dataset(
                start_date, end_date, lat, lon, model_run_service)

        model_run_service.save_driving_dataset_for_new_model(new_driving_dataset, old_driving_dataset, user)

    def _validate_download_values(self, driving_data, errors, values):
        start = self._validate_date(errors, 'dt_start', values)
        end = self._validate_date(errors, 'dt_end', values)
        if start is not None and end is not None:
            self.ascii_download_helper.get_actual_data_start(driving_data, start)
            self.ascii_download_helper.get_actual_data_end(driving_data, end)

        lat, lon = None, None
        if 'lat' not in values or values['lat'] == '':
            errors['lat'] = "Please enter a value"
        elif 'lon' not in values or values['lon'] == '':
            errors['lon'] = "Please enter a value"
        else:
            lat = float(values['lat'])
            lon = float(values['lon'])

            spatial_extent = SpatialExtent(driving_data.boundary_lat_north, driving_data.boundary_lat_south,
                                           driving_data.boundary_lon_west, driving_data.boundary_lon_east)

            ExtentsControllerHelper().validate_singlecell_spatial_extents(spatial_extent, errors, lat, lon)
        return lat, lon, start, end

    def download_driving_data(self, values, errors, response):
        """
        Download driving data for driving dataset, position and time specified in POST values dict
        :param values: POST values dictionary
        :param errors: Object to add errors to
        :param response: Pylons response object
        :return:
        """

        driving_id = values['driving_dataset']
        driving_data = self.dataset_service.get_driving_dataset_by_id(driving_id)

        lat, lon, start, end = self._validate_download_values(driving_data, errors, values)

        if len(errors) > 0:
            return

        filename = self.ascii_download_helper.get_driving_data_filename(driving_data, lat, lon, start, end)
        filesize = self.ascii_download_helper.get_driving_data_filesize(driving_data, start, end)

        response.headers['Content-Type'] = str('text/plain')
        response.headers['Content-Disposition'] = str('attachment; filename="%s"' % filename)
        response.headers['Content-Length'] = str(filesize)

        file_generator = self.ascii_download_helper.get_driving_data_file_gen(driving_data, lat, lon, start, end)

        return file_generator

    def _save_fractional_file_to_job_runner(self, model_run, model_run_id):

        # TODO this properly by reading from the fractional netCDF file
        frac = "0.0  0.0  0.0  1.0  0.0  0.0  0.0  0.0  0.0"

        self.job_runner_client.start_new_file(model_run_id, constants.FRACTIONAL_FILENAME)
        self.job_runner_client.append_to_file(model_run, constants.FRACTIONAL_FILENAME, frac)
        self.job_runner_client.close_file(model_run_id, constants.FRACTIONAL_FILENAME)

    def _create_uploaded_driving_dataset(self, start_date, end_date, lat, lon, model_run_service):
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
        driving_dataset.driving_data_rows = self.n_lines
        driving_dataset.parameter_values = []

        params_to_save = [[constants.JULES_PARAM_DRIVE_DATA_START, start_date],
                          [constants.JULES_PARAM_DRIVE_DATA_END, end_date],
                          [constants.JULES_PARAM_DRIVE_DATA_PERIOD, self.period],
                          [constants.JULES_PARAM_DRIVE_FILE, constants.USER_UPLOAD_FILE_NAME],
                          [constants.JULES_PARAM_DRIVE_NVARS, len(self.var_list)],
                          [constants.JULES_PARAM_DRIVE_VAR, self.var_list],
                          [constants.JULES_PARAM_DRIVE_INTERP, self.interp_list],
                          [constants.JULES_PARAM_LATLON_LATITUDE, lat],
                          [constants.JULES_PARAM_LATLON_LONGITUDE, lon],
                          [constants.JULES_PARAM_FRAC_FILE, constants.FRACTIONAL_FILENAME]]

        for param in params_to_save:
            parameter = model_run_service.get_parameter_by_constant(param[0])
            param_val = ParameterValue()
            param_val.set_value_from_python(param[1])
            param_val.parameter_id = parameter.id

            driving_dataset.parameter_values.append(param_val)

        user_upload_id = self.dataset_service.get_id_for_user_upload_driving_dataset()
        ds = self.dataset_service.get_driving_dataset_by_id(user_upload_id)
        for pv in ds.parameter_values:
            parameter_value = ParameterValue()
            parameter_value.parameter_id = pv.parameter_id
            parameter_value.value = pv.value
            driving_dataset.parameter_values.append(parameter_value)
        return driving_dataset

    def _process_driving_data_file(self, file, start_date, end_date, model_run_id):
        """
        Parse a driving data file
        :param file: The file to parse
        :param start_date: Date/time of first row of data in file
        :param end_date: Date/time of last row of data in file
        :param model_run_id: ID of model run being created
        :raise DrivingDataParsingException: on finding an error with the file
        """

        # Record the previous and previous but one lines
        prev2line = None
        prevline = None
        left_header = False  # Indicates that we have left the header
        n_line = 0
        self.job_runner_client.start_new_file(model_run_id, constants.USER_UPLOAD_FILE_NAME)
        for line in file:
            self.job_runner_client.append_to_file(model_run_id, constants.USER_UPLOAD_FILE_NAME, line)
            line = line.strip()
            if not line.startswith('#'):
                if not left_header:
                    self._process_header(prev2line, prevline)
                    left_header = True
                n_line += 1
                data = line.split()
                if len(data) != self.n_vars:
                    raise DrivingDataParsingException("Row %s has an invalid number of data points: should be %s, "
                                                      "found %s" % (n_line, self.n_vars, len(data)))
                for num in data:
                    try:
                        float(num)
                    except ValueError:
                        raise DrivingDataParsingException("Non-numeric value found in row %s: value was %s"
                                                          % (n_line, num))
            # Finally move the stored lines on one
            prev2line = prevline
            prevline = line
        self.n_lines = n_line

        seconds = (end_date - start_date).total_seconds()
        period = seconds / (self.n_lines - 1)
        self.period = int(period)
        self.job_runner_client.close_file(model_run_id, constants.USER_UPLOAD_FILE_NAME)

    def _process_header(self, var_line, interp_line):
        if var_line is None or interp_line is None:
            raise DrivingDataParsingException("Invalid header: last two lines of header must be variable names and "
                                              "interpolation flags")
        var_line = var_line.replace('#', '')
        vars = var_line.split()
        if len(vars) == 0:
            raise DrivingDataParsingException("No driving data variables were found in the header")
        for var in vars:
            if var not in constants.USER_UPLOAD_ALLOWED_VARS:
                raise DrivingDataParsingException("Invalid variable name found in the header: %s is not a "
                                                  "JULES input variable" % var)
        self.var_list = vars
        self.n_vars = len(vars)

        interp_line = interp_line.replace('#', '')
        interps = interp_line.split()
        if len(interps) != self.n_vars:
            raise DrivingDataParsingException("Incorrect number of interpolation flags in header: should be %s, "
                                              "found %s" % (self.n_vars, len(interps)))
        for interp in interps:
            if interp not in constants.USER_UPLOAD_ALLOWED_INTERPS:
                raise DrivingDataParsingException("Invalid flat found in the header: %s is not a "
                                                  "JULES interpolation flag" % interp)
        self.interp_list = interps

    def _validate_upload_values(self, values, errors):
        """
        Validate uploaded driving data and add any errors to an errors object
        :param values: POST values dictionary
        :param errors: Object to add errors to
        """

        # Validate the dates
        start_date = self._validate_date(errors, 'dt_start', values)
        end_date = self._validate_date(errors, 'dt_end', values)

        if end_date is not None and start_date is not None:
            if start_date > end_date:
                errors['dt_end'] = 'End date must not be before the start date'

        # Validate the lat lon:
        if 'lat' not in values or values['lat'] == '':
            errors['lat'] = "Please enter a value"
        elif 'lon' not in values or values['lon'] == '':
            errors['lon'] = "Please enter a value"
        else:
            lat = float(values['lat'])
            lon = float(values['lon'])
            self._validate_lat_lon(errors, lat, lon)

        file = values['driving-file']
        if file == u'':
            errors['driving-file'] = "You must select a driving data file"

    def _validate_date(self, errors, key, values):
        if key not in values or values[key] == '':
            errors[key] = 'Please enter a date'
        else:
            date_str = values[key]
            try:
                return datetime.datetime.strptime(date_str, constants.USER_UPLOAD_DATE_FORMAT)
            except ValueError:
                errors[key] = 'Please enter date in the format YYYY-MM-DD HH:MM'
            return None

    def _validate_lat_lon(self, errors, lat, lon):
        # FormEncode should have already converted these to floats
        if not (-90 < lat < 90):
            errors['lat'] = "Latitude must be between -90 and 90"
        if not (-180 < lon < 180):
            errors['lon'] = "Longitude must be between -180 and 180"