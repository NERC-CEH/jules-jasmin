"""
header
"""
import os
import sys
from pylons import config
from joj.utils.download.dataset_download_helper import DatasetDownloadHelper
from joj.services.dap_client.dap_client_factory import DapClientFactory
from joj.services.model_run_service import ModelRunService
from joj.utils import constants


class AsciiDatasetDownloadHelper(DatasetDownloadHelper):
    """
    Manges ASCII download of output datasets
    """
    header = """# MAJIC SINGLE CELL OUTPUT DATA DOWNLOAD
#
# This is a download of output data for a single cell JULES run.
#
# Model Run Name: {mr_name}
# Date Completed: {mr_date}
# Latitude: {lat}
# Lon: {lon}

# The output variable in this file is:
# {longname} ({units})
#
# The first row of data is at: {start}
# The last row of data is at: {end}
# The data time period is: {period} seconds
"""

    def __init__(self, model_run_service=ModelRunService(), dap_client_factory=DapClientFactory(), config=config):
        super(AsciiDatasetDownloadHelper, self).__init__(model_run_service, dap_client_factory, config=config)
        self.dap_client = None

    def _make_file_header(self, model_run, dap_client):
        lat, lon = dap_client.get_closest_lat_lon(0, 0)
        mr_start = model_run.get_python_parameter_value(constants.JULES_PARAM_RUN_START)
        mr_end = model_run.get_python_parameter_value(constants.JULES_PARAM_RUN_END)
        actual_start = dap_client.get_time_immediately_after(mr_start)
        actual_end = dap_client.get_time_immediately_before(mr_end)
        period = dap_client.get_period()
        longname = dap_client.get_longname()
        units = dap_client.get_variable_units()

        return self.header.format(mr_name=model_run.name,
                                  mr_date=model_run.last_status_change,
                                  lat=lat,
                                  lon=lon,
                                  start=actual_start,
                                  end=actual_end,
                                  period=period,
                                  longname=longname,
                                  units=units)

    def _estimate_filesize(self, dap_client):
        header_size = sys.getsizeof(self.header, None)
        nlines = dap_client.get_number_of_times()
        data_size = 15.5 * nlines  # Estimate measured from sample files
        return int(header_size + data_size)

    def _get_dap_client(self, filepath):
        url = self.dap_client_factory.get_full_url_for_file(filepath, config=self.config)
        if self.dap_client is None or self.dap_client.url != url:
            self.dap_client = self.dap_client_factory.get_dap_client(url)
        return self.dap_client

    def set_response_header(self, header_dict, filepath):
        """
        Set the download information on a Pylons header
        :param header_dict: Pylons Header (response.header)
        :param filepath: File path (relative to run dir)
        :return:
        """
        dap_client = self._get_dap_client(filepath)
        filename = filepath.split('/')[-1]
        path, ext = os.path.splitext(filename)
        ascii_filename = path + constants.USER_DOWNLOAD_DATA_FILE_EXTENSION
        header_dict['Content-Type'] = str('text/plain')
        header_dict['Content-Disposition'] = str('attachment; filename="%s"' % ascii_filename)
        header_dict['Content-Length'] = str(self._estimate_filesize(dap_client))

    def download_file_generator(self, file_path, model_run):
        """
        Download an output file from the THREDDS file server and serve it to the user as ASCII
        :param file_path: File path to download
        :param model_run: Model run to use
        :return: Generator (for streamed download)
        """
        dap_client = self._get_dap_client(file_path)
        header = self._make_file_header(model_run, dap_client)
        yield header
        n_points = dap_client.get_number_of_times()
        index = 0
        while index <= n_points:
            data = dap_client.get_data_by_chunk(index, chunk_size=constants.GRAPH_NPOINTS)
            index += constants.GRAPH_NPOINTS
            for datum in data:
                yield str(datum) + str("\r\n")
