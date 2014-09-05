from pylons import config
from hamcrest import *
from joj.tests import *
from joj.services.file_server_client import FileServerClient

EXISTING_FILE = "model_runs/data/WATCH_2D/driving/Wind_WFD/Wind_WFD.ncml"
NON_EXISTING_FILE = "this_doesntexist"


class TestFileServerClient(TestController):

    def setUp(self):
        self.file_server_client = FileServerClient()

    def test_GIVEN_file_exists_WHEN_check_THEN_true(self):
        result = self.file_server_client.file_exists(EXISTING_FILE)

        assert_that(result, is_(True), "file exists in thredds (%s)" % EXISTING_FILE)

    def test_GIVEN_file_does_not_exists_WHEN_check_THEN_false(self):
        result = self.file_server_client.file_exists(NON_EXISTING_FILE)

        assert_that(result, is_(False), "file exists in thredds (%s)" % NON_EXISTING_FILE)