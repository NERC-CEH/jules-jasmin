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
import re
import os
from src.sync.utils.constants import CONFIG_DATA_SECTION, JSON_MODEL_RUN_ID, CONFIG_DATA_PATH


class FileSystemComparer(object):
    """
    Compare the list of directories on the file system with a list of model and detect changes
    """

    def __init__(self, config, existing_directories, model_properties):
        """
        Constructor
        :param config: configuration for file system comparer
        :param existing_directories: list of directories in current directory
        :param model_properties: model properties expected to appear
        :return: nothing but set internal properties for new, changed and deleted files
        """
        self._config = config
        self._config.set_section(CONFIG_DATA_SECTION)
        self.new_directories = []
        self.deleted_directories = []

        existing_run_ids = set()
        for existing_directory in existing_directories:
            match = re.match('run(\d+)', existing_directory)
            if match:
                existing_run_ids.add(int(match.group(1)))

        model_run_ids = set()
        for model_property in model_properties:
            model_run_ids.add(model_property[JSON_MODEL_RUN_ID])

        for model_run_id in model_run_ids.difference(existing_run_ids):
            self.new_directories.append(self._create_model_dir(model_run_id))

        for model_run_id in existing_run_ids.difference(model_run_ids):
            self.deleted_directories.append(self._create_model_dir(model_run_id))

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
