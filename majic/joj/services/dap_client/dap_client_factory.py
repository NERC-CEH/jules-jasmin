"""
# header
"""
from pylons import config
from joj.services.dap_client.dap_client import DapClient
from joj.services.dap_client.graphing_dap_client import GraphingDapClient
from joj.services.dap_client.land_cover_dap_client import LandCoverDapClient
from joj.services.dap_client.soil_properties_dap_client import SoilPropertiesDapClient
from joj.services.dap_client.ancils_dap_client import AncilsDapClient


class DapClientFactory(object):
    """
    Factory for creating dap clients
    """

    def get_full_url_for_file(self, filepath, service="dodsC", config=config):
        """
        Get the full THREDDS URL for a file on the THREDDS server
        :param filepath: Path of file relative to the model run directory.
        :param service: Service name to use (e.g. 'wms', 'dodsC').
        :param config: Configuration file to use
        :return:
        """
        url_template = "{thredds_server_base}/{service}/{run_dir}/{filepath}"
        return url_template.format(thredds_server_base=config["thredds.server_url"].rstrip("/"),
                                   service=service,
                                   run_dir=config["thredds.run_dir_name"].rstrip("/").lstrip("/"),
                                   filepath=filepath)

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

    def get_soil_properties_dap_client(self, url):
        """
        Create and return a Soil properties DAP Client
        :param url: URL for the DAP Client to use
        :return:
        """
        return SoilPropertiesDapClient(url)

    def get_ancils_dap_client(self, url):
        """
        Create and return an Ancillary files DAP Client
        :param url: URL for the DAP Client to use
        :return: AncilsDapClient
        """
        return AncilsDapClient(url)