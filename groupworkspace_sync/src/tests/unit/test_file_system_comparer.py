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
import os
from sync.file_system_comparer import FileSystemComparer, FileProperties
from sync.utils.config_accessor import ConfigAccessor
from sync.utils.constants import JSON_MODEL_RUN_ID, CONFIG_DATA_PATH, JSON_IS_PUBLISHED, JSON_USER_NAME, JSON_IS_PUBLIC
from tests.test_mother import ConfigMother


def assert_arrays_the_same(directory_list, expected_directory_list, message):
    if expected_directory_list is None:
        assert_that(directory_list, has_length(0), message)
    else:
        assert_that(directory_list, has_length(len(expected_directory_list)), message)
        assert_that(directory_list, contains_inanyorder(*expected_directory_list), message)


def assert_that_file_system_comparer(file_system_comparer, expected_new_dirs=None, expected_changed_dirs=[], expected_deleted_dirs=[]):
    assert_arrays_the_same(file_system_comparer.new_directories, expected_new_dirs, "new directories")
    assert_arrays_the_same(file_system_comparer.deleted_directories, expected_deleted_dirs, "deleted directories")
    if expected_changed_dirs is None:
        assert_that(file_system_comparer.changed_directories, has_length(0), "changed directories")
    else:
        assert_that(file_system_comparer.changed_directories, has_length(len(expected_changed_dirs)), "changed directories")
        for directory in file_system_comparer.changed_directories:
            found = False
            for expected_dir in expected_changed_dirs:
                if expected_dir.file_path == directory.file_path:
                    assert_that(directory.owner, is_(expected_dir.owner), "model_owner for {}".format(directory.file_path))
                    assert_that(directory.is_published, is_(expected_dir.is_published), "is published for {}".format(directory.file_path))
                    assert_that(directory.is_public, is_(expected_dir.is_public), "is_public for {}".format(directory.file_path))
                    found = True
            assert_that(found, is_(True), "Can not find {} in expected list {}".format(directory, expected_changed_dirs))


