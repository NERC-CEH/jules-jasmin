"""
#    Majic
#    Copyright (C) 2015  CEH
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
import logging
import requests
from requests.packages.urllib3 import Timeout
from requests.exceptions import RequestException
from src.sync.common_exceptions import UserPrintableError
from src.sync.utils.constants import CONFIG_WS_SECTION, CONFIG_MAJIC_WS_CERT_PATH, CONFIG_MAJIC_WS_USER_KEY_PATH, \
    CONFIG_MAJIC_WS_USER_CERT_PATH, CONFIG_URL, JSON_MODEL_RUNS

log = logging.getLogger(__name__)


class WebserviceClientError(UserPrintableError):
    """
    Error thrown when there is an identifiable error in the web service. Must include a
    message which is printable for a user
    """
    
    def __init__(self, message):
        """
        Constructor
        :param message: message for the user
        :returns: nothing
        """
        super(WebserviceClientError, self).__init__(message)


class MajicWebserviceClient(object):
    """
    Client to access the majic web service
    """

    def __init__(self, config):
        """
        Constructor
        :param config: configuration to use (expecting a config accessor)
        :return: nothing
        """
        super(MajicWebserviceClient, self).__init__()
        self._config = config
        self._config.set_section(CONFIG_WS_SECTION)

    def get_properties_list(self):
        """
        Get the files and their properties from the web service
        :return: the files and their properties
        """
        properties = self._get_securely(self._config.get(CONFIG_URL))
        return properties[JSON_MODEL_RUNS]

    def _get_securely(self, url):
        """
        Use the ssl certificates to get some data
        :param url: the url to get
        :return: the response as json
        :raises WebserviceClientError: if there are connection problems
        """

        verify = self._config.get(CONFIG_MAJIC_WS_CERT_PATH, default=True)

        cert = None
        cert_path = self._config.get(CONFIG_MAJIC_WS_USER_CERT_PATH, default=None)
        if cert_path is not None:
            key_path = self._config.get(CONFIG_MAJIC_WS_USER_KEY_PATH)
            cert = (cert_path, key_path)

        try:
            return requests.get(url=url, verify=verify, cert=cert).json()
        except Timeout:
            log.exception("Timeout during post to Majic Web Service, url {}".format(url))
            raise WebserviceClientError("Can not contact {} (trying {})".format(url))
        except RequestException:
            log.exception("Connection error on post to Majic Web Service to url {}".format(url))
            raise WebserviceClientError("There is a connection error when contacting the Majic Web Service (trying {})"
                                        .format(url))
