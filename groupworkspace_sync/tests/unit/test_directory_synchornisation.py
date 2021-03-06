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
from mock import Mock
from hamcrest import *
import unittest
from sync.clients.apache_client import ApacheClient, ApacheClientError
from sync.clients.file_system_client import FileSystemClient, FileSystemClientError
from sync.directory_synchroniser import DirectorySynchroniser
from sync.file_properties import FileProperties
from tests.test_mother import ConfigMother
from sync.file_system_comparer import FileSystemComparer


class TestDirectorySynchronisation(unittest.TestCase):

    def setup_mocks(self, directory_contents_on_apache, reg_ex_to_ignore=""):
        self.contents = directory_contents_on_apache

        self.mock_apache_client = Mock(ApacheClient)
        self.mock_apache_client.get_contents = self._find_contents

        self.mock_file_handle = Mock()
        self.mock_file_system_client = Mock(FileSystemClient)
        self.mock_file_system_client.create_file = Mock(return_value=self.mock_file_handle)
        self.mock_file_system_client.create_dir = Mock(return_value=True)

        config = ConfigMother.test_configuration_with_values(reg_ex_to_ignore=reg_ex_to_ignore)
        self.files_synchronisation = DirectorySynchroniser(config, self.mock_apache_client, self.mock_file_system_client)

    def _find_contents(self, directory):
        return self.contents[directory]

    def test_GIVEN_no_files_in_directory_WHEN_copy_new_THEN_directory_created_and_permissions_set(self):

        model_run_path = "data/run1"
        self.setup_mocks({model_run_path: []})
        new_directories = [FileProperties(model_run_path, "owner", False, False)]

        copied_count = self.files_synchronisation.copy_new(new_directories)

        assert_that(self.mock_file_system_client.create_dir.called, is_(True), "Directory was created")
        self.mock_file_system_client.create_dir.assert_called_with(model_run_path)
        assert_that(self.mock_file_system_client.set_permissions.called, is_(True), "Permissions called")
        self.mock_file_system_client.set_permissions.assert_called_with(new_directories[0])
        assert_that(copied_count, is_(1), "copied_count")

    def assert_file_downloaded(self, expected_file_name):
        assert_that(self.mock_file_system_client.create_file.called, is_(True), "File was opened")
        self.mock_file_system_client.create_file.assert_called_with(expected_file_name)
        assert_that(self.mock_apache_client.download_file.called, is_(True), "Download called")
        self.mock_apache_client.download_file.assert_called_with(expected_file_name, self.mock_file_handle)

    def test_GIVEN_file_in_directory_WHEN_copy_new_THEN_directory_created_and_permissions_set(self):
        model_run_dir = "data/run1"
        self.new_directories = [FileProperties(model_run_dir, "owner", False, False)]
        expected_file = "data.nc"
        self.setup_mocks({model_run_dir: [expected_file]})
        expected_file_name = "{}/{}".format(model_run_dir, expected_file)

        copied_count = self.files_synchronisation.copy_new(self.new_directories)

        self.assert_file_downloaded(expected_file_name)
        assert_that(copied_count, is_(2), "copied_count")

    def test_GIVEN_files_in_directory_some_not_nc_or_ncml_WHEN_copy_new_THEN_only_nc_and_ncml_files_copied(self):
        model_run_dir = "data/run1"
        self.new_directories = [FileProperties(model_run_dir, "owner", False, False)]
        expected_files = ["data.nc",                "copy.ncml"]
        self.setup_mocks({model_run_dir: ["data.nc", "not to copy", "copy.ncml", "nottocopy.hi"]})
        expected_file_names = ["{}/{}".format(self.new_directories[0].file_path, expected_file) for expected_file in expected_files]

        copied_count = self.files_synchronisation.copy_new(self.new_directories)

        assert_that(self.mock_file_system_client.create_file.called, is_(True), "File was opened")
        call_list = self.mock_file_system_client.create_file.call_args_list
        assert_that(call_list[0][0][0], is_(expected_file_names[0]))
        assert_that(call_list[1][0][0], is_(expected_file_names[1]))
        assert_that(self.mock_apache_client.download_file.called, is_(True), "Permissions called")
        call_args = [x[0] for x in self.mock_apache_client.download_file.call_args_list]
        assert_that(call_args[0], is_((expected_file_names[0], self.mock_file_handle)))
        assert_that(call_args[1], is_((expected_file_names[1], self.mock_file_handle)))

        assert_that(copied_count, is_(3), "copied_count")

    def test_GIVEN_directory_in_directory_WHEN_copy_new_THEN_directory_created(self):
        model_run_dir = "data/run1"
        self.new_directories = [FileProperties(model_run_dir, "owner", False, False)]
        expected_dir = "subdir"
        expected_dir_name = "{}/{}".format(model_run_dir, expected_dir)
        self.setup_mocks({model_run_dir: [expected_dir + '/'],
                          expected_dir_name: []})

        copied_count = self.files_synchronisation.copy_new(self.new_directories)

        assert_that(self.mock_file_system_client.create_dir.call_count, is_(2), "Parent and sub directory created count")
        self.mock_file_system_client.create_dir.assert_called_with(expected_dir_name)
        assert_that(copied_count, is_(2), "copied_count")

    def test_GIVEN_file_in_sub_directory_WHEN_copy_new_THEN_directory_created_and_file_copied(self):
        model_run_dir = "data/run1"
        self.new_directories = [FileProperties(model_run_dir, "owner", False, False)]
        expected_dir = "subdir"
        expected_dir_name = "{}/{}".format(model_run_dir, expected_dir)
        expected_filename = "my_file.nc"
        expected_file_path = "{}/{}".format(expected_dir_name, expected_filename)
        self.setup_mocks({model_run_dir: [expected_dir + '/'],
                          expected_dir_name: [expected_filename]})

        copied_count = self.files_synchronisation.copy_new(self.new_directories)

        assert_that(self.mock_file_system_client.create_dir.call_count, is_(2), "Parent and sub directory created count")
        self.mock_file_system_client.create_dir.assert_called_with(expected_dir_name)

        self.assert_file_downloaded(expected_file_path)
        assert_that(copied_count, is_(3), "copied_count")

    def test_GIVEN_apache_client_throws_error_WHEN_copy_new_THEN_next_directory_look_at(self):

        model_run_path = "data/run1"
        self.setup_mocks({model_run_path: []})
        new_directories = [FileProperties(model_run_path, "owner", False, False),
                           FileProperties(model_run_path, "owner", False, False)]
        self.mock_apache_client.get_contents = Mock(side_effect=ApacheClientError("Error"))

        copied_count = self.files_synchronisation.copy_new(new_directories)

        assert_that(self.mock_file_system_client.create_dir.called, is_(True), "Directory was created")
        self.mock_file_system_client.create_dir.assert_called_with(model_run_path)
        assert_that(self.mock_file_system_client.set_permissions.called, is_(True), "Permissions called")
        self.mock_file_system_client.set_permissions.assert_called_with(new_directories[0])
        assert_that(copied_count, is_(2), "copied_count")

    def test_GIVEN_create_directory_throws_error_WHEN_copy_new_THEN_next_directory_look_at(self):

        model_run_path = "data/run1"
        self.setup_mocks({model_run_path: []})
        new_directories = [FileProperties(model_run_path, "owner", False, False),
                           FileProperties(model_run_path, "owner", False, False)]
        self.mock_file_system_client.create_dir = Mock(side_effect=FileSystemClientError("Error"))

        copied_count = self.files_synchronisation.copy_new(new_directories)

        assert_that(self.mock_file_system_client.create_dir.call_count, is_(2), "Directory was created count")
        assert_that(self.mock_file_system_client.set_permissions.call_count, is_(0), "Set permissions is not called")
        assert_that(copied_count, is_(0), "copied_count")

    def test_GIVEN_create_file_throws_error_WHEN_copy_new_THEN_next_file_look_at(self):

        model_run_path = "data/run1"
        self.setup_mocks({model_run_path: ["file1.ncml", "file2.nc"]})
        new_directories = [FileProperties(model_run_path, "owner", False, False)]
        self.mock_file_system_client.create_file = Mock(side_effect=FileSystemClientError("Error"))

        copied_count = self.files_synchronisation.copy_new(new_directories)

        assert_that(self.mock_file_system_client.create_file.call_count, is_(2), "File opened")
        assert_that(copied_count, is_(1), "copied_count")

    def test_GIVEN_file_exists_already_WHEN_copy_new_THEN_file_is_not_copied(self):

        model_run_path = "data/run1"
        self.setup_mocks({model_run_path: ["file1.ncml", "file2.nc"]})
        new_directories = [FileProperties(model_run_path, "owner", False, False)]
        self.mock_file_system_client.create_file = Mock(return_value=None)

        copied_count = self.files_synchronisation.copy_new(new_directories)

        assert_that(self.mock_file_system_client.create_file.call_count, is_(2), "File opened")
        assert_that(self.mock_apache_client.download_file.call_count, is_(0), "File downloaded")
        assert_that(copied_count, is_(1), "copied_count")

    def test_GIVEN_download_file_throws_error_WHEN_copy_new_THEN_next_file_look_at(self):

        model_run_path = "data/run1"
        self.setup_mocks({model_run_path: ["file1.ncml", "file2.nc"]})
        new_directories = [FileProperties(model_run_path, "owner", False, False)]
        self.mock_apache_client.download_file = Mock(side_effect=ApacheClientError("Error"))

        copied_count = self.files_synchronisation.copy_new(new_directories)

        assert_that(self.mock_apache_client.download_file.call_count, is_(2), "File download start")
        assert_that(self.mock_file_system_client.close_and_delete_file.call_count, is_(2), "File is deleted when download fails")
        assert_that(copied_count, is_(1), "copied_count")

    def test_GIVEN_folder_WHEN_update_permissions_THEN_permissions_updated(self):
        model_run_path = "data/run1"
        self.setup_mocks({})
        changed_directories = [FileProperties(model_run_path, "owner", False, False),
                               FileProperties(model_run_path, "owner", False, False)]

        updated_count = self.files_synchronisation.update_permissions(changed_directories)

        assert_that(self.mock_file_system_client.set_permissions.call_count, is_(2), "Permissions set on directories count")
        assert_that(updated_count, is_(2), "updated count")

    def test_GIVEN_folder_WHEN_update_permissions_THEN_permissions_updated(self):
        model_run_path = "data/run1"
        self.setup_mocks({})
        changed_directories = [FileProperties(model_run_path, "owner", False, False),
                               FileProperties(model_run_path, "owner", False, False)]

        updated_count = self.files_synchronisation.update_permissions(changed_directories)

        assert_that(self.mock_file_system_client.set_permissions.call_count, is_(2), "Permissions set on directories count")
        assert_that(updated_count, is_(2), "updated count")

    def test_GIVEN_update_permissions_throws_WHEN_update_permissions_THEN_next_directory_looked_at(self):
        model_run_path = "data/run1"
        self.setup_mocks({})
        self.mock_file_system_client.set_permissions = Mock(side_effect=FileSystemClientError("Error"))
        changed_directories = [FileProperties(model_run_path, "owner", False, False),
                               FileProperties(model_run_path, "owner", False, False)]

        updated_count = self.files_synchronisation.update_permissions(changed_directories)

        assert_that(self.mock_file_system_client.set_permissions.call_count, is_(2), "Permissions set on directories count")
        assert_that(updated_count, is_(0), "updated count")

    def test_GIVEN_folders_WHEN_delete_THEN_folders_deleted(self):
        model_run_path = "data/run1"
        self.setup_mocks({})
        deleted_directories = [FileProperties(model_run_path, "owner", False, False),
                               FileProperties(model_run_path, "owner", False, False)]

        deleted_count = self.files_synchronisation.delete(deleted_directories)

        assert_that(self.mock_file_system_client.delete_directory.call_count, is_(2), "Delete call count")
        assert_that(deleted_count, is_(2), "deleted count")

    def test_GIVEN_exception_thrown_on_delete_WHEN_delete_THEN_next_folder_deleted(self):
        model_run_path = "data/run1"
        self.setup_mocks({})
        self.mock_file_system_client.delete_directory = Mock(side_effect=FileSystemClientError("Error"))
        deleted_directories = [FileProperties(model_run_path, "owner", False, False),
                               FileProperties(model_run_path, "owner", False, False)]

        deleted_count = self.files_synchronisation.delete(deleted_directories)

        assert_that(self.mock_file_system_client.delete_directory.call_count, is_(2), "Delete call count")
        assert_that(deleted_count, is_(0), "deleted count")

    def test_GIVEN_one_change_new_and_delete_WHEN_sync_all_THEN_all_files_synched(self):
        model_run_path_to_copy = "data/run1"
        model_run_path_to_delete = "data/run2"
        model_run_path_to_update = "data/run3"
        model_run_path_to_resync = "data/run4"
        filename = "blah.nc"
        self.setup_mocks({model_run_path_to_copy: [],
                          model_run_path_to_resync: [filename]})
        file_sync = Mock(FileSystemComparer)
        file_sync.deleted_directories = [model_run_path_to_delete]
        file_sync.new_directories = [FileProperties(model_run_path_to_copy, "owner", False, False)]
        file_sync.changed_directories = [FileProperties(model_run_path_to_update, "owner", False, False)]
        file_sync.existing_non_deleted_directories = [FileProperties(model_run_path_to_resync, "owner", False, False)]
        self.mock_file_system_client.create_file = Mock(return_value=self.mock_file_handle)

        new_count, updated_count, deleted_count = self.files_synchronisation.synchronise_all(file_sync)

        assert_that(self.mock_file_system_client.create_dir.call_args_list[0][0][0], is_(model_run_path_to_copy))
        assert_that(self.mock_file_system_client.create_dir.call_args_list[1][0][0], is_(model_run_path_to_resync))
        self.mock_file_system_client.create_file.assert_called_with(model_run_path_to_resync + '/' + filename)
        self.mock_file_system_client.set_permissions.assert_called_with(file_sync.changed_directories[0])
        self.mock_file_system_client.delete_directory.assert_called_with(model_run_path_to_delete)

        assert_that(new_count, is_(3), "updated count (plus one for erant existing update)")
        assert_that(updated_count, is_(1), "updated count")
        assert_that(deleted_count, is_(1), "deleted count")

    def test_GIVEN_directory_matches_reg_ex_to_ignore_WHEN_copy_new_THEN_directory_not_created(self):
        reg_ex_to_ignore = "run(\d)+/data/"
        model_run_dir = "data/run13"
        self.new_directories = [FileProperties(model_run_dir, "owner", False, False)]
        expected_dir = "data"
        expected_dir_name = "{}/{}".format(model_run_dir, expected_dir)
        self.setup_mocks({model_run_dir: [expected_dir + '/'],
                          expected_dir_name: []},
                         reg_ex_to_ignore)

        copied_count = self.files_synchronisation.copy_new(self.new_directories)

        assert_that(self.mock_file_system_client.create_dir.call_count, is_(1), "Just parent created count")
        self.mock_file_system_client.create_dir.assert_called_with(model_run_dir)
        assert_that(copied_count, is_(1), "copied_count")

    def test_GIVEN_file_matches_reg_ex_to_ignore_WHEN_copy_new_THEN_directory_not_created(self):
        reg_ex_to_ignore = "run(\d)+/data/ output/.*\.dump\..*.nc"
        model_run_dir = "data/run13"
        self.new_directories = [FileProperties(model_run_dir, "owner", False, False)]
        expected_dir = "output"
        expected_dir_name = "{}/{}".format(model_run_dir, expected_dir)
        filename = "majic.dump.spin1.196701.nc"
        self.setup_mocks({model_run_dir: [expected_dir + '/'],
                          expected_dir_name: [filename]},
                         reg_ex_to_ignore)

        copied_count = self.files_synchronisation.copy_new(self.new_directories)

        assert_that(self.mock_file_system_client.create_dir.call_count, is_(2), "Copy parent and sub")
        assert_that(self.mock_file_system_client.create_file.call_count, is_(0), "create file (not called because ignored)")
        assert_that(copied_count, is_(2), "copied_count")

    def test_GIVEN_new_file_in_directory_WHEN_copy_new_THEN_directory_not_created_permissions_set_as_writable_and_then_set_back(self):
        # the directory must become writable to the process so that the process can update the directory if needed
        model_run_path = "data/run1"
        self.setup_mocks({model_run_path: []})
        new_directories = [FileProperties(model_run_path, "owner", False, False)]

        copied_count = self.files_synchronisation.copy_new(new_directories)

        assert_that(self.mock_file_system_client.create_dir.called, is_(True), "Directory was created")
        self.mock_file_system_client.create_dir.assert_called_with(model_run_path)
        assert_that(self.mock_file_system_client.set_permissions.called, is_(True), "Permissions called")
        self.mock_file_system_client.set_permissions.assert_called_with(new_directories[0])
        assert_that(copied_count, is_(1), "copied_count")