class TestFileSystemComparer(unittest.TestCase):

    def setUp(self):
        self.expected_path = "path"
        self.config = ConfigMother.set_data_path_config(self.expected_path)
        self.mock_file_stats = {}
        self.model_owner = "model_owner"

    def get_file_properties_mock(self, file_path):
            return self.mock_file_stats[file_path]

    def create_filelist_and_mock_file_stats(self, runids):
        filelist = ["run{}".format(runid) for runid in runids]
        for file in filelist:
            file_path = os.path.join(self.expected_path, file)
            self.mock_file_stats[file_path] = FileProperties(file_path, self.model_owner, False, False)
        return filelist

    def test_GIVEN_one_extra_entry_on_model_list_WHEN_compare_THEN_extra_entry_is_in_new_dirs_list(self):

        runid = 12
        expected_new_dir = "{}/run{}".format(self.expected_path, runid)
        filelist = self.create_filelist_and_mock_file_stats([])
        model_properties = self.create_model_run_properties([runid])

        file_system_comparer = FileSystemComparer(self.config, filelist, model_properties, self.get_file_properties_mock)

        assert_that_file_system_comparer(file_system_comparer, expected_new_dirs=[expected_new_dir, ])

    def test_GIVEN_two_extra_models_WHEN_compare_THEN_models_appear_on_new_dirs_list(self):

        runids = [100, 12]
        expected_new_dirs = ["{}/run{}".format(self.expected_path, runid) for runid in runids]
        filelist = self.create_filelist_and_mock_file_stats([])
        model_properties = self.create_model_run_properties(runids)

        file_system_comparer = FileSystemComparer(self.config, filelist, model_properties, self.get_file_properties_mock)

        assert_that_file_system_comparer(file_system_comparer, expected_new_dirs=expected_new_dirs)

    def create_model_run_properties(self, runids, owner=None, published=False, public=False):
        owner_to_use = owner
        if owner is None:
            owner_to_use = self.model_owner
        return [{JSON_MODEL_RUN_ID: runid,
                 JSON_USER_NAME: owner_to_use,
                 JSON_IS_PUBLISHED: published,
                 JSON_IS_PUBLIC: public} for runid in runids]

    def test_GIVEN_entries_in_file_list_same_as_model_list_WHEN_compare_THEN_no_extra_entires(self):

        runids = [100, 12]
        expected_new_dirs = []
        filelist = self.create_filelist_and_mock_file_stats(runids)
        model_properties = self.create_model_run_properties(runids)

        file_system_comparer = FileSystemComparer(self.config, filelist, model_properties, self.get_file_properties_mock)

        assert_that_file_system_comparer(file_system_comparer, expected_new_dirs=expected_new_dirs)

    def test_GIVEN_one_extra_entry_on_file_list_WHEN_compare_THEN_extra_entry_on_del_list(self):

        runids = [1, 10]
        filelist = self.create_filelist_and_mock_file_stats(runids)
        expected_deleted_dirs = ["{}/run{}".format(self.expected_path, runid) for runid in runids]
        model_properties = []

        file_system_comparer = FileSystemComparer(self.config, filelist, model_properties, self.get_file_properties_mock)

        assert_that_file_system_comparer(file_system_comparer, expected_deleted_dirs=expected_deleted_dirs)

    def test_GIVEN_non_run_directory_WHEN_compare_THEN_no_directories_deleted(self):

        filelist = ["blah"]
        model_properties = []

        file_system_comparer = FileSystemComparer(self.config, filelist, model_properties, self.get_file_properties_mock)
        assert_that_file_system_comparer(file_system_comparer)

    def test_GIVEN_existing_file_owned_by_someone_else_WHEN_compare_THEN_directory_is_set_for_change(self):

        runids = [23]
        expected_owner = "different_username"
        model_properties = self.create_model_run_properties(runids, owner=expected_owner)
        filelist = self.create_filelist_and_mock_file_stats(runids)
        expected_changed_dirs = [FileProperties("{}/{}".format(self.expected_path, file), expected_owner, False, False) for file in filelist]

        file_system_comparer = FileSystemComparer(self.config, filelist, model_properties, self.get_file_properties_mock)

        assert_that_file_system_comparer(file_system_comparer, expected_changed_dirs=expected_changed_dirs)

    def test_GIVEN_existing_file_is_not_published_and_model_is_WHEN_compare_THEN_directory_is_set_for_change(self):

        runids = [23]
        model_properties = self.create_model_run_properties(runids, published=True)
        filelist = self.create_filelist_and_mock_file_stats(runids)
        for mock_file_stat in self.mock_file_stats.values():
            mock_file_stat.is_published = False
        expected_changed_dirs = [FileProperties("{}/{}".format(self.expected_path, file), self.model_owner, True, False) for file in filelist]

        file_system_comparer = FileSystemComparer(self.config, filelist, model_properties, self.get_file_properties_mock)

        assert_that_file_system_comparer(file_system_comparer, expected_changed_dirs=expected_changed_dirs)

    def test_GIVEN_existing_file_is_not_publc_and_model_is_WHEN_compare_THEN_directory_is_set_for_change(self):

        runids = [23]
        model_properties = self.create_model_run_properties(runids, public=True)
        filelist = self.create_filelist_and_mock_file_stats(runids)
        for mock_file_stat in self.mock_file_stats.values():
            mock_file_stat.is_published = False
        expected_changed_dirs = [FileProperties("{}/{}".format(self.expected_path, file), self.model_owner, False, True) for file in filelist]

        file_system_comparer = FileSystemComparer(self.config, filelist, model_properties, self.get_file_properties_mock)

        assert_that_file_system_comparer(file_system_comparer, expected_changed_dirs=expected_changed_dirs)


if __name__ == '__main__':
    unittest.main()
