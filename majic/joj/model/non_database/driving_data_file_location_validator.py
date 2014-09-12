"""
header
"""
import re
from joj.services.file_server_client import FileServerClient
from joj.model import DrivingDatasetLocation
from joj.utils import constants


class DrivingDataFileLocationValidator(object):
    """
    Validator for driving data file locations
    """

    def __init__(self, errors, dataset_types, file_server_client=FileServerClient()):
        """
        Initialise
        :param file_server_client: file service client
        :param errors: errors list
        :param dataset_types: dictionary of dataset types (key is name, value is id)
        :return: list of locations
        """
        self._errors = errors
        self._file_server_client = file_server_client
        self._dataset_types = dataset_types

    def _check_location(self, key, locations, filename, errors, dataset_type_id, jules_varname):
        """
        Check the location and add a key error if not found or add to location is found
        :param key: key
        :param locations: locations list (None if we location shouldn't be added)
        :param filename: filename to check
        :param errors: error list to add error to
        :param dataset_type_id: datasets type
        :param jules_varname: the variable name for the location
        :return: true if valid, false otherwise
        """
        if filename is None:
            return True

        if not self._file_server_client.file_exists("model_runs/" + filename):
            errors[key] = "Please check, file does not exist"
            return False

        if locations is not None:
            locations.append(
                DrivingDatasetLocation(base_url=filename, dataset_type_id=dataset_type_id, var_name=jules_varname))
        return True

    def get_file_locations(self, results):
        """
        Return all the file locations referenced by the results parameters
        if there is an error add it to the error dictionary
        :param results: dictionary of results from the driving dataset page
        :return:list of locations
        """
        locations = []

        for key in ['land_frac_file', 'latlon_file', 'frac_file', 'soil_props_file']:
            self._check_location(key, None, results.get(key), self._errors, None, None)

        regions = results.get('region', [])
        region_errors = []
        region_error = False
        for region, index in zip(regions, range(len(regions))):
            region_errors.append({})
            local_error = not self._check_location('path', None, region['path'], region_errors[index], None, None)
            region_error = region_error or local_error
        if region_error:
            self._errors['region'] = region_errors

        driving_data_vars = results.get(constants.PREFIX_FOR_DRIVING_VARS, [])
        driving_data_errors = []
        driving_data_error = False
        drive_file = results.get('drive_file')
        start_date = results.get('driving_data_start')
        end_date = results.get('driving_data_end')
        for driving_data, index in zip(driving_data_vars, range(len(driving_data_vars))):
            driving_data_errors.append({})

            ncml_filename = self._get_ncml_filename(driving_data['templates'], drive_file)

            local_error = not self._check_location(
                'templates',
                locations,
                ncml_filename,
                driving_data_errors[index],
                self._dataset_types[constants.DATASET_TYPE_COVERAGE],
                driving_data['vars'])
            driving_data_error = driving_data_error or local_error

            for filename in self._get_drive_filenames(driving_data['templates'], drive_file, start_date, end_date):
                local_error = not self._check_location(
                    'templates',
                    None,
                    filename,
                    driving_data_errors[index],
                    None,
                    None)
                if local_error:
                    driving_data_error = True
                    break

        if driving_data_error:
            self._errors[constants.PREFIX_FOR_DRIVING_VARS] = driving_data_errors

        return locations

    def _get_drive_filenames(self, variable_name, drive_file, start_date, end_date):
        """
        get the driving data filenames for a templated filename
        :param variable_name: the variable name
        :param drive_file: the driving data file template
        :param start_date: the start date
        :param end_date: the end date
        :return: list of file locations
        """
        if drive_file is None or variable_name is None:
            return []

        filename = drive_file.replace('%vv', variable_name)

        #Spec says months are only templated if year is so just check for year templates
        if filename.find('%y4') == -1 and filename.find('%y2') == -1:
            return [filename]

        return self._replace_date_templates(start_date, end_date, filename)

    def _replace_date_templates(self, start_date, end_date, filename):
        """
        replace the date templates and return the locations for those files
        :param start_date: the start date
        :param end_date: the end date
        :param filename: the filename template (with just time templating in)
        :return: list of locations
        """
        if start_date is None or end_date is None:
            return []

        months = []
        if filename.find('%m2') != -1 or filename.find('%m1') != -1 or filename.find('%mc') != -1:
            if start_date.year == end_date.year:
                for month in range(start_date.month, end_date.month + 1):
                    months.append([start_date.year, month])
            else:
                #initial month to the end of the year
                for month in range(start_date.month, 12 + 1):
                    months.append([start_date.year, month])
                #intervenning years
                for year in range(start_date.year + 1, end_date.year):
                    for month in range(1, 12 + 1):
                        months.append([year, month])
                #final year up to end month
                for month in range(1, end_date.month + 1):
                    months.append([end_date.year, month])
        else:
            for year in range(start_date.year, end_date.year + 1):
                months.append([year, 0])

        filenames = []
        for year, month in months:
            final_filename = filename \
                .replace('%y4', str(year)) \
                .replace('%y2', str(year % 100)) \
                .replace('%m2', "{:02}".format(month)) \
                .replace('%m1', "{}".format(month)) \
                .replace('%mc', "{}".format(constants.JULES_MONTH_ABBREVIATIONS[month - 1]))
            filenames.append(final_filename)
        return filenames

    def _get_ncml_filename(self, variable_name, drive_file):
        """
        Generate the ncml filename for a driving data set
        :param variable_name: the variable name
        :param drive_file: drive file
        :return:name
        """
        filename = drive_file.replace('%vv', variable_name)
        if filename.endswith('.nc'):
            filename += 'ml'
        else:
            filename += '.ncml'
        return re.sub('_?((%y4)|(%y2)|(%m2)|(%m1)|(%mc))', '', filename)
