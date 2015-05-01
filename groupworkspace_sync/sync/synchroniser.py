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
from logging.config import fileConfig
import os
import sys

from sync.clients.majic_web_service_client import MajicWebserviceClient
from sync.common_exceptions import UserPrintableError
from sync.directory_synchroniser import DirectorySynchroniser
from sync.file_system_comparer import FileSystemComparer
from sync.utils.config_accessor import ConfigAccessor

log = logging.getLogger("sync")


class Synchroniser(object):
    """
    Provides services to synchronisation file
    """

    def __init__(self,
                 configuration,
                 majic_webservice_client=None,
                 file_system_comparer=None,
                 directory_synchroniser=None):
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

        if file_system_comparer is None:
            self._file_system_comparer = FileSystemComparer(self._config)
        else:
            self._file_system_comparer = file_system_comparer

        if directory_synchroniser is None:
            self._directory_synchroniser = DirectorySynchroniser(self._config)
        else:
            self._directory_synchroniser = directory_synchroniser

    def synchronise(self):
        """
        Synchronise the files returned by the web service with those on the disc
        :return: error code to exit with
        """
        try:
            log.debug("Starting to sync")
            model_propeties = self._majic_webservice_client.get_properties_list_with_filtered_users()
            self._file_system_comparer.perform_analysis(model_propeties)
            self._file_system_comparer.add_extra_directories_to_sync()
            new_count, updated_count, deleted_count = \
                self._directory_synchroniser.synchronise_all(self._file_system_comparer)
            log.info("Finished Synchronisation:")
            log.info("  {}: Count of copied files and directories: ".format(new_count))
            log.info("  {}: Count of directory permissions updated".format(updated_count))
            log.info("  {}: Count of deleted directories".format(deleted_count))
            return 0
        except UserPrintableError as ex:
            log.error(str(ex))
            return 1
        except Exception:
            log.exception("Unknown error in synchronisation")
            log.error("An unknown error occurred so files are not synced")
            return 2

if __name__ == '__main__':
    config_file = 'production.ini'
    here = os.curdir
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        here = os.path.realpath(os.path.dirname(config_file))
    if not os.path.exists(config_file):
        print("Configuration file doesn't exist ('{}')".format(config_file))
        exit(-1)
    config = ConfigParser.SafeConfigParser({'here': here})
    config.read(config_file)
    fileConfig(config_file)

    sync = Synchroniser(ConfigAccessor(config))
    exit(sync.synchronise())
