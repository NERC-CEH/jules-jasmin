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
import re
import os
from sync.clients.apache_client import ApacheClient, ApacheClientError
from sync.clients.file_system_client import FileSystemClient, FileSystemClientError
from sync.utils.constants import CONFIG_DATA_SECTION, CONFIG_EXTENSIONS_TO_COPY, CONFIG_CONTENT_TO_IGNORE_REGEX

log = logging.getLogger(__name__)


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
        if apache_client is None:
            self._apache_client = ApacheClient(self._config)
        else:
            self._apache_client = apache_client

        if file_system_client is None:
            self._file_system_client = FileSystemClient(self._config)
        else:
            self._file_system_client = file_system_client

        self.extensions_to_copy = self._config.get(CONFIG_EXTENSIONS_TO_COPY, CONFIG_DATA_SECTION).split()
        regexes = self._config.get(CONFIG_CONTENT_TO_IGNORE_REGEX, CONFIG_DATA_SECTION).split()
        self._regexes = [re.compile(expression) for expression in regexes]

    def _copy_directory_content_item(self, directory_content, relative_directory_path):
        """
        Copy an item in a directory
        :param directory_content: the name of content to copy
        :param relative_directory_path: the relative path of the directory
        :return: count of copied items
        """
        relative_file_path = os.path.join(relative_directory_path, directory_content)

        # check that content doesn't match some ignored content
        for regex in self._regexes:
            if regex.search(relative_file_path):
                return 0

        if relative_file_path.endswith('/'):
            return self._copy_directory(relative_file_path[:-1])

        path, ext = os.path.splitext(relative_file_path)
        if ext not in self.extensions_to_copy:
            return 0

        new_file = self._file_system_client.create_file(relative_file_path)
        if new_file is None:
            # file already exists
            return 0

        try:
            self._apache_client.download_file(relative_file_path, new_file)
            self._file_system_client.close_file(new_file)
            return 1
        except Exception as ex:
            self._file_system_client.close_and_delete_file(new_file)
            raise ex

    def _copy_directory(self, new_directory_path):
        """
        Copy a directory and all its sub directories
        :param new_directory_path:
        :return: number of files and directories copied
        """
        copied_count = 0
        try:
            if self._file_system_client.create_dir(new_directory_path):
                copied_count += 1

            directory_contents = self._apache_client.get_contents(new_directory_path)
            for directory_content in directory_contents:
                try:
                    copied_count += self._copy_directory_content_item(directory_content, new_directory_path)
                except FileSystemClientError as ex:
                    # log the error and skip content
                    log.error("Error opening the file {} in directory {}. {}"
                              .format(directory_content, new_directory_path, ex.message))
                except ApacheClientError as ex:
                    # log the error and skip directory
                    log.error("Error downloading file from apache for file {} in directory {}. {}"
                              .format(directory_content, new_directory_path, ex.message))

        except ApacheClientError as ex:
            # log the error and skip directory
            log.error("Error contacting apache for directory contents of {}. {}".format(new_directory_path, ex.message))
        except FileSystemClientError as ex:
            # log the error and skip directory
            log.error("Error creating a directory {}. {}".format(new_directory_path, ex.message))

        return copied_count

    def copy_new(self, new_directories):
        """
        copy new directories and their content from apache
        :param new_directories: the new directory file properties to copy
        :return: number of files and directories copied
        """
        copied_count = 0
        for new_directory in new_directories:
            log.info("Copying New Directory: {}".format(new_directory.file_path))
            new_directory_path = new_directory.file_path
            current_count = self._copy_directory(new_directory_path)
            if current_count > 0:
                self._file_system_client.set_permissions(new_directory)
            copied_count += current_count

        return copied_count

    def update_permissions(self, changed_directories):
        """
        Update the permissions of changed directories
        :param changed_directories: the directories that have changed
        :return: count of directories changed
        """
        update_count = 0
        for changed_directory in changed_directories:
            log.info("Updating Permissions on directory: {}".format(changed_directory.file_path))
            try:
                self._file_system_client.set_permissions(changed_directory)
                update_count += 1
            except FileSystemClientError as ex:
                # log the error and skip directory
                log.error("Error when setting permissions on directory {}. {}".format(changed_directory, ex.message))
        return update_count

    def delete(self, deleted_directories):
        """
        Delete directories which are no longer present
        :param deleted_directories: the directories to delete
        :return: count of deleted directories
        """
        delete_count = 0
        for deleted_directory in deleted_directories:
            log.info("Deleting directory: {}".format(deleted_directory))
            try:
                self._file_system_client.delete_directory(deleted_directory)
                delete_count += 1
            except FileSystemClientError as ex:
                # log the error and skip directory
                log.error("Error when setting permissions on directory {}. {}".format(deleted_directory, ex.message))
        return delete_count

    def synchronise_all(self, directory_types):
        """
        Synchronise the directory dtructure based on directory type
        :param directory_types: a object holding new, changed and deleted directories
        :return: count of new, updated and deleted file and directories
        """
        new_count = self.copy_new(directory_types.new_directories) + \
            self.copy_new(directory_types.existing_non_deleted_directories)
        return (
            new_count,
            self.update_permissions(directory_types.changed_directories),
            self.delete(directory_types.deleted_directories))
