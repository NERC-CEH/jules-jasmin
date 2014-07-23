"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
from unittest import TestCase
import datetime
from hamcrest import assert_that, is_
from mock import Mock
import os
import sys

import pylons
from pylons.i18n.translation import _get_translator
from paste.deploy import loadapp
from pylons import url
from paste.script.appinstall import SetupCommand
from routes.util import URLGenerator
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from webtest import TestApp

from joj.config.environment import load_environment
from joj.model import User, ModelRun, Dataset, ParameterValue, AccountRequest, ModelRunStatus, \
    Parameter, Namelist, DrivingDatasetParameterValue, DrivingDataset, DrivingDatasetLocation, SystemAlertEmail
from joj.services.user import UserService
from joj.utils import constants
from joj.services.model_run_service import ModelRunService
from joj.model import session_scope, Session, ModelRun
from joj.services.dap_client_factory import DapClientFactory

TEST_LOG_FORMAT_STRING = '%(name)-20s %(asctime)s ln:%(lineno)-3s %(levelname)-8s\n %(message)s\n'

__all__ = ['environ', 'url', 'TestController']

environ = {}
here_dir = os.path.dirname(os.path.abspath(__file__))
conf_dir = os.path.dirname(os.path.dirname(here_dir))

sys.path.insert(0, conf_dir)


