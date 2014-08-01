"""
header
"""
from pylons import config
from joj.crowd.client import CrowdClient


class CrowdClientFactory(object):
    """
    A factory to create configured crowd clients
    """

    def get_client(self):
        """
        Get a configured crowd client
        :return: a crowd client
        """
        crowd_client = CrowdClient()
        crowd_client.config(config)

        return crowd_client
