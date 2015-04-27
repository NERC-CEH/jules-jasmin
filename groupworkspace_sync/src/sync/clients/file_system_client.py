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
from sync.common_exceptions import UserPrintableError
from sync.utils.constants import CONFIG_ROOT_PATH


class FileSystemClientError(UserPrintableError):
    """
    Error thrown when there is an identifiable error in the file system client. Must include a
    message which is printable for a user
    """

    def __init__(self, message):
        """
        Constructor
        :param message: message for the user
        :returns: nothing
        """
        super(FileSystemClientError, self).__init__(message)


class FileSystemClient(object):
    """
    File system client to interact with the file system
    """

    def __init__(self, config):
        self._config = config

    def _create_full_path(self, relative_path):
        """
        Create a full path based on the relative path in the filesystem root path
        :param relative_path: the relative path
        :return: full path
        """
        return os.path.join(self._config.get(CONFIG_ROOT_PATH), relative_path.file_path)

    def create_dir(self, relative_directory):
        """
        Create a directory tree in the file path root with relative path. If directory already exists don't do anything
        :param relative_directory: the relative directory to create
        :return: nothing
        """
        self._create_full_path(relative_directory)
        raise NotImplementedError()

    def set_permissions(self, file_property):
        """
        Set the permissions for the file property object
        :param file_property: the file property object
        :return: nothing
        """
        self._create_full_path(file_property)
        raise NotImplementedError()

    def create_file(self, relative_file_path):
        """
        Creates a file and returns the open file object
        Caller is expected to close the file
        :param relative_file_path: the relative file path
        :return: file handle object, or None if the file already exists
        """
        self._create_full_path(relative_file_path)
        raise NotImplementedError()

    def close_file(self, file_handle):
        """
        Close the file_handle
        :param file_handle: the file_handle handle to close
        :return: nothing
        """
        file_handle.close()

    def close_and_delete_file(self, file):
        """
        Delete the file previously opened
        :param file: the open file object
        :return:nothing
        """
        raise NotImplementedError()
        self.close_file(file)
        os.remove(file.name)