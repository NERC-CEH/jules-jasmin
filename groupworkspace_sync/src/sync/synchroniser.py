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
import ConfigParser
import logging
import os

from src.sync.clients.majic_web_service_client import MajicWebserviceClient, WebserviceClientError
from utils.config_accessor import ConfigAccessor

log = logging.getLogger(__name__)


class Synchroniser(object):
    """
    Provides services to synchronisation file
    """

    def __init__(self, configuration, majic_webservice_client=None):
        """
        Constructor
        :param configuration: the configuration to use for the synchronisation
        :param majic_webservice_client: the majic web service to use
        :return: nothing
        """
        super(Synchroniser, self).__init__()
        self._config = configuration

        if majic_webservice_client is None:
            self._majic_webservice_client = MajicWebserviceClient(self._config)
        else:
            self._majic_webservice_client = majic_webservice_client

    def synchronise(self):
        """
        Synchronise the files returned by the web service with those on the disc
        :return: error code to exit with
        """
        try:
            self._majic_webservice_client.get_properties_list_with_filtered_users()
            return 0
        except WebserviceClientError as ex:
            log.error(str(ex))
            return 1
        except Exception:
            log.exception("Unknown error in synchronisation")
            log.error("An unknown error occurred so files are not synced")
            return 2

if __name__ == '__main__':

    config = ConfigParser.SafeConfigParser({'here': os.curdir})
    config.read('production.ini')
    sync = Synchroniser(ConfigAccessor(config))
    exit(sync.synchronise())
