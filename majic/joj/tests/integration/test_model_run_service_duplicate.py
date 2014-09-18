"""
# header
"""
from datetime import datetime
from mock import Mock
from sqlalchemy.orm.exc import NoResultFound

from hamcrest import *
from joj.model import User, session_scope, Session, ModelRun, ModelRunStatus, Parameter, ParameterValue, Dataset, \
    LandCoverAction, LandCoverRegion
from joj.services.general import ServiceException
from joj.services.model_run_service import ModelRunService
from pylons import config
from joj.utils import constants
from joj.services.job_runner_client import JobRunnerClient
from joj.tests.test_with_create_full_model_run import TestWithFullModelRun


class ModelRunServiceDuplicateTest(TestWithFullModelRun):
    def setUp(self):
        super(ModelRunServiceDuplicateTest, self).setUp()
        self.job_runner_client = JobRunnerClient(config)
        self.model_run_service = ModelRunService(job_runner_client=self.job_runner_client)
        self.clean_database()

    def test_GIVEN_model_doesnot_exist_WHEN_duplicate_THEN_not_found(self):
        # Add a user who doesn't have any model runs
        with session_scope(Session) as session:
            user = User()
            user.name = 'Has No Model Runs'
            session.add(user)

        # Get the users model runs
        with self.assertRaises(NoResultFound, msg="Should have thrown a NoResultFound exception"):
            model_runs = self.model_run_service.duplicate_run_model(10000, user)

    def test_GIVEN_model_belongs_to_someone_else_WHEN_duplicate_THEN_not_found(self):
        # Add a user who doesn't have any model runs
        other_user = self.login("other_user")
        model = self.create_run_model(10, "test", other_user)

        with session_scope(Session) as session:
            user = User()
            user.name = 'Has No Model Runs'
            session.add(user)

        # Get the users model runs
        with self.assertRaises(NoResultFound, msg="Should have thrown a NoResultFound exception"):
            self.model_run_service.duplicate_run_model(model.id, user)

    def test_GIVEN_model_WHEN_duplicate_THEN_model_is_duplicated(self):
        # Add a user who doesn't have any model runs
        user = self.login()
        model = self.create_run_model(10, "test", user)
        model = self.model_run_service.get_model_by_id(user, model.id)
        self.job_runner_client.duplicate = Mock()

        self.model_run_service.duplicate_run_model(model.id, user)

        assert_that(self.job_runner_client.duplicate.called, is_(False), "Job runner not called")
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(user)
        assert_that(model_run.name, is_(model.name + " (Copy)"), "names are the same")
        assert_that(len(model_run.parameter_values), is_(len(model.parameter_values)), "names are the same")
        assert_that(model_run.parameter_values[0].parameter_id, is_(model.parameter_values[0].parameter_id), "first parameter value is for same paramerer")
        assert_that(model_run.parameter_values[0].value, is_(model.parameter_values[0].value), "first parameter value is for same value")

    def test_GIVEN_model_with_land_cover_actions_WHEN_duplicate_THEN_model_is_duplicated(self):
        # Add a user who doesn't have any model runs
        user = self.login()
        model = self.create_run_model(10, "test", user)
        model = self.model_run_service.get_model_by_id(user, model.id)
        with session_scope() as session:
            region1 = LandCoverRegion()
            region2 = LandCoverRegion()
            session.add(region1)
            session.add(region2)
            session.add(LandCoverAction(model_run_id=model.id, order=1, value_id=1, region=region1))
            session.add(LandCoverAction(model_run_id=model.id, order=2, value_id=2, region=region2))
        self.job_runner_client.duplicate = Mock()

        self.model_run_service.duplicate_run_model(model.id, user)

        assert_that(self.job_runner_client.duplicate.called, is_(False), "Job runner not called")
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(user)
        with session_scope() as session:
            regions = session.query(LandCoverAction).filter(LandCoverAction.model_run_id == model_run.id).all()

        assert_that(len(regions), is_(2), "regions")
        assert_that(regions[0].value_id, is_(1), "value id")
        assert_that(regions[0].order, is_(1), "order id")
        assert_that(regions[0].region_id, is_(region1.id), "region id")
        assert_that(regions[1].value_id, is_(2), "value id")
        assert_that(regions[1].order, is_(2), "order id")
        assert_that(regions[1].region_id, is_(region2.id), "region id")

    def test_GIVEN_model_belongs_to_someone_else_and_is_published_WHEN_duplicate_THEN_duplicate_model(self):
        self.job_runner_client.delete = Mock()
        # Add a user who doesn't have any model runs
        other_user = self.login("other_user")
        model = self.create_run_model(10, "test", other_user, constants.MODEL_RUN_STATUS_PUBLISHED)
        user = self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

        self.model_run_service.duplicate_run_model(model.id, user)

        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(user)
        assert_that(model_run.name, is_(model.name), "model name")

    def test_GIVEN_model_WHEN_duplicate_and_name_is_same_as_owner_THEN_model_is_duplicated_name_is_changed(self):

        # Add a user who doesn't have any model runs
        user = self.login()
        model = self.create_run_model(10, "test", user)
        self.create_run_model(10, "test (Copy)", user)
        model = self.model_run_service.get_model_by_id(user, model.id)
        self.job_runner_client.duplicate = Mock()

        self.model_run_service.duplicate_run_model(model.id, user)

        assert_that(self.job_runner_client.duplicate.called, is_(False), "Job runner not called")
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(user)
        assert_that(model_run.name, is_(model.name + " (Copy 2)"), "names are the same")

    def test_GIVEN_model_run_already_being_created_WHEN_duplicate_THEN_model_is_duplicated_and_created_is_overwritten(self):

        # Add a user who doesn't have any model runs
        user = self.login()
        model_being_created = self.create_run_model(10, "test", user, status=constants.MODEL_RUN_STATUS_CREATED)
        model = self.create_run_model(10, "test", user)
        model = self.model_run_service.get_model_by_id(user, model.id)
        self.job_runner_client.duplicate = Mock()
        self.job_runner_client.delete = Mock()

        self.model_run_service.duplicate_run_model(model.id, user)

        assert_that(self.job_runner_client.duplicate.called, is_(False), "Job runner not called")
        model_run = self.model_run_service.get_model_being_created_with_non_default_parameter_values(user)
        assert_that(model_run.name, is_(model.name + " (Copy)"), "names are the same")
        with self.assertRaises(NoResultFound):
            self.model_run_service.get_model_by_id(user, model_being_created.id)

