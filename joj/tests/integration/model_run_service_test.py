# header

from mock import MagicMock, ANY

from joj.services.tests.base import BaseTest
from hamcrest import *
from joj.model import User
from services.model_run_service import ModelRunService
from joj.tests import TestController
from pylons import config
from formencode.validators import Invalid

class ModelRunServiceTest(TestController):

    def setUp(self):

        super(ModelRunServiceTest, self).setUp()
        self.model_run_service = ModelRunService()

    def test_GIVEN_no_model_runs_WHEN_get_model_list_THEN_empty_list_returned(self):

        models = self.model_run_service.get_code_versions()

        assert_that(len(models), is_not(0), "There should be at least one code version on the list")
        assert_that([x.name for x in models], has_item(config['default_code_version']), "The list of code versions")

    def test_GIVEN_valid_code_version_id_runs_WHEN_get_code_version_THEN_code_version_returned(self):

        expectedModel = self.model_run_service.get_code_versions()[0]

        model = self.model_run_service.get_code_version_by_id(expectedModel.id)

        assert_that(model.id, is_(expectedModel.id), "Id")
        assert_that(model.name, is_(expectedModel.name), "Name")

    def test_GIVEN_non_existant_code_version_id_runs_WHEN_get_code_version_THEN_code_version_returned(self):

        try:
            model = self.model_run_service.get_code_version_by_id(-100)
        except Invalid:
            return

        assert_that(1, is_(2), "Should have thrown an invalid exception")