class TestController(TestCase):
    def __init__(self, *args, **kwargs):
        wsgiapp = loadapp('config:test.ini', relative_to=conf_dir)
        config = wsgiapp.config
        pylons.app_globals._push_object(config['pylons.app_globals'])
        pylons.config._push_object(config)

        # Initialize a translator for tests that utilize i18n
        translator = _get_translator(pylons.config.get('lang'))
        pylons.translator._push_object(translator)

        url._push_object(URLGenerator(config['routes.map'], environ))
        self.app = TestApp(wsgiapp)
        TestCase.__init__(self, *args, **kwargs)

    def login(self, username="test", access_level=constants.USER_ACCESS_LEVEL_EXTERNAL):
        """
        Setup the request as if the user has already logged in as a non admin user

        :param username the username for the user to log in, stored in self.login_username, default "test"
        :return the details for the logged in user
        """
        self.login_username = username
        user_service = UserService()
        user = user_service.get_user_by_username(self.login_username)
        if user is None:
            user_service.create(self.login_username, 'test', 'testerson', 'test@ceh.ac.uk', access_level)
            user = user_service.get_user_by_username(self.login_username)

        self.app.extra_environ['REMOTE_USER'] = str(user.username)
        return user

    def clean_database(self):
        """
        Cleans the User, ModelRun, Dataset, DrivingDataset and ParameterValue tables in the database
        """
        with session_scope(Session) as session:
            parameter_to_keep = session\
                .query(ParameterValue.id)\
                .join(ModelRun)\
                .join(User)\
                .filter(User.username == constants.CORE_USERNAME)\
                .all()

            session\
                .query(ParameterValue)\
                .filter(ParameterValue.id.notin_([x[0] for x in parameter_to_keep]))\
                .delete(synchronize_session='fetch')

            core_user_id = session.query(User.id).filter(User.username == constants.CORE_USERNAME).one()[0]

            session.query(Dataset).delete()

            session\
                .query(ModelRun)\
                .filter(or_(ModelRun.user_id != core_user_id, ModelRun.user_id.is_(None)))\
                .delete(synchronize_session='fetch')

            session.query(DrivingDatasetLocation).delete()
            session.query(DrivingDatasetParameterValue).delete()
            session.query(DrivingDataset)\
                .filter(DrivingDataset.name != constants.USER_UPLOAD_DRIVING_DATASET_NAME)\
                .delete()

            session\
                .query(User)\
                .filter(User.username != constants.CORE_USERNAME)\
                .delete()

            session.query(AccountRequest).delete()

            emails = session\
                .query(SystemAlertEmail).all()
            for email in emails:
                email.last_sent = None
            
    def assert_model_definition(self, expected_username, expected_science_configuration, expected_name, expected_description):
        """
        Check that a model definition is correct in the database. Throws assertion error if there is no match

        Arguments:
        expected_name -- the expected name
        expected_science_configuration -- the expected science configuration id
        """
        session = Session()
        row = session.query("username", "name", "science_configuration_id", "description").from_statement(
            """
            SELECT u.username, m.name, m.science_configuration_id, m.description
            FROM model_runs m
            JOIN model_run_statuses s on s.id = m.status_id
            JOIN users u on u.id = m.user_id
            WHERE s.name=:status
              AND u.username = :username
            """
        ).params(status=constants.MODEL_RUN_STATUS_CREATED, username = expected_username).one()
        assert_that(row.username, is_(expected_username), "username")
        assert_that(row.name, is_(expected_name), "model run name")
        assert_that(row.science_configuration_id, is_(expected_science_configuration), "science_configuration_id")
        assert_that(row.description, is_(expected_description), "description")

    def assert_parameter_of_model_being_created_is_a_value(self, parameter_id, expected_parameter_value):
        """
        Assert that the parameter value is correct for the model being created
        :param parameter_id: the id of the parameter to assert the value of
        :param expected_parameter_value: expected parameters value
        :return:Nothing
        """

        session = Session()
        row = session.query("value").from_statement(
            """
            SELECT pv.value
            FROM model_runs m
            JOIN model_run_statuses s on s.id = m.status_id
            JOIN parameter_values pv on pv.model_run_id = m.id
            JOIN parameters p on pv.parameter_id = p.id
            WHERE s.name=:status
              AND p.id = :parameter_id
            """
        ).params(status=constants.MODEL_RUN_STATUS_CREATED, parameter_id = parameter_id).one()
        assert_that(row.value, is_(expected_parameter_value), "parameter value")

    def _status(self, status_name):
        """
        Return from the database the ModelRunStatus for a requested status name
        :param status_name: The name of the status to find
        :return: The matching status object
        """
        with session_scope(Session) as session:
            return session.query(ModelRunStatus).filter(ModelRunStatus.name == status_name).one()

    def create_two_driving_datasets(self):
        """
        Creates two driving datasets with datasets, parameter values etc set up
        :return: nothing
        """
        with session_scope(Session) as session:
            ds1 = Dataset()
            ds1.name = "Driving dataset 1"
            ds1.netcdf_url = "url1"
            ds2 = Dataset()
            ds2.name = "Driving dataset 2"
            ds2.netcdf_url = "url2"
            session.add_all([ds1, ds2])

            driving1 = DrivingDataset()
            driving1.name = "driving1"
            driving1.description = "driving 1 description"
            driving1.dataset = ds1
            driving1.geographic_region = 'European'
            driving1.spatial_resolution = '1km'
            driving1.temporal_resolution = '24 hours'
            driving1.boundary_lat_north = 50
            driving1.boundary_lat_south = -10
            driving1.boundary_lon_west = -15
            driving1.boundary_lon_east = 30
            driving1.time_start = datetime.datetime(1979, 1, 1, 0, 0, 0)
            driving1.time_end = datetime.datetime(2010, 1, 1, 0, 0, 0)
            driving1.order_by_id = 100
            location1 = DrivingDatasetLocation()
            location1.base_url = "base_url"
            location1.driving_dataset = driving1
            location2 = DrivingDatasetLocation()
            location2.base_url = "base_url2"
            location2.driving_dataset = driving1

            driving2 = DrivingDataset()
            driving2.name = "driving2"
            driving2.description = "driving 2 description"
            driving2.dataset = ds2
            driving2.geographic_region = 'Global'
            driving2.spatial_resolution = 'Half degree'
            driving2.temporal_resolution = '3 Hours'
            driving2.boundary_lat_north = 90
            driving2.boundary_lat_south = -90
            driving2.boundary_lon_west = -180
            driving2.boundary_lon_east = 180
            driving2.time_start = datetime.datetime(1901, 1, 1, 0, 0, 0)
            driving2.time_end = datetime.datetime(2001, 1, 1, 0, 0, 0)
            driving2.order_by_id = 200

            location3 = DrivingDatasetLocation()
            location3.base_url = "base_url3"
            location3.driving_dataset = driving2

            session.add_all([driving1, driving2])
            session.commit()

            model_run_service = ModelRunService()
            driving_data_filename_param_val = DrivingDatasetParameterValue(
                model_run_service,
                driving1,
                constants.JULES_PARAM_DRIVE_FILE,
                "'testFileName'")
            session.add(driving_data_filename_param_val)

    def assert_model_run_status_and_return(self, model_run_id, status):
        """
        assert that a model has a given status
        :param model_run_id: id of the model
        :param status: name of the status
        :return:the model run
        """
        with session_scope(Session) as session:
            result = session \
                .query(ModelRun) \
                .filter(ModelRun.id == model_run_id) \
                .one()
            assert_that(result.status.name, is_(status))
            return result

    def create_run_model(self, storage_in_mb, name, user, status=constants.MODEL_RUN_STATUS_COMPLETED):
        """
        Create a model run
        :param storage_in_mb: storage_in_mb for the model
        :param name: name of the model run
        :param user: user who has created the model run
        :param status: the status, default to complete
        :return:the model run
        """
        model_run_service = ModelRunService()
        with model_run_service.transaction_scope() as session:
            model_run = model_run_service._create_new_model_run(session, user)
            session.add(model_run)
            model_run.name = name
            science_configuration = model_run_service._get_science_configuration(constants.DEFAULT_SCIENCE_CONFIGURATION, session)
            model_run.science_configuration_id = science_configuration.id
            model_run.code_version = science_configuration.code_version
            model_run.description = "testing"
            model_run_service._copy_parameter_set_into_model(science_configuration.parameter_values, model_run, session)
            model_run.storage_in_mb = storage_in_mb
            model_run.change_status(session, status)

        return model_run

    def assert_model_run_creation_action(self, user, expected_action):
        """
        Assert that the user model run creation expected_action is correct
        :param user: user
        :param expected_action: expected_action
        :return:nothing
        """
        with session_scope(Session) as session:
            modified_user = session.query(User).filter(User.id == user.id).one()
            assert_that(modified_user.model_run_creation_action, is_(expected_action), "model run creation action")

    def create_mock_dap_factory_client(self):
        """
        Create a mock for the dap client
        :return:
        """
        self.dap_client = Mock()
        self.dap_client.get_longname = Mock(return_value="long_name")
        self.dap_client.get_data_range = Mock(return_value=[10, 12])
        dap_client_factory = DapClientFactory()
        dap_client_factory.get_dap_client = Mock(return_value=self.dap_client)
        return dap_client_factory