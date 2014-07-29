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

    def __init__(self):
        super(DapClientFactory, self).__init__()

        def new_request(url):
            """
            Create a new dap request
            :param url: the url
            :return: headers and body tuple
            """
            log = logging.getLogger('pydap')
            log.INFO('Opening %s' % url)

            f = create_request_and_open_url(url.rstrip('?&'))
            headers = dict(f.info().items())
            body = f.read()
            return headers, body

        from pydap.util import http
        http.request = new_request

    def get_dap_client(self, url):
        """
        create a return a dap client using the url
        :param url: the url for the dap client to use
        :return: a dap client
        """
        return DapClient(url)