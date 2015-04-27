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
import os
import pwd
from stat import S_IRGRP, S_IROTH
import subprocess

from src.sync.common_exceptions import UserPrintableError
from sync.file_properties import FileProperties
from src.sync.utils.constants import CONFIG_ROOT_PATH, CONFIG_FILES_SECTION, CONFIG_DELETE_SCRIPT_PATH, \
    CONFIG_UPDATE_PERMISSIONS_SCRIPT_PATH

log = logging.getLogger(__name__)


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
        self._config.set_section(CONFIG_FILES_SECTION)
        self._filesystem_root_for_app = os.path.realpath(self._config.get(CONFIG_ROOT_PATH))
        self._del_dir_script = self._config.get(CONFIG_DELETE_SCRIPT_PATH)
        self._update_permissions_script = self._config.get(CONFIG_UPDATE_PERMISSIONS_SCRIPT_PATH)

    def _create_full_path(self, relative_path):
        """
        Create a full path based on the relative path in the filesystem root path
        :param relative_path: the relative path
        :return: full path
        """
        real_full_path = os.path.realpath(os.path.join(self._filesystem_root_for_app, relative_path))
        if not real_full_path.startswith(self._filesystem_root_for_app):
            raise AssertionError("Code is trying to access a directory outside root with path '{}'"
                                 .format(relative_path))
        return real_full_path

    def create_dir(self, relative_directory):
        """
        Create a directory tree in the file path root with relative path. If directory already exists don't do anything
        :param relative_directory: the relative directory to create
        :return: nothing
        """
        full_path = self._create_full_path(relative_directory)
        try:
            os.makedirs(full_path)
        except OSError as ex:
            if ex.errno != 17:
                # directory exists
                log.exception("Error creating directory '{}'.".format(full_path))
                raise FileSystemClientError("Error creating directory.")
        except Exception:
            log.exception("Error creating directory '{}'.".format(full_path))
            raise FileSystemClientError("Error creating directory.")

    def create_file(self, relative_file_path):
        """
        Creates a file and returns the open file object
        Caller is expected to close the file
        :param relative_file_path: the relative file path
        :return: file handle object, or None if the file already exists
        """
        full_path = self._create_full_path(relative_file_path)
        try:
            if os.path.exists(full_path):
                return None
            return open(full_path, 'w')
        except Exception:
            log.exception("Error creating file '{}'.".format(full_path))
            raise FileSystemClientError("Error creating file.")

    def close_file(self, file_object):
        """
        Close the file_object
        :param file_object: the file_object handle to close
        :return: nothing
        """
        try:
            file_object.close()
        except Exception:
            log.exception("Error closing file object '{}'".format(file_object))
            raise FileSystemClientError("Error closing file.")

    def close_and_delete_file(self, file_object):
        """
        Delete the file_object previously opened
        :param file_object: the open file_object object
        :return:nothing
        """
        try:
            self.close_file(file_object)
            os.remove(file_object.name)
        except Exception:
            log.exception("Error closing and deleting file object '{}'".format(file_object))
            raise FileSystemClientError("Error closing and deleting file.")

    def _run_script_using_sudo(self, action, script_and_var):
        try:
            script_and_var.insert(0, "sudo")
            subprocess.check_output(script_and_var, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as ex:
            log.exception("Error when {}".format(action))
            raise FileSystemClientError("Error when {}. Error: {}".format(action, ex.output))
        except Exception as ex:
            log.exception("Unknown problem when {}".format(action))
            raise ex

    def delete_directory(self, relative_path):
        """
        Delete a directory and its contents
        :param relative_path: the file of the file relative to the filesystem root
        :return: count of deleted directories
        """
        script_and_var = [self._del_dir_script, relative_path]
        action = "deleting directory '{}'".format(relative_path)
        self._run_script_using_sudo(action, script_and_var)

    def set_permissions(self, file_property):
        """
        Set the permissions for the file property object
        :param file_property: the file property object
        :return: nothing
        """
        script_and_var = [
            self._update_permissions_script,
            file_property.file_path,
            file_property.owner,
            str(file_property.is_published),
            str(file_property.is_public)]
        action = "setting permissions on directory '{}'".format(file_property.file_path)
        self._run_script_using_sudo(action, script_and_var)

    def get_file_properties(self, relative_path):
        """
        Create a file properties object from a file path
        :param relative_path: the relative file to read
        :returns: file properties
        :raises IOError: if the file does not exist
        """
        full_path = self._create_full_path(relative_path)
        stat = os.stat(full_path)
        owner = pwd.getpwuid(stat.st_uid).pw_name
        published = bool(stat.st_mode & S_IRGRP)
        public = bool(stat.st_mode & S_IROTH)
        return FileProperties(relative_path, owner, published, public)
