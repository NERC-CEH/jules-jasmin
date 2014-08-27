"""
header
"""
import sys
import datetime

from joj.utils import constants
from joj.services.dataset import DatasetService
from joj.services.dap_client.dap_client_factory import DapClientFactory
from joj.services.general import ServiceException


class AsciiDownloadHelper(object):
    """
    Class to manage the downloading of ASCII driving data files
    """
    col_size = 8
    header = """# MAJIC SINGLE CELL DRIVING DATA DOWNLOAD
#
# This is a download of a subset of JULES driving data for a single location:
#
# Driving data: {dd_name}
# Latitude: {lat}
# Lon: {lon}
#
# The first row of data is at: {start}
# The last row of data is at: {end}
# The data time period is: {period} seconds
# NOTE: These are the the first and last data points WITHIN the start and end times you
# requested when you downloaded this data. Therefore they are likely to NOT be the exact
# start and end times you requested - if you edit or re-upload this data you must use the
# start and end times shown above, not those you requested.
#
# The forcing variables in this file are:
{description}
#
# NOTE: The Majic driving data upload format requires that the last two lines of the header
# should be whitespace separated lists of:
# 	1) The names of the JULES forcing variables for each of the data columns
# 	2) The interpolation flags for each of the data columns
# both as given in the JULES manual.
#
# Here are the last two lines of the header:
# {vars}
# {interps}
"""

    def __init__(self, thredds_url, dataset_service=DatasetService(), dap_client_factory=DapClientFactory()):
        """
        Constructor
        :param dataset_service: Provides access to datasets
        :param dap_client_factory: Factory to create dap clients
        :return: AsciiDownloadHelper
        """
        self.thredds_url = thredds_url
        self._dap_clients = None
        self._dataset_service = dataset_service
        self._dap_client_factory = dap_client_factory

    def get_driving_data_file_gen(self, driving_data, lat, lon, start, end):
        """
        Get the correctly formatted contents of the ascii driving data download file
        :param driving_data: Driving data to get data from
        :param lat: Latitude of position to get data at
        :param lon: Longitude of position to get data at
        :param start: Earliest date/time to get data at
        :param end:  Latest date/time to get data at
        :return: Contents of file as generator object
        """
        self._create_dap_clients(driving_data)
        actual_start = self.get_actual_data_start(driving_data, start)
        actual_end = self.get_actual_data_end(driving_data, end)

        period = driving_data.get_python_parameter_value(constants.JULES_PARAM_DRIVE_DATA_PERIOD)
        description = self._get_description_string(driving_data)
        vars = self._get_vars_string(driving_data)
        interps = self._get_interps_string(driving_data)
        header = self.header.format(dd_name=driving_data.name,
                                    lat=lat,
                                    lon=lon,
                                    start=actual_start.strftime("%Y-%m-%d %X"),
                                    end=actual_end.strftime("%Y-%m-%d %X"),
                                    description=description,
                                    period=period,
                                    vars=vars,
                                    interps=interps)
        yield str(header)
        line_date = actual_start
        while line_date <= actual_end:
            data_line = self._get_data_line(driving_data, lat, lon, line_date)
            line_date += datetime.timedelta(seconds=period)
            yield str(data_line)

    def get_driving_data_filename(self, driving_data, lat, lon, start, end):
        """
        Get an appropriate filename for the file being downloaded
        :param driving_data: Driving data to get data from
        :param lat: Latitude of position to get data at
        :param lon: Longitude of position to get data at
        :param start: Earliest date/time to get data at
        :param end:  Latest date/time to get data at
        :return:
        """
        dd_name = driving_data.name.strip().replace(" ", "_")
        filename = "_".join([dd_name, str(lat), str(lon), start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")])
        return filename + constants.USER_DOWNLOAD_DRIVING_DATA_FILE_EXTENSION

    def get_driving_data_filesize(self, driving_data, start, end):
        """
        Get an estimate of the file size of an ASCII download of the driving data file
        :param driving_data: Driving data to download
        :param start: Start date
        :param end: End date
        :return: Estimated size in bytes of the download
        """
        size_header = sys.getsizeof(self.header, None)  # This is an estimate (header is not filled in) but good enough

        period = int(driving_data.get_python_parameter_value(constants.JULES_PARAM_DRIVE_DATA_PERIOD))
        time_delta = end - start  # This is an approximation since we know these may not be the actual start/ends
        nlines = (time_delta.total_seconds() / period) + 1

        nvars = int(driving_data.get_python_parameter_value(constants.JULES_PARAM_DRIVE_NVARS))
        size_of_one_var = 12.5  # Estimate of size usage based on measuring sample files
        size_lines = nvars * size_of_one_var * nlines
        return size_header + size_lines

    def _get_vars_string(self, driving_data):
        vars = driving_data.get_python_parameter_value(constants.JULES_PARAM_DRIVE_VAR, is_list=True)
        return '\t'.join(('%-*s' % (self.col_size, x) for x in vars))

    def _get_interps_string(self, driving_data):
        interps = driving_data.get_python_parameter_value(constants.JULES_PARAM_DRIVE_INTERP, is_list=True)
        return '\t'.join(('%-*s' % (self.col_size, x) for x in interps))

    def _get_description_string(self, driving_data):
        self._create_dap_clients_if_missing(driving_data)
        vars = driving_data.get_python_parameter_value(constants.JULES_PARAM_DRIVE_VAR, is_list=True)
        descs = []
        units = []
        for dap_client in self._dap_clients:
            desc = dap_client.get_longname()
            descs.append(desc)
            unit = dap_client.get_variable_units()
            units.append(unit)
        lines = []
        for var, desc, units in zip(vars, descs, units):
            line = "# {var}: {desc} ({units})".format(var=var, desc=desc, units=units)
            lines.append(line)
        return "\n".join(lines)

    def get_actual_data_start(self, driving_data, start):
        """
        Get the actual start date of the driving data download
        :param driving_data: The driving data being downloaded
        :param start: The requested start date
        :return: :raise ServiceException: On error with the dates
        """
        self._create_dap_clients_if_missing(driving_data)
        starts = []
        for dap_client in self._dap_clients:
            actual_start = dap_client.get_time_immediately_after(start)
            if actual_start is None:
                raise ServiceException("No datapoints found in the requested time range")
            starts.append(actual_start)
        if len(set(starts)) > 1:
            raise ServiceException("Driving dataset timesteps are not synchronised between variables. "
                                   "Cannot process download")
        return starts[0]

    def get_actual_data_end(self, driving_data, end):
        """
        Get the actual end date of the driving data download
        :param driving_data: The driving data being downloaded
        :param end: The requested end date
        :return: :raise ServiceException: On error with the dates
        """
        self._create_dap_clients_if_missing(driving_data)
        ends = []
        for dap_client in self._dap_clients:
            actual_end = dap_client.get_time_immediately_before(end)
            if actual_end is None:
                raise ServiceException("No datapoints found in the requested time range")
            ends.append(actual_end)
        if len(set(ends)) > 1:
            raise ServiceException("Driving dataset timesteps are not synchronised between variables. "
                                   "Cannot process download")
        return ends[0]

    def _get_data_line(self, driving_data, lat, lon, date):
        self._create_dap_clients_if_missing(driving_data)
        data_values = []
        for dap_client in self._dap_clients:
            data = dap_client.get_data_at(lat, lon, date)
            data_values.append((data))
        return '\t'.join(('%-*G' % (self.col_size, x) for x in data_values)) + "\n"

    def _create_dap_clients_if_missing(self, driving_data):
        if self._dap_clients is None or len(self._dap_clients) == 0:
            self._create_dap_clients(driving_data)

    def _create_dap_clients(self, driving_data):
        self._dap_clients = []
        vars = driving_data.get_python_parameter_value(constants.JULES_PARAM_DRIVE_VAR, is_list=True)
        location_dict = {location.var_name: location.base_url for location in driving_data.locations}
        for var in vars:
            url = self.thredds_url + "dodsC/model_runs/" + location_dict[var]
            dap_client = self._dap_client_factory.get_dap_client(url)
            self._dap_clients.append(dap_client)
