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
from src.sync.common_exceptions import UserPrintableError
from src.sync.utils.constants import CONFIG_WS_SECTION


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
        :param config: configuration to use
        :return: nothing
        """
        super(MajicWebserviceClient, self).__init__()
        self._config = config

    def get_properties_list(self):
        """
        Get the files and their properties from the web service
        :return: the files and their properties
        """
        raise WebserviceClientError(
            "Can not contact Majic Web Service (trying {})".format(self._config.get(CONFIG_WS_SECTION, "url")))