"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
from unittest import TestCase
from hamcrest import assert_that, is_
import os
import sys

import pylons
from pylons.i18n.translation import _get_translator
from paste.deploy import loadapp
from pylons import url
from paste.script.appinstall import SetupCommand
from routes.util import URLGenerator
from webtest import TestApp

from joj.config.environment import load_environment
from joj.model import User, ModelRun, Dataset, ParameterValue, session_scope, Session, AccountRequest, ModelRunStatus
from joj.services.user import UserService
from joj.utils import constants

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

    def login(self):
        """
        Setup the request as if the user has already logged in as a non admin user
        """
        username = 'test'
        user_service = UserService()
        user = user_service.get_user_by_username(username)
        if user is None:
            user_service.create(username,'test', 'testerson', 'test@ceh.ac.uk', '')
            user = user_service.get_user_by_username(username)

        self.app.extra_environ['REMOTE_USER'] = str(user.username)

    def clean_database(self):
        """
        Cleans the User, ModelRun, Dataset and ParameterValue tables in the database
        """
        with session_scope(Session) as session:
            session.query(Dataset).delete()
            session.query(ParameterValue).delete()
            session.query(ModelRun).delete()
            session.query(User).delete()
            session.query(AccountRequest).delete()
            
    def assert_model_definition(self, expected_code_version, expected_name):
        """
        Check that a model definition is correct in the database. Throws assertion error if there is no match

        Arguments:
        expected_name -- the expected name
        expected_code_version -- the expceted code version id
        """
        session = Session()
        row = session.query("name", "code_version_id").from_statement(
            """
            SELECT m.name, m.code_version_id
            FROM model_runs m
            JOIN model_run_statuses s on s.id = m.status_id
            WHERE s.name=:status
            """
        ).params(status=constants.MODEL_RUN_STATUS_CREATING).one()
        assert_that(row.name, is_(expected_name), "model run name")
        assert_that(row.code_version_id, is_(expected_code_version), "code version")

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
        ).params(status=constants.MODEL_RUN_STATUS_CREATING, parameter_id = parameter_id).one()
        assert_that(row.value, is_(expected_parameter_value), "parameter value")

    def _status(self, status_name):
        """
        Return from the database the ModelRunStatus for a requested status name
        :param status_name: The name of the status to find
        :return: The matching status object
        """
        with session_scope(Session) as session:
            return session.query(ModelRunStatus).filter(ModelRunStatus.name == status_name).one()