"""
header
"""
from joj.services.dap_client.dap_client_factory import DapClientFactory
from joj.services.model_run_service import ModelRunService
from joj.lib.wmc_util import create_request_and_open_url
from joj.utils.download.dataset_download_helper import DatasetDownloadHelper


class NetcdfDatasetDownloadHelper(DatasetDownloadHelper):
    """
    Manages the download of whole datasets.
    """

    def __init__(self, model_run_service=ModelRunService(), dap_client_factory=DapClientFactory()):
        super(NetcdfDatasetDownloadHelper, self).__init__(model_run_service, dap_client_factory)

    def download_file_generator(self, file_path, model_run):
        """
        Download an output file from the THREDDS file server and serve it to the user
        :param file_path: File path to download
        :return: Generator (for streamed download)
        """
        url = self.dap_client_factory.get_full_url_for_file(file_path, service="fileServer")
        dataset = create_request_and_open_url(url)
        for line in dataset.read():
            yield (line)

    def set_response_header(self, header_dict, filepath):
        """
        Set the download information on a Pylons header
        :param header_dict: Pylons Header (response.header)
        :param filepath: File path (relative to run dir)
        :return:
        """

        # Get the HTTP header from THREDDS to identify the file size
        url = self.dap_client_factory.get_full_url_for_file(filepath, service="fileServer")
        head = create_request_and_open_url(url, method='HEAD').headers

        filename = filepath.split('/')[-1]
        header_dict['Content-Type'] = str(head['Content-Type'])
        header_dict['Content-Disposition'] = str('attachment; filename="%s"' % filename)
        header_dict['Content-Length'] = str(head['Content-Length'])
