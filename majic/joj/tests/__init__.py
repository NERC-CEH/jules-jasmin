"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
from unittest import TestCase
import datetime
import sys

from hamcrest import assert_that, is_
from mock import Mock
import os
import pylons
from pylons.i18n.translation import _get_translator
from paste.deploy import loadapp
from pylons import url
from routes.util import URLGenerator
from sqlalchemy import or_
from webtest import TestApp

from joj.model import User, Dataset, ParameterValue, ModelRunStatus, \
    DrivingDatasetParameterValue, DrivingDataset, DrivingDatasetLocation, SystemAlertEmail, \
    AccountRequest, LandCoverAction, LandCoverRegion, LandCoverRegionCategory
from joj.services.user import UserService
from joj.utils import constants, f90_helper
from joj.services.model_run_service import ModelRunService
from joj.model import session_scope, Session, ModelRun
from joj.services.dap_client.dap_client_factory import DapClientFactory
from joj.model.non_database.driving_dataset_jules_params import DrivingDatasetJulesParams


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
            parameter_to_keep = session \
                .query(ParameterValue.id) \
                .join(ModelRun) \
                .join(User) \
                .filter(User.username == constants.CORE_USERNAME) \
                .all()

            session.query(LandCoverAction).delete()
            session.query(LandCoverRegion).delete()
            session.query(LandCoverRegionCategory).delete()

            session \
                .query(ParameterValue) \
                .filter(ParameterValue.id.notin_([x[0] for x in parameter_to_keep])) \
                .delete(synchronize_session='fetch')

            core_user_id = session.query(User.id).filter(User.username == constants.CORE_USERNAME).one()[0]

            session.query(Dataset).delete()

            published_status = session \
                .query(ModelRunStatus) \
                .filter(ModelRunStatus.name == constants.MODEL_RUN_STATUS_PUBLISHED) \
                .one()

            # delete all runs except the scientific configurations
            session \
                .query(ModelRun) \
                .filter(or_(
                ModelRun.user_id != core_user_id,
                ModelRun.user_id.is_(None),
                ModelRun.status_id == published_status.id)) \
                .delete(synchronize_session='fetch')

            session.query(DrivingDatasetLocation).delete()
            session.query(DrivingDatasetParameterValue).delete()
            session.query(DrivingDataset) \
                .filter(DrivingDataset.name != constants.USER_UPLOAD_DRIVING_DATASET_NAME) \
                .delete()

            session \
                .query(User) \
                .filter(or_(User.username != constants.CORE_USERNAME, User.username.is_(None))) \
                .delete()

            session.query(AccountRequest).delete()

            emails = session \
                .query(SystemAlertEmail).all()
            for email in emails:
                email.last_sent = None

    def assert_model_definition(self, expected_username, expected_science_configuration, expected_name,
                                expected_description):
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
        ).params(status=constants.MODEL_RUN_STATUS_CREATED, username=expected_username).one()
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
        ).params(status=constants.MODEL_RUN_STATUS_CREATED, parameter_id=parameter_id).one()
        assert_that(row.value, is_(expected_parameter_value), "parameter value")

    def _status(self, status_name):
        """
        Return from the database the ModelRunStatus for a requested status name
        :param status_name: The name of the status to find
        :return: The matching status object
        """
        with session_scope(Session) as session:
            return session.query(ModelRunStatus).filter(ModelRunStatus.name == status_name).one()

    def create_driving_dataset(
            self,
            session,
            jules_params=DrivingDatasetJulesParams(dataperiod=3600, var_interps=8 * ["i"])):
        """
        Create a driving dataset
        :param session: session to use
        :param jules_params: set of jules parameters
        :return: dataset
        """
        model_run_service = ModelRunService()

        driving1 = DrivingDataset()
        driving1.name = "driving1"
        driving1.description = "driving 1 description"
        driving1.geographic_region = 'European'
        driving1.spatial_resolution = '1km'
        driving1.temporal_resolution = '24 hours'
        driving1.boundary_lat_north = 50
        driving1.boundary_lat_south = -10
        driving1.boundary_lon_west = -15
        driving1.boundary_lon_east = 30
        driving1.time_start = datetime.datetime(1979, 1, 1, 0, 0, 0)
        driving1.time_end = datetime.datetime(2010, 1, 1, 0, 0, 0)
        driving1.view_order_index = 100
        driving1.is_restricted_to_admins = False
        location1 = DrivingDatasetLocation()
        location1.base_url = "base_url"
        location1.driving_dataset = driving1
        location2 = DrivingDatasetLocation()
        location2.base_url = "base_url2"
        location2.driving_dataset = driving1
        jules_params.add_to_driving_dataset(model_run_service, driving1, session)

        val = f90_helper.python_to_f90_str(8 * ["i"])
        pv1 = DrivingDatasetParameterValue(model_run_service, driving1,
                                           constants.JULES_PARAM_DRIVE_INTERP, val)
        val = f90_helper.python_to_f90_str(3600)
        pv2 = DrivingDatasetParameterValue(model_run_service, driving1,
                                           constants.JULES_PARAM_DRIVE_DATA_PERIOD, val)
        val = f90_helper.python_to_f90_str("data/driving1/frac.nc")
        pv3 = DrivingDatasetParameterValue(model_run_service, driving1,
                                           constants.JULES_PARAM_FRAC_FILE, val)
        val = f90_helper.python_to_f90_str("frac")
        pv4 = DrivingDatasetParameterValue(model_run_service, driving1,
                                           constants.JULES_PARAM_FRAC_NAME, val)

        session.add(driving1)
        session.commit()

        driving_data_filename_param_val = DrivingDatasetParameterValue(
            model_run_service,
            driving1,
            constants.JULES_PARAM_DRIVE_FILE,
            "'testFileName'")
        session.add(driving_data_filename_param_val)
        session.commit()

        return driving1

    def create_two_driving_datasets(self):
        """
        Creates two driving datasets with datasets, parameter values etc set up
        :return: nothing
        """

        with session_scope(Session) as session:
            self.create_driving_dataset(session)

            model_run_service = ModelRunService()

            driving2 = DrivingDataset()
            driving2.name = "driving2"
            driving2.description = "driving 2 description"
            driving2.geographic_region = 'Global'
            driving2.spatial_resolution = 'Half degree'
            driving2.temporal_resolution = '3 Hours'
            driving2.boundary_lat_north = 85
            driving2.boundary_lat_south = -90
            driving2.boundary_lon_west = -180
            driving2.boundary_lon_east = 180
            driving2.time_start = datetime.datetime(1901, 1, 1, 0, 0, 0)
            driving2.time_end = datetime.datetime(2001, 1, 1, 0, 0, 0)
            driving2.view_order_index = 200
            driving2.usage_order_index = 2
            driving2.is_restricted_to_admins = False

            location3 = DrivingDatasetLocation()
            location3.base_url = "base_url3"
            location3.driving_dataset = driving2

            val = f90_helper.python_to_f90_str(8 * ["i"])
            pv1 = DrivingDatasetParameterValue(model_run_service, driving2,
                                               constants.JULES_PARAM_DRIVE_INTERP, val)
            val = f90_helper.python_to_f90_str(3600)
            pv2 = DrivingDatasetParameterValue(model_run_service, driving2,
                                               constants.JULES_PARAM_DRIVE_DATA_PERIOD, val)
            val = f90_helper.python_to_f90_str("data/driving2/frac.nc")
            pv3 = DrivingDatasetParameterValue(model_run_service, driving2,
                                               constants.JULES_PARAM_FRAC_FILE, val)
            val = f90_helper.python_to_f90_str("frac2")
            pv4 = DrivingDatasetParameterValue(model_run_service, driving2,
                                               constants.JULES_PARAM_FRAC_NAME, val)
            val = f90_helper.python_to_f90_str(['b', 'sathh', 'satcon', 'sm_sat', 'sm_crit',
                                                'sm_wilt', 'hcap', 'hcon', 'albsoil'])
            pv5 = DrivingDatasetParameterValue(model_run_service, driving2,
                                               constants.JULES_PARAM_SOIL_PROPS_VAR, val)
            val = f90_helper.python_to_f90_str(['bexp', 'sathh', 'satcon', 'vsat', 'vcrit',
                                                'vwilt', 'hcap', 'hcon', 'albsoil'])
            pv6 = DrivingDatasetParameterValue(model_run_service, driving2,
                                               constants.JULES_PARAM_SOIL_PROPS_VAR_NAME, val)
            val = f90_helper.python_to_f90_str(9)
            pv7 = DrivingDatasetParameterValue(model_run_service, driving2,
                                               constants.JULES_PARAM_SOIL_PROPS_NVARS, val)
            val = f90_helper.python_to_f90_str("data/WATCH_2D/ancils/soil_igbp_bc_watch_0p5deg_capUM6.6_2D.nc")
            pv7 = DrivingDatasetParameterValue(model_run_service, driving2,
                                               constants.JULES_PARAM_SOIL_PROPS_FILE, val)
            session.add(driving2)
            session.commit()

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
            science_configuration = model_run_service._get_science_configuration(
                constants.DEFAULT_SCIENCE_CONFIGURATION, session)
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
        self.dap_client_factory = DapClientFactory()
        self.dap_client_factory.get_dap_client = Mock(return_value=self.dap_client)
        return self.dap_client_factory

    def create_account_request(self, email_addess="test@test.ceh.ac.uk"):
        """
        Create an account request
        :return: id of account request
        """
        with session_scope() as session:
            self.account_request = AccountRequest()
            self.account_request.email = email_addess
            self.account_request.institution = "institution"
            self.account_request.first_name = "a very unique name for the user " + str(datetime.datetime.now())
            self.account_request.last_name = "last name"
            self.account_request.usage = "usage"
            session.add(self.account_request)

        with session_scope() as session:
            ac = session.query(AccountRequest).filter(
                AccountRequest.first_name == self.account_request.first_name).one()
            return ac.id

    def add_land_cover_actions(self, land_cover_region, model_run, value_order_pairs, land_cover_service):
        """
        Create land cover actions and save them using the model_run_service.save_land_cover_actions method
        :param land_cover_region: Land cover region actions should belong to
        :param model_run: Model run to add them against
        :param value_order_pairs: List of 2-tuples [(value, order)]; each tuple is a land cover action to be added
        :param land_cover_service: Land Cover service to use
        :return:
        """
        land_cover_actions = []
        for value, order in value_order_pairs:
            lca = LandCoverAction()
            lca.region_id = land_cover_region.id
            lca.value_id = value
            lca.order = order
            land_cover_actions.append(lca)
        land_cover_service.save_land_cover_actions_for_model(model_run, land_cover_actions)

    def add_land_cover_region(self, model_run):
        with session_scope() as session:
            land_cover_cat = LandCoverRegionCategory()
            land_cover_cat.name = "Countries"
            land_cover_cat.driving_dataset_id = model_run.driving_dataset_id

            land_cover_region = LandCoverRegion()
            land_cover_region.mask_file = "filepath"
            land_cover_region.name = "Wales"
            land_cover_region.category = land_cover_cat

            session.add(land_cover_region)
        return land_cover_region

    def _add_model_run_being_created(self, user):
        model_run_service = ModelRunService()
        model_run_service.update_model_run(user, "test", constants.DEFAULT_SCIENCE_CONFIGURATION)