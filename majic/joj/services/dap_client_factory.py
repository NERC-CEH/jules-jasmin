"""
# header
"""
import logging
from joj.services.dap_client import DapClient
from joj.lib.wmc_util import create_request_and_open_url


class DapClientFactory(object):
    """
    Factory for creating dap clients
    """

    def get_dap_client(self, url):
        """
        create a return a dap client using the url
        :param url: the url for the dap client to use
        :return: a dap client
        """
        return DapClient(url)