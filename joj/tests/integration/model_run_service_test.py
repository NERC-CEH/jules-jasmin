# header

from mock import MagicMock, ANY
from sqlalchemy.orm.exc import NoResultFound

from joj.services.tests.base import BaseTest
from hamcrest import *
from joj.model import User, session_scope, Session, ModelRun, Dataset, CodeVersion
from services.model_run_service import ModelRunService
from joj.tests import TestController
from pylons import config
from formencode.validators import Invalid


class ModelRunServiceTest(TestController):
    def setUp(self):
        super(ModelRunServiceTest, self).setUp()
        self.model_run_service = ModelRunService()
        self.clean_database()

    def test_GIVEN_no_model_runs_WHEN_get_model_runs_for_user_THEN_empty_list(self):
        # Add a user who doesn't have any model runs
        with session_scope(Session) as session:
            user = User()
            user.name = 'Has No Model Runs'
            session.add(user)
        # Get the users model runs
        model_runs = self.model_run_service.get_models_for_user(user)
        assert_that(model_runs, is_([]))

    def test_GIVEN_non_existent_user_WHEN_get_model_runs_for_user_THEN_returns_empty_list(self):
        user = User()
        user.id = -100
        user.name = "Doesn't Exist"
        model_runs = self.model_run_service.get_models_for_user(user)
        assert_that(model_runs, is_([]))

    def test_GIVEN_user_None_WHEN_get_model_runs_for_user_THEN_throws_AttributeError(self):
        with self.assertRaises(AttributeError, msg="Should have thrown a AttributeError exception"):
            model_runs = self.model_run_service.get_models_for_user(None)

    def test_GIVEN_two_users_with_one_model_each_WHEN_get_model_runs_for_user_THEN_returns_correct_model(self):
        # Add two users and give them each one model run
        with session_scope(Session) as session:
            # First add two users
            user1 = User()
            user1.name = 'user1'
            user2 = User()
            user2.name = 'user2'
            session.add_all([user1, user2])
            session.commit()
            # Give them each a model
            model_run1 = ModelRun()
            model_run1.name = "MR1"
            model_run1.user_id = user1.id
            model_run2 = ModelRun()
            model_run2.name = "MR2"
            model_run2.user_id = user2.id

            session.add_all([model_run1, model_run2])
        # Get the users model runs
        model_runs = self.model_run_service.get_models_for_user(user1)
        assert_that(len(model_runs), is_(1))
        assert_that(model_runs[0].name, is_("MR1"))

    def test_WHEN_get_code_versions_THEN_returns_list_including_default_code_version(self):

        models = self.model_run_service.get_code_versions()

        assert_that(len(models), is_not(0), "There should be at least one code version on the list")
        assert_that([x.name for x in models], has_item(config['default_code_version']), "The list of code versions")

    def test_GIVEN_valid_code_version_id_WHEN_get_code_version_THEN_code_version_returned(self):
        expectedModel = self.model_run_service.get_code_versions()[0]

        model = self.model_run_service.get_code_version_by_id(expectedModel.id)

        assert_that(model.id, is_(expectedModel.id), "Id")
        assert_that(model.name, is_(expectedModel.name), "Name")

    def test_GIVEN_non_existent_code_version_id_WHEN_get_code_version_THEN_throws_NoResultFound_exception(self):
        with self.assertRaises(NoResultFound, msg="Should have thrown a NoResultFound exception"):
            model = self.model_run_service.get_code_version_by_id(-100)

    def test_GIVEN_no_defining_model_run_WHEN_get_defining_model_run_THEN_error_returned(self):
        with self.assertRaises(NoResultFound, msg="Should have thrown a NoResultFound exception"):
            self.model_run_service.get_parameters_for_model_being_created()