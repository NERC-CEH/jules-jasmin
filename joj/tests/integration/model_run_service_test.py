# header

from mock import MagicMock, ANY

from joj.services.tests.base import BaseTest
from hamcrest import *
from joj.model import User
from services.model_run_service import ModelRunService
from joj.tests import TestController


class ModelRunServiceTest(TestController):

    def setUp(self):

        super(ModelRunServiceTest, self).setUp()
        self.model_run_service = ModelRunService()

    def test_GIVEN_no_model_runs_WHEN_get_model_list_THEN_empty_list_returned(self):

        models = self.model_run_service.get_code_versions()

        assert_that(len(models), is_not(0), "There should be at least one code version on the list")
        assert_that([x.name for x in models], contains("Jules v3.4.1"), "The list of code versions")
