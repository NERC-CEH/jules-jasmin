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
from stat import S_IRUSR, S_IWUSR, S_IRGRP, S_IROTH
from hamcrest import *
import unittest
import os
import getpass
from sync.clients.file_system_client import FileSystemClient, FileSystemClientError
from sync.file_properties import FileProperties
from tests.test_mother import ConfigMother
import shutil


class TestFileSystemClient(unittest.TestCase):

    def setUp(self):
        self.root_dir = "/tmp/majic_test"  # same as in delete_dir_test.sh
        try:
            os.mkdir(self.root_dir)
        except OSError as ex:
            if ex.errno != 17:
                raise ex
            else:
                self.tearDown()
                os.mkdir(self.root_dir)
        self.filename = os.path.join(self.root_dir, "test_file")
        f = open(self.filename, 'w')
        f.write("testing")
        f.close()
        config = ConfigMother.test_configuration_with_values(file_root_path=self.root_dir)
        self.file_system_client = FileSystemClient(config)

    def tearDown(self):
        try:
            shutil.rmtree(self.root_dir)
        except OSError as e:
            if e.errno != 2:  # file doesn't exist
                raise e

    def test_GIVEN_file_WHEN_from_path_THEN_properties_set(self):
        props = self.file_system_client.get_file_properties(self.filename)

        assert_that(props.file_path, is_(self.filename), "file path")
        assert_that(props.owner, is_(getpass.getuser()), "file path")

    def test_GIVEN_file_is_group_read_WHEN_from_path_THEN_properties_is_published_butnot_public(self):
        os.chmod(self.filename,  S_IRUSR | S_IWUSR | S_IRGRP)

        props = self.file_system_client.get_file_properties(self.filename)

        assert_that(props.is_published, is_(True), "published")
        assert_that(props.is_public, is_(False), "public")

    def test_GIVEN_file_is_other_read_WHEN_from_path_THEN_properties_is_not_published_but_is_public(self):
        # this is a funny situation to be in
        os.chmod(self.filename,  S_IRUSR | S_IWUSR | S_IROTH)

        props = self.file_system_client.get_file_properties(self.filename)

        assert_that(props.is_published, is_(False), "published")
        assert_that(props.is_public, is_(True), "public")

    def test_GIVEN_file_is_group_read_and_other_read_WHEN_from_path_THEN_properties_is_published_and_is_public(self):
        os.chmod(self.filename,  S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH)

        props = self.file_system_client.get_file_properties(self.filename)

        assert_that(props.is_published, is_(True), "published")
        assert_that(props.is_public, is_(True), "public")

    def test_GIVEN_file_is_not_read_WHEN_from_path_THEN_properties_is_not_published_but_is_not_public(self):
        os.chmod(self.filename,  S_IRUSR | S_IWUSR)

        props = self.file_system_client.get_file_properties(self.filename)

        assert_that(props.is_published, is_(False), "published")
        assert_that(props.is_public, is_(False), "public")

    def test_GIVEN_dir_WHEN_create_directory_created(self):
        file_path = "tmp"

        self.file_system_client.create_dir(file_path)

        assert_that(os.path.isdir(os.path.join(self.root_dir, file_path)), "Path is not directory or doesn't exist")

    def test_GIVEN_dir_in_non_existant_dir_WHEN_create_THEN_directory_tree_created(self):
        file_path = "tmp/sub/sub/end"

        self.file_system_client.create_dir(file_path)

        assert_that(os.path.isdir(os.path.join(self.root_dir, file_path)), "Path is not directory or doesn't exist")

    def test_GIVEN_dir_already_exists_WHEN_create_directory_created(self):
        file_path = "tmp"
        self.file_system_client.create_dir(file_path)

        self.file_system_client.create_dir(file_path)

        assert_that(os.path.isdir(os.path.join(self.root_dir, file_path)), "Path still exists")

    def test_GIVEN_any_other_error_WHEN_create_THEN_exception_thrown_as_apache_file_error(self):
        self.file_system_client._filesystem_root_for_app = "/data"

        assert_that(calling(self.file_system_client.create_dir).with_args("1"),
                    raises(FileSystemClientError))

    def test_GIVEN_dir_referenced_dir_outside_of_root_WHEN_create_directory_THEN_exception(self):
        file_path = "../john"

        assert_that(calling(self.file_system_client.create_dir).with_args(file_path),
                    raises(Exception, "Code is trying to access a directory outside root"))

    def test_GIVEN_file_WHEN_create_THEN_file_created(self):
        file_path = "tmp"

        fileobj = self.file_system_client.create_file(file_path)
        fileobj.write("hi")

        assert_that(os.path.isfile(os.path.join(self.root_dir, file_path)), "Path is not a file or doesn't exist")

    def test_GIVEN_file_exists_WHEN_create_THEN_non_returned(self):
        file_path = self.filename

        fileobj = self.file_system_client.create_file(file_path)

        assert_that(fileobj, none(), "File object is none")

    def test_GIVEN_any_error_thrown_WHEN_create_THEN_FileSystemClientError(self):
        file_path = "doesntexists/file.txt"

        assert_that(calling(self.file_system_client.create_file).with_args(file_path),
                    raises(FileSystemClientError))

    def test_GIVEN_file_WHEN_close_THEN_file_closed(self):
        file_path = "tmp"
        fileobj = self.file_system_client.create_file(file_path)

        self.file_system_client.close_file(fileobj)

        assert_that(fileobj.closed, "File is not closed")

    def test_GIVEN_exception_WHEN_close_THEN_FileSystemClientError(self):

        assert_that(calling(self.file_system_client.close_file).with_args(None),
                    raises(FileSystemClientError))

    def test_GIVEN_file_WHEN_close_and_delete_THEN_file_deleted(self):
        file_path = "tmp"
        fileobj = self.file_system_client.create_file(file_path)
        fileobj.write("hi")

        self.file_system_client.close_and_delete_file(fileobj)

        assert_that(os.path.isfile(os.path.join(self.root_dir, file_path)), is_(False), "Path exists")

    def test_GIVEN_dir_with_file_WHEN_delete_directory_THEN_directory_deleted(self):
        file_path = "run1"
        subdir = "blah"
        self.file_system_client.create_dir(file_path)
        sub_dir_path = os.path.join(file_path, subdir)
        self.file_system_client.create_dir(sub_dir_path)
        f = self.file_system_client.create_file(os.path.join(sub_dir_path, "file"))
        f.write("hi there")
        self.file_system_client.close_file(f)

        self.file_system_client.delete_directory(file_path)

        assert_that(os.path.exists(os.path.join(self.root_dir, file_path)), is_(False), "Path still exists")

    def test_GIVEN_error_WHEN_delete_directory_THEN_exception(self):
        file_path = ""

        assert_that(calling(self.file_system_client.delete_directory).with_args(file_path),
                    raises(FileSystemClientError))

    def create_file_and_sub_dir(self):
        self.model_run_path = "run1"
        subdir = "blah"
        self.file_system_client.create_dir(self.model_run_path)
        sub_dir_path = os.path.join(self.model_run_path, subdir)
        self.file_system_client.create_dir(sub_dir_path)
        file_path = os.path.join(sub_dir_path, "file")
        f = self.file_system_client.create_file(file_path)
        f.write("hi there")
        self.file_system_client.close_file(f)

        return file_path

    def test_GIVEN_dir_WHEN_set_permissions_FF_THEN_premissions_set(self):
        file_path = self.create_file_and_sub_dir()
        file_property = FileProperties(file_path, getpass.getuser(), False, False)

        self.file_system_client.set_permissions(file_property)

        assert_that(self.file_system_client.get_file_properties(file_path), is_(file_property), "File properties")

    def test_GIVEN_dir_WHEN_set_permissions_FT_THEN_premissions_set(self):
        file_path = self.create_file_and_sub_dir()
        file_property = FileProperties(file_path, getpass.getuser(), False, True)

        self.file_system_client.set_permissions(file_property)

        assert_that(self.file_system_client.get_file_properties(file_path), is_(file_property), "File properties")

    def test_GIVEN_dir_WHEN_set_permissions_TF_THEN_premissions_set(self):
        file_path = self.create_file_and_sub_dir()
        file_property = FileProperties(file_path, getpass.getuser(), True, False)

        self.file_system_client.set_permissions(file_property)

        assert_that(self.file_system_client.get_file_properties(file_path), is_(file_property), "File properties")

    def test_GIVEN_dir_WHEN_set_permissions_TT_THEN_premissions_set(self):
        file_path = self.create_file_and_sub_dir()
        file_property = FileProperties(file_path, "root", True, True)

        self.file_system_client.set_permissions(file_property)

        assert_that(self.file_system_client.get_file_properties(file_path), is_(file_property), "File properties")

    def test_GIVEN_dir_WHEN_list_THEN_directories_returned(self):
        file_path = self.create_file_and_sub_dir()

        dirs = self.file_system_client.list_dirs("")

        assert_that(dirs, contains(self.model_run_path), "Directories")
