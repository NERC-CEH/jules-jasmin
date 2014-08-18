"""
# header
"""
from joj.services.dap_client.dap_client import DapClient
from joj.services.dap_client.graphing_dap_client import GraphingDapClient
from joj.services.dap_client.land_cover_dap_client import LandCoverDapClient


class DapClientFactory(object):
    """
    Factory for creating dap clients
    """

    def get_dap_client(self, url):
        """
        Create and return a DAP client using the URL
        :param url: URL for the DAP client to use
        :return: Dapclient
        """
        return DapClient(url)

    def get_land_cover_dap_client(self, url, key='frac'):
        """
        Create and return a Land Cover DAP Client
        :param url: URL for the DAP Client to use
        :param key: the variable key for the land cover pseudo dimension
        :return: LandCoverDapClient
        """
        return LandCoverDapClient(url, key)

    def get_graphing_dap_client(self, url):
        """
        Create and return a 2D Graphing DAP Client
        :param url: URL for the DAP Client to use
        :return: GraphingDapClient
        """
        return GraphingDapClient(url)