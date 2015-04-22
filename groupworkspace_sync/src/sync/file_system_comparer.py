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
import pwd
from stat import S_IRGRP, S_IROTH
import re
import os
from src.sync.utils.constants import CONFIG_DATA_SECTION, JSON_MODEL_RUN_ID, CONFIG_DATA_PATH, JSON_USER_NAME, \
    JSON_IS_PUBLIC, JSON_IS_PUBLISHED


class FileProperties(object):
    """
    Important properties of a file needing to be synchronised
    """

    def __init__(self, file_path, owner, is_published, is_public):
        """
        constructor
        :param file_path: path to the file relative to the root
        :param owner: userid of the user who owns the file
        :param is_published: True if the file is published, false otherwise (i.e. readable by majic users)
        :param is_public: True if the file is public, false otherwise (i.e. readable by everyone)
        """
        self.file_path = file_path
        self.owner = owner
        self.is_published = is_published
        self.is_public = is_public

    def __repr__(self):
        return "{} (model_owner:{}, published?:{}, public?:{})"\
            .format(self.file_path, self.owner, self.is_published, self.is_public)

    def __cmp__(self, other):
        """
        Compare two File properties
        Order is filepath, model_owner, is_publoshed, is_publis
        :param other: other File Property to compare
        :return: negative integer if self < other, zero if self == other, a positive integer if self > other
        """
        if self.file_path != other.file_path:
            if self.file_path < other.file_path:
                return -1
            else:
                return 1

        if self.owner != other.owner:
            if self.owner < other.owner:
                return -1
            else:
                return 1

        result = self.is_published.__cmp__(other.is_published)
        if result == 0:
            result = self.is_public.__cmp__(other.is_public)
        return result

    @staticmethod
    def from_path(path, base_directory=None):
        """
        Create a file properties object from a file path
        :param path: the file to read
        :param base_directory: the relative path from which the path should be started,
            None for from current directory
        :returns: file properties
        :raises IOError: if the file does not exist
        """
        full_path = path
        if base_directory is not None:
            full_path = os.path.join(base_directory, path)
        stat = os.stat(full_path)
        owner = pwd.getpwuid(stat.st_uid).pw_name
        published = bool(stat.st_mode & S_IRGRP)
        public = bool(stat.st_mode & S_IROTH)
        return FileProperties(path, owner, published, public)


class FileSystemComparer(object):
    """
    Compare the list of directories on the file system with a list of model and detect changes
    """

    def __init__(
            self,
            config,
            existing_directories,
            model_properties,
            get_file_properties_from_path=FileProperties.from_path):
        """
        Constructor
        :param config: configuration for file system comparer
        :param existing_directories: list of directories in current directory
        :param model_properties: model properties expected to appear
        :param get_file_properties_from_path: a method to generate the file properties from a file,
            defaults to FileProperties.from path
        :return: nothing but set internal properties for new, changed and deleted files
        """
        self._config = config
        self._config.set_section(CONFIG_DATA_SECTION)
        self._get_file_properties_from_path = get_file_properties_from_path
        self.new_directories = []
        self.deleted_directories = []
        self.changed_directories = []

        existing_run_ids = set()
        for existing_directory in existing_directories:
            match = re.match('run(\d+)', existing_directory)
            if match:
                existing_run_ids.add(int(match.group(1)))

        model_run_ids = set()
        file_properties_for_model_runs = {}
        for model_property in model_properties:
            model_run_id = model_property[JSON_MODEL_RUN_ID]
            model_run_ids.add(model_run_id)
            file_properties_for_model_runs[model_run_id] = FileProperties(
                self._create_model_dir(model_run_id),
                model_property[JSON_USER_NAME],
                model_property[JSON_IS_PUBLISHED],
                model_property.get(JSON_IS_PUBLIC, False))

        for model_run_id in model_run_ids.difference(existing_run_ids):
            self.new_directories.append(file_properties_for_model_runs[model_run_id])

        for model_run_id in existing_run_ids.difference(model_run_ids):
            self.deleted_directories.append(self._create_model_dir(model_run_id))

        existing_run_ids.intersection_update(model_run_ids)
        for model_run_id in existing_run_ids:
            file_properties_to_set = file_properties_for_model_runs[model_run_id]
            current_file_properties = self._get_file_properties_from_path(file_properties_to_set.file_path)
            if current_file_properties != file_properties_for_model_runs[model_run_id]:
                self.changed_directories.append(file_properties_to_set)

    def _create_model_dir(self, model_run_id):
        """
        Create the model run dir path from the model run id
        :param model_run_id: model run id
        :return: the full path to the model run directory
        """
        #  ensure that the model id is a number so it can not possible contain path elements
        model_run_id_dir = str(model_run_id)
        assert(model_run_id_dir.isdigit())

        data_path = self._config.get(CONFIG_DATA_PATH)
        dir_name = "run{}".format(model_run_id)
        return os.path.join(data_path, dir_name)
