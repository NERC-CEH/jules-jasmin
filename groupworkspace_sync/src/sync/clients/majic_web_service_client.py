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
import pwd
import requests
from requests.exceptions import RequestException, Timeout
from src.sync.common_exceptions import UserPrintableError
from src.sync.utils.constants import CONFIG_WS_SECTION, CONFIG_MAJIC_WS_CERT_PATH, CONFIG_MAJIC_WS_USER_KEY_PATH, \
    CONFIG_MAJIC_WS_USER_CERT_PATH, CONFIG_URL, JSON_MODEL_RUNS, CONFIG_DATA_NOBODY_USERNAME, JSON_USER_NAME, \
    CONFIG_DATA_SECTION, CONFIG_MAJIC_WS_TIMEOUT

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
        Returns a dictionary with the model_runs element which is a list of dictionaries for the runs
        :return: the files and their properties
        """
        properties = self._get_securely(self._config.get(CONFIG_URL))
        return properties

    def get_properties_list_with_filtered_users(self):
        """
        Get the files and their properties from the web service and then filters the users to ensure that
        the users exist on the current system
        Returns a dictionary with the model_runs element which is a list of dictionaries for the runs
        :return: the files and their properties
        """
        model_run_properties = self.get_properties_list()[JSON_MODEL_RUNS]
        for model_run_property in model_run_properties:
            username = model_run_property[JSON_USER_NAME]
            nobody_username = self._config.get(CONFIG_DATA_NOBODY_USERNAME, section=CONFIG_DATA_SECTION)
            if username is None or len(username.strip()) == 0:
                model_run_property[JSON_USER_NAME] = nobody_username
            else:
                try:
                    pwd.getpwnam(username)
                except KeyError:
                    model_run_property[JSON_USER_NAME] = nobody_username
        return model_run_properties

    def _get_securely(self, url):
        """
        Use the ssl certificates to get some data
        :param url: the url to get
        :return: the response as json
        :raises WebserviceClientError: if there are connection problems
        """

        timeout_as_string = self._config.get(CONFIG_MAJIC_WS_TIMEOUT)
        verify = self._config.get(CONFIG_MAJIC_WS_CERT_PATH, default=True)

        cert = None
        cert_path = self._config.get(CONFIG_MAJIC_WS_USER_CERT_PATH, default=None)
        if cert_path is not None:
            key_path = self._config.get(CONFIG_MAJIC_WS_USER_KEY_PATH)
            cert = (cert_path, key_path)
        try:
            return requests.get(url=url, verify=verify, cert=cert, timeout=float(timeout_as_string)).json()
        except Timeout:
            log.exception("Timeout during post to Majic Web Service, url {}".format(url))
            raise WebserviceClientError("Timeout when contacting the Majic Web Service (trying {})".format(url))
        except RequestException:
            log.exception("Connection error on post to Majic Web Service to url {}".format(url))
            raise WebserviceClientError("There is a connection error when contacting the Majic Web Service (trying {})"
                                        .format(url))
