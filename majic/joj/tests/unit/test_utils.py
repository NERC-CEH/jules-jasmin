"""
header
"""
from hamcrest import is_, assert_that
from joj.services.tests.base import BaseTest
from joj.utils.utils import insert_before_file_extension


class TestUtils(BaseTest):

    def test_insert_before_file_extension(self):
        path = "/home/user/data/file.name.here.nc"
        string_to_insert = "_INSERTED_STRING"
        modified_path = insert_before_file_extension(path, string_to_insert)
        expected_result = "/home/user/data/file.name.here_INSERTED_STRING.nc"
        assert_that(modified_path, is_(expected_result))
