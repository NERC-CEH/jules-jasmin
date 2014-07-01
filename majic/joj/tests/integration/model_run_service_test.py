# header
from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound

from hamcrest import *
from joj.model import User, session_scope, Session, ModelRun, Parameter, ParameterValue
from joj.services.model_run_service import ModelRunService
from joj.model import User, session_scope, Session, ModelRun, ModelRunStatus
from joj.services.general import ServiceException
from joj.services.model_run_service import ModelRunService
from joj.tests import TestController
from pylons import config
from joj.utils import constants
from joj.model.non_database.spatial_extent import SpatialExtent


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

    def test_GIVEN_user_has_published_model_run_WHEN_get_model_runs_for_user_THEN_published_model_is_returned(self):
        # Add one user and give them a published and unpublished model run
        with session_scope(Session) as session:
            # First add user
            user1 = User()
            user1.name = 'user1'
            session.add(user1)
            session.commit()
            # Give a model
            model_run1 = ModelRun()
            model_run1.name = "MR1"
            model_run1.user_id = user1.id
            model_run1.status = self._status(constants.MODEL_RUN_STATUS_CREATED)
            model_run2 = ModelRun()
            model_run2.name = "MR2"
            model_run2.status = self._status(constants.MODEL_RUN_STATUS_PUBLISHED)
            model_run2.user_id = user1.id
            model_run2.status = self._status(constants.MODEL_RUN_STATUS_COMPLETED)
            session.add_all([model_run1, model_run2])
        # Get the users model runs
        model_runs = self.model_run_service.get_models_for_user(user1)
        assert_that(len(model_runs), is_(2))

    def test_GIVEN_user_has_published_model_run_WHEN_get_published_model_runs_THEN_only_published_model_run_returned(self):
        # Add one user and give them a published and unpublished model run
        with session_scope(Session) as session:
            # First add user
            user1 = User()
            user1.name = 'user1'
            session.add(user1)
            session.commit()
            # Give them each a model
            model_run1 = ModelRun()
            model_run1.name = "MR1"
            model_run1.user_id = user1.id
            model_run2 = ModelRun()
            model_run2.name = "MR2"
            model_run2.status = self._status(constants.MODEL_RUN_STATUS_PUBLISHED)
            model_run2.user_id = user1.id
            session.add_all([model_run1, model_run2])
        # Get the published model runs
        model_runs = self.model_run_service.get_published_models()
        assert_that(len(model_runs), is_(1))
        assert_that(model_runs[0].name, is_("MR2"))

    def test_GIVEN_no_published_runs_WHEN_get_published_model_runs_THEN_empty_list(self):
        model_runs = self.model_run_service.get_published_models()
        assert_that(model_runs, is_([]))

    def test_WHEN_get_user_model_runs_THEN_list_ordered_by_date_created_newest_first(self):
        with session_scope(Session) as session:
            # First add user
            user1 = User()
            user1.name = 'user1'
            session.add(user1)
            session.commit()
            # Create three published models not in datetime order
            model_run1 = ModelRun()
            model_run1.user_id = user1.id
            model_run1.name = "MR1"
            model_run1.date_created = datetime(2013, 12, 7, 17, 15, 30)
            session.add(model_run1)
            session.commit()
            model_run2 = ModelRun()
            model_run2.user_id = user1.id
            model_run2.name = "MR2"
            model_run2.date_created = datetime(2014, 6, 9, 12, 30, 24)
            session.add(model_run2)
            session.commit()
            model_run3 = ModelRun()
            model_run3.user_id = user1.id
            model_run3.name = "MR3"
            model_run3.date_created = datetime(2014, 6, 9, 11, 39, 30)
            session.add_all([model_run1, model_run2, model_run3])
        model_runs = self.model_run_service.get_models_for_user(user1)
        assert_that(model_runs[0].name, is_("MR2"))
        assert_that(model_runs[1].name, is_("MR3"))
        assert_that(model_runs[2].name, is_("MR1"))

    def test_WHEN_get_published_model_runs_THEN_list_ordered_by_date_created_newest_first(self):
        with session_scope(Session) as session:
            # Create three published models not in datetime order
            model_run1 = ModelRun()
            model_run1.name = "MR1"
            model_run1.date_created = datetime(2013, 12, 7, 17, 15, 30)
            model_run1.status = self._status(constants.MODEL_RUN_STATUS_PUBLISHED)
            session.add(model_run1)
            session.commit()
            model_run2 = ModelRun()
            model_run2.name = "MR2"
            model_run2.date_created = datetime(2014, 6, 9, 12, 30, 24)
            model_run2.status = self._status(constants.MODEL_RUN_STATUS_PUBLISHED)
            session.add(model_run2)
            session.commit()
            model_run3 = ModelRun()
            model_run3.name = "MR3"
            model_run3.date_created = datetime(2014, 6, 9, 11, 39, 30)
            model_run3.status = self._status(constants.MODEL_RUN_STATUS_PUBLISHED)
            session.add_all([model_run1, model_run2, model_run3])
        model_runs = self.model_run_service.get_published_models()
        assert_that(model_runs[0].name, is_("MR2"))
        assert_that(model_runs[1].name, is_("MR3"))
        assert_that(model_runs[2].name, is_("MR1"))

    def test_WHEN_get_code_versions_THEN_returns_list_including_default_code_version(self):

        models = self.model_run_service.get_code_versions()

        assert_that(len(models), is_not(0), "There should be at least one code version on the list")
        assert_that([x.name for x in models], has_item(config['default_code_version']), "The list of code versions")

    def test_GIVEN_valid_code_version_id_WHEN_get_code_version_THEN_code_version_returned(self):
        expectedModel = self.model_run_service.get_code_versions()[0]

        model = self.model_run_service.get_code_version_by_id(expectedModel.id)

        assert_that(model.id, is_(expectedModel.id), "Id")
        assert_that(model.name, is_(expectedModel.name), "Name")

    def test_GIVEN_non_existent_code_version_id_WHEN_get_code_version_THEN_raises_NoResultFound_exception(self):
        with self.assertRaises(NoResultFound, msg="Should have thrown a NoResultFound exception"):
            model = self.model_run_service.get_code_version_by_id(-100)

    def test_GIVEN_user_has_model_run_WHEN_get_model_run_by_id_THEN_model_run_returned(self):
        # Add a user and give them a model
        with session_scope(Session) as session:
            # First add user
            user = User()
            user.name = 'user1'
            session.add(user)
            session.commit()
            # Give them a model
            model_run = ModelRun()
            model_run.name = "MR1"
            model_run.user_id = user.id
            session.add(model_run)
        # Get the users model runs
        model_run_returned = self.model_run_service.get_model_by_id(user, model_run.id)
        assert_that(model_run_returned.name, is_("MR1"))

    def test_GIVEN_model_run_id_belongs_to_another_user_WHEN_get_model_run_by_id_THEN_NoResultFound_exception(self):
        # Add two users and give one a model
        with session_scope(Session) as session:
            user = User()
            user.name = 'user1'
            user2 = User()
            user2.name = 'user2'
            session.add_all([user, user2])
            session.commit()
            # Give them a model
            model_run = ModelRun()
            model_run.name = "MR1"
            model_run.user_id = user.id
            model_run.status = self._status(constants.MODEL_RUN_STATUS_COMPLETED)
            session.add(model_run)
        # Get the users model runs
        with self.assertRaises(NoResultFound, msg="Should have thrown a NoResultFound exception"):
            self.model_run_service.get_model_by_id(user2, model_run.id)

    def test_GIVEN_no_defining_model_run_WHEN_get_defining_model_run_THEN_error_returned(self):
        user = self.login()
        with self.assertRaises(NoResultFound, msg="Should have thrown a NoResultFound exception"):
            self.model_run_service.get_parameters_for_model_being_created(user)

    def test_GIVEN_incomplete_model_WHEN_publish_model_THEN_ServiceException_raised(self):
        # Add a user and give them a model
        with session_scope(Session) as session:
            user = User()
            user.name = 'user1'
            session.add(user)
            session.commit()
            # Give them a model
            model_run = ModelRun()
            model_run.name = "MR1"
            model_run.user_id = user.id
            model_run.status = self._status(constants.MODEL_RUN_STATUS_FAILED)
            session.add(model_run)
        # Get the users model runs
        with self.assertRaises(ServiceException, msg="Should have raised a ServiceException"):
            self.model_run_service.publish_model(user, model_run.id)

    def test_GIVEN_model_belongs_to_another_user_WHEN_publish_model_THEN_ServiceException_raised(self):
        # Add two users and give one a model
        with session_scope(Session) as session:
            user = User()
            user.name = 'user1'
            user2 = User()
            user2.name = 'user2'
            session.add_all([user, user2])
            session.commit()
            # Give them a model
            model_run = ModelRun()
            model_run.name = "MR1"
            model_run.user_id = user.id
            model_run.status = self._status(constants.MODEL_RUN_STATUS_COMPLETED)
            session.add(model_run)
        # Get the users model runs
        with self.assertRaises(ServiceException, msg="Should have raised a ServiceException"):
            self.model_run_service.publish_model(user2, model_run.id)

    def test_GIVEN_nonexistent_model_id_WHEN_publish_model_THEN_ServiceException_raised(self):
        # Add a user
        with session_scope(Session) as session:
            user = User()
            user.name = 'user1'
            session.add(user)
        with self.assertRaises(ServiceException, msg="Should have raised a ServiceException"):
            self.model_run_service.publish_model(user, -100)

    def test_GIVEN_user_has_completed_model_WHEN_publish_model_THEN_model_published(self):
        # Add a user and give them a model
        with session_scope(Session) as session:
            user = User()
            user.name = 'user1'
            session.add(user)
            session.commit()
            # Give them a model
            model_run = ModelRun()
            model_run.name = "MR1"
            model_run.user_id = user.id
            model_run.status = self._status(constants.MODEL_RUN_STATUS_COMPLETED)
            session.add(model_run)
        # Get the users model runs
        self.model_run_service.publish_model(user, model_run.id)
        with session_scope(Session) as session:
            updated_model_run = session.query(ModelRun).join(ModelRunStatus).filter(ModelRun.id == model_run.id).one()
            assert_that(updated_model_run.status.name, is_(constants.MODEL_RUN_STATUS_PUBLISHED))

    def test_GIVEN_default_science_configurations_THEN_all_configurations_returned(self):

         results = self.model_run_service.get_scientific_configurations()

         assert_that(len(results), greater_than(0), "at least one default configuration")
         assert_that(results[0]['id'], not_none(), "Configuration has an id")
         assert_that(results[0]['name'], not_none(), "Configuration has a name")
         assert_that(results[0]['description'], not_none(), "Configuration has a description")

    def test_GIVEN_model_with_parameters_WHEN_get_parameter_value_THEN_parameter_value_returned(self):
        with session_scope(Session) as session:
            user = User()
            user.name = 'user1'
            session.add(user)
            session.commit()

            param = session.query(Parameter).first()
            param_id = param.id
            param_name = param.name
            param_namelist = param.namelist.name

            model_run = ModelRun()
            model_run.name = "MR1"
            model_run.user_id = user.id
            model_run.status = self._status(constants.MODEL_RUN_STATUS_CREATED)
            session.add(model_run)
            session.commit()

            parameter1 = ParameterValue()
            parameter1.parameter_id = param_id
            parameter1.value = "param1 value"
            parameter1.model_run_id = model_run.id
            session.add(parameter1)
        model_run_returned = self.model_run_service.get_model_being_created_with_non_default_parameter_values(user)
        param_value_returned = model_run_returned.get_parameter_value(param_name, param_namelist)
        assert_that(param_value_returned, is_("param1 value"))

    def test_GIVEN_no_run_model_WHEN_create_run_model_with_science_config_THEN_model_created_with_parameter_values_copied(self):

        user = self.login()
        expected_name = "model run name"
        expected_description = "some slightly long winded description"

        self.model_run_service.update_model_run(
            user,
            expected_name,
            constants.DEFAULT_SCIENCE_CONFIGURATION,
            expected_description)

        parameter_values_count = self.count_parameter_values_in_model_being_created(user)
        assert_that(parameter_values_count, is_not(0), "parameter values have been set")

    def test_GIVEN_run_model_WHEN_create_run_model_with_same_science_config_THEN_model_updated_with_new_parameter_values_copied(self):

        user = self.login()
        expected_name = "model run name"
        expected_description = "some slightly long winded description"
        self.model_run_service.update_model_run(
            user,
            expected_name,
            constants.DEFAULT_SCIENCE_CONFIGURATION,
            expected_description)
        expected_parameters_count = self.count_parameter_values_in_model_being_created(user)

        self.model_run_service.update_model_run(
            user,
            expected_name,
            constants.DEFAULT_SCIENCE_CONFIGURATION,
            expected_description)

        parameter_values_count = self.count_parameter_values_in_model_being_created(user)
        assert_that(parameter_values_count, is_(expected_parameters_count), "parameter values have been set and old ones removed")

    def test_GIVEN_run_model_with_time_extent_WHEN_create_run_model_with_same_science_config_THEN_model_updated_with_new_parameter_values_copied_and_has_time_extent(self):

        user = self.login()
        expected_name = "model run name"
        expected_description = "some slightly long winded description"
        self.model_run_service.update_model_run(
            user,
            expected_name,
            constants.DEFAULT_SCIENCE_CONFIGURATION,
            expected_description)
        self.model_run_service.save_parameter(constants.JULES_PARAM_LATLON_REGION[1],
                                                   constants.JULES_PARAM_LATLON_REGION[0], True, user)
        expected_parameters_count = self.count_parameter_values_in_model_being_created(user)

        self.model_run_service.update_model_run(
            user,
            expected_name,
            constants.DEFAULT_SCIENCE_CONFIGURATION,
            expected_description)

        parameter_values_count = self.count_parameter_values_in_model_being_created(user)
        assert_that(parameter_values_count, is_(expected_parameters_count), "parameter values have been set and old ones removed")


    def count_parameter_values_in_model_being_created(self, user):
        """
        Count the number of parameter values that this model has
        """
        with session_scope(Session) as session:
            parameter_values = session \
                .query(ParameterValue) \
                .join(ModelRun) \
                .join(ModelRunStatus) \
                .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_CREATED) \
                .filter(ModelRun.user == user) \
                .count()
        return parameter_values