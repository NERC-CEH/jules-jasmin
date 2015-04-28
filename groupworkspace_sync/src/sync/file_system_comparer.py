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

from src.sync.utils.constants import CONFIG_DATA_SECTION, JSON_MODEL_RUN_ID, CONFIG_DATA_PATH, JSON_USER_NAME, \
    JSON_IS_PUBLIC, JSON_IS_PUBLISHED, MODEL_RUN_DIR_PREFIX, MODEL_RUN_OUTPUT_DIR
from src.sync.clients.file_system_client import FileSystemClient
from sync.file_properties import FileProperties

log = logging.getLogger(__name__)


class FileSystemComparer(object):
    """
    Compare the list of directories from the data path on the file system with a list of model and detects changes

    On perform_analysis the following are populated:
        new_directories - with FileProperties for models that needs to be copied
        deleted_directories  - with directory names which need deleting
        changed_directories - with FileProperties of directories which need their permissions updating
    """

    def __init__(
            self,
            config,
            file_system_client=None):
        """
        Constructor
        :param config: configuration for file system comparer
        :param file_system_client: the file system client
        :return:
        """
        self._config = config
        self._config.set_section(CONFIG_DATA_SECTION)
        self.data_path = self._config.get(CONFIG_DATA_PATH)
        if file_system_client is not None:
            self._file_system_client = file_system_client
        else:
            self._file_system_client = FileSystemClient(self._config)
        self.new_directories = None
        self.deleted_directories = None
        self.changed_directories = None

    def perform_analysis(self, model_properties):
        """
        Perform the analysis of the file system compared to the model properties
        :param model_properties: model properties expected to appear
        :return: nothing but set internal properties for new, changed and deleted files
        """
        self.new_directories = []
        self.deleted_directories = []
        self.changed_directories = []

        existing_run_ids = set()
        existing_directories = self._file_system_client.list_dirs(self.data_path)
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
            current_file_properties = self._file_system_client.get_file_properties(file_properties_to_set.file_path)
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

        dir_name = "{}{}".format(MODEL_RUN_DIR_PREFIX, model_run_id)
        return os.path.join(self.data_path, dir_name, MODEL_RUN_OUTPUT_DIR)
