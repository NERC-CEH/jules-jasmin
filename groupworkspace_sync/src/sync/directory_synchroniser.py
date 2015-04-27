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
import os
from src.sync.clients.apache_client import ApacheClient
from src.sync.clients.file_system_client import FileSystemClient
from sync.utils.constants import CONFIG_FILES_SECTION, CONFIG_DATA_SECTION, CONFIG_EXTENSIONS_TO_COPY


class DirectorySynchroniser(object):
    """
    Synchronise Directories and their content between the apache file server and the local filesystem
    It only copies new files, it does not check file contents or delete old file

    Only files with extensions in the configuration file are copied
    """

    def __init__(self, config, apache_client=None, file_system_client=None):
        """
        Constructor
        :param config: configuration accessor
        :param apache_client: client to contact apache
        :param file_system_client: client to contact the file system
        :return: nothing
        """
        self._config = config
        self._config.set_section(CONFIG_FILES_SECTION)
        if apache_client is None:
            self._apache_client = ApacheClient(self._config)
        else:
            self._apache_client = apache_client

        if file_system_client is None:
            self._file_system_client = FileSystemClient(self._config)
        else:
            self._file_system_client = file_system_client

        self.extensions_to_copy = self._config.get(CONFIG_EXTENSIONS_TO_COPY, CONFIG_DATA_SECTION).split()

    def _copy_directory(self, new_directory_path):
        """
        Copy a directory and all its sub directories
        :param new_directory_path:
        :return: number of files and directories copied
        """
        self._file_system_client.create_dir(new_directory_path)
        copied_count = 1

        directory_contents = self._apache_client.get_contents(new_directory_path)
        for directory_content in directory_contents:
            if directory_content.endswith('/'):
                sub_dir = os.path.join(new_directory_path, directory_content[:-1])
                copied_count += self._copy_directory(sub_dir)

            path, ext = os.path.splitext(directory_content)
            if ext in self.extensions_to_copy:
                relative_file_path = os.path.join(new_directory_path, directory_content)
                new_file = self._file_system_client.open_file(relative_file_path)
                self._apache_client.download_file(relative_file_path, new_file)
                self._file_system_client.close_file(new_file)
                copied_count += 1
        return copied_count

    def copy_new(self, new_directories):
        """
        copy new directories and their content from apache
        :param new_directories: the new directory file properties to copy
        :return: number of files and directories copied
        """
        copied_count = 0
        for new_directory in new_directories:
            new_directory_path = new_directory.file_path
            copied_count += self._copy_directory(new_directory_path)
            self._file_system_client.set_permissions(new_directory)
        return copied_count