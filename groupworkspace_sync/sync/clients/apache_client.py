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
import socket
import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException, Timeout
from sync.common_exceptions import UserPrintableError
from sync.utils.constants import CONFIG_APACHE_SECTION, CONFIG_APACHE_USERNAME, CONFIG_APACHE_PASSWORD, \
    DOWNLOAD_CHUNK_SIZE_IN_BYTES, CONFIG_APACHE_TIMEOUT, CONFIG_APACHE_ROOT_PATH

log = logging.getLogger(__name__)


class ApacheClientError(UserPrintableError):
    """
    Error thrown when there is an identifiable error in the apache client. Must include a
    message which is printable for a user
    """

    def __init__(self, message):
        """
        Constructor
        :param message: message for the user
        :returns: nothing
        """
        super(ApacheClientError, self).__init__(message)


class ApacheClient(object):
    """
    A client to request data from the apache server
    """

    def __init__(self, config):
        """
        Constructor
        :param config: configuration for this object
        :return: nothing
        """
        self._config = config

    def _request_to_apache(self, url):
        """
        open a request to the url given for the apache file server
        :param url: uel to use
        :return: request
        :raises ApacheClientError: when there is a problem connecting to the url
        """
        self._config.set_section(CONFIG_APACHE_SECTION)
        try:
            auth = HTTPBasicAuth(username=self._config.get(CONFIG_APACHE_USERNAME),
                                 password=self._config.get(CONFIG_APACHE_PASSWORD))
            timeout_as_string = self._config.get(CONFIG_APACHE_TIMEOUT)
            request = requests.get(url, auth=auth, timeout=float(timeout_as_string))
            return request
        except Timeout:
            log.exception("Timeout during get from apache file server, url {}".format(url))
            raise ApacheClientError("Timeout when contacting apache file server (trying url {})".format(url))
        except socket.timeout:
            log.exception("Socket timeout during get from apache file server, url {}".format(url))
            raise ApacheClientError("Timeout when contacting apache file server (trying url {})".format(url))
        except RequestException:
            log.exception("Connection error when contacting the apache file server (trying url {})".format(url))
            raise ApacheClientError("There is a connection error when contacting the apache file server (trying {})"
                                    .format(url))

    def _links_in_table_data(self, tag):
        """
        Is this tag a link in a table data which is not "Parent Directory"
        :param tag: the tag to check
        :returns true if this is a file link; false otherwise
        """
        return tag.name == 'a' and tag.parent.name == "td" and tag.text != 'Parent Directory'

    def _create_full_url(self, relative_url):
        """
        Create the full url for the relative url
        :param relative_url:
        :return: full url with server prefix
        """
        url = "{}/{}".format(self._config.get(CONFIG_APACHE_ROOT_PATH, CONFIG_APACHE_SECTION), relative_url)
        return url

    def get_contents(self, directory):
        """
        Return a list of contents at the url, excluding the parent directory
        :param directory: the directory to open
        :return: list of file and directories in that directory
        """
        url = self._create_full_url(directory)
        file_list_response = self._request_to_apache(url)
        file_list_page = BeautifulSoup(file_list_response.text)

        content_links = file_list_page.find_all(self._links_in_table_data)

        content_list = []
        for content_link in content_links:
            content_list.append(content_link.text)

        return content_list

    def download_file(self, relative_file_path, file_handle):
        """
        Download and save a file
        :param relative_file_path: relative url for the file download
        :param file_handle: the file handle to write the file to
        :return: nothing
        """
        url = self._create_full_url(relative_file_path)
        request = self._request_to_apache(url)
        for chunk in request.iter_content(DOWNLOAD_CHUNK_SIZE_IN_BYTES):
            file_handle.write(chunk)
