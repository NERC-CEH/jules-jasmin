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

from hamcrest import *
import unittest
from sync.file_system_comparer import FileSystemComparer
from sync.utils.config_accessor import ConfigAccessor
from sync.utils.constants import JSON_MODEL_RUN_ID, CONFIG_DATA_PATH
from tests.test_mother import ConfigMother


def assert_that_file_system_comparer(file_system_comparer, expected_new_dirs=None, expected_changed_dirs=[], expected_deleted_dirs=[]):
    if expected_new_dirs is None:
        assert_that(file_system_comparer.new_directories, has_length(0), "new directories")
    else:
        assert_that(file_system_comparer.new_directories, has_length(len(expected_new_dirs)), "new directories")
        assert_that(file_system_comparer.new_directories, contains_inanyorder(*expected_new_dirs), "new directories")
    if expected_deleted_dirs is None:
        assert_that(file_system_comparer.deleted_directories, has_length(0), "deleted directories")
    else:
        assert_that(file_system_comparer.deleted_directories, has_length(len(expected_deleted_dirs)), "deleted directories")
        assert_that(file_system_comparer.deleted_directories, contains_inanyorder(*expected_deleted_dirs), "deleted directories")


class TestConfigAccessor(unittest.TestCase):

    def setUp(self):
        self.expected_path = "path"
        self.config = ConfigMother.set_data_path_config(self.expected_path)

    def test_GIVEN_one_extra_entry_on_model_list_WHEN_compare_THEN_extra_entry_is_in_new_dirs_list(self):

        runid = 12
        expected_new_dir = "{}/run{}".format(self.expected_path, runid)
        filelist = []
        model_properties = [{JSON_MODEL_RUN_ID: runid}]

        file_system_comparer = FileSystemComparer(self.config, filelist, model_properties)

        assert_that_file_system_comparer(file_system_comparer, expected_new_dirs=[expected_new_dir, ])

    def test_GIVEN_two_extra_models_WHEN_compare_THEN_models_appear_on_new_dirs_list(self):

        runids = [100, 12]
        expected_new_dirs = ["{}/run{}".format(self.expected_path, runid) for runid in runids]
        filelist = []
        model_properties = [{JSON_MODEL_RUN_ID: runid} for runid in runids]

        file_system_comparer = FileSystemComparer(self.config, filelist, model_properties)

        assert_that_file_system_comparer(file_system_comparer, expected_new_dirs=expected_new_dirs)

    def test_GIVEN_entries_in_file_list_same_as_model_list_WHEN_compare_THEN_no_extra_entires(self):

        runids = [100, 12]
        expected_new_dirs = []
        filelist = ["run{}".format(runid) for runid in runids]
        model_properties = [{JSON_MODEL_RUN_ID: runid} for runid in runids]

        file_system_comparer = FileSystemComparer(self.config, filelist, model_properties)

        assert_that_file_system_comparer(file_system_comparer, expected_new_dirs=expected_new_dirs)

    def test_GIVEN_one_extra_entry_on_file_list_WHEN_compare_THEN_extra_entry_on_del_list(self):

        runids = [1, 10]
        filelist = ["run{}".format(runid) for runid in runids]
        expected_deleted_dirs = ["{}/run{}".format(self.expected_path, runid) for runid in runids]
        model_properties = []

        file_system_comparer = FileSystemComparer(self.config, filelist, model_properties)

        assert_that_file_system_comparer(file_system_comparer, expected_deleted_dirs=expected_deleted_dirs)

    def test_GIVEN_non_run_directory_WHEN_compare_THEN_no_directories_deleted(self):

        filelist = ["blah"]
        model_properties = []

        file_system_comparer = FileSystemComparer(self.config, filelist, model_properties)
        assert_that_file_system_comparer(file_system_comparer)

if __name__ == '__main__':
    unittest.main()
