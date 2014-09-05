"""
header
"""
from pylons import config
import requests
from joj.services.general import ServiceException


class FileServerClient(object):
    """
    Client for interacting with the THREDDS fileserver
    """

    def __init__(self):
        super(FileServerClient, self).__init__()
        if config.get('run_in_test_mode', '').lower() == 'true':
            self.file_exists = lambda(filename): True

    def file_exists(self, filename):
        """
        Does a file exist (according to thredds)
        :param filename: filename to query
        :return: true if it exists; false otherwise
        """
        try:
            url = "{}/fileServer/{}".format(config["thredds.server_url"].rstrip('/'), filename)

            head_response = self._get_head_securely(url)
            return head_response.status_code == requests.codes.ok
        except requests.ConnectionError:
            raise ServiceException("Can not connect to Map server to determine whether the files exist")

    def _get_head_securely(self, url):
        """
        Use the ssl certificates to get the head for some data
        :param url: the url to get head of
        :return: the response
        """
        verify = False
        cert = None
        if config and 'majic_certificate_path' in config:
            cert = (config['majic_certificate_path'], config['majic_certificate_key_path'])

        return requests.head(url=url, verify=verify, cert=cert)
