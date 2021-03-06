"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
from unittest import TestCase
import os
import sys
from hamcrest import assert_that, is_

import pylons
from pylons.i18n.translation import _get_translator
from paste.deploy import loadapp
from pylons import url
from paste.script.appinstall import SetupCommand
from routes.util import URLGenerator
from sqlalchemy.orm.exc import NoResultFound
from webtest import TestApp

from majic_web_service.config.environment import load_environment
from majic_web_service.model import session_scope, ModelRun, User, ModelRunStatus
from majic_web_service.utils.constants import JSON_MODEL_RUN_ID, JSON_USER_NAME, JSON_IS_PUBLISHED, \
    JSON_LAST_STATUS_CHANGE, JSON_IS_PUBLIC
from majic_web_service.utils.general import convert_time_to_standard_string

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

    def clean_database(self):
        """
        Cleans the dynamic data from the database
        """
        with session_scope() as session:
            # delete all runs except the scientific configurations
            session \
                .query(ModelRun) \
                .delete()

            session \
                .query(User) \
                .delete()

    def add_model_run(
            self,
            workbench_username,
            last_status_change,
            status, model_name="model name",
            description="a description",
            majic_username=None):
        """
        Add a model run to the db
        :param workbench_username: username for the workbench
        :param last_status_change: last staus change
        :param status: current status (as string)
        :param model_name: name of the model
        :param description: description of the model
        :param majic_username: username in majic, defaults to the workbench_username if not set
        :return:id of model run created
        """
        with session_scope() as session:
            try:
                if majic_username is not None:
                    user = session.query(User).filter(User.username == majic_username).one()
                else:
                    user = session.query(User).filter(User.username == workbench_username).one()
            except NoResultFound:
                user = User(workbench_username=workbench_username)
                if majic_username is None:
                    user.username = workbench_username
                else:
                    user.username = majic_username
                session.add(user)

            if status is not None:
                found_status = session.query(ModelRunStatus).filter(ModelRunStatus.name == status).one()
            else:
                found_status = None

            model_run = ModelRun()
            model_run.name = model_name
            model_run.status = found_status
            model_run.last_status_change = last_status_change
            model_run.description = description
            model_run.user = user
            session.add(model_run)
            session.flush()
            return model_run.id

    def assert_model_run_json_is(self, model_run_json_dict, model_id, last_status_change, username, is_published, is_public):
        """
        assert that the model_run_json_dict has the expected answers
        :param model_run_json_dict: dictionary to check
        :param model_id: model id
        :param last_status_change: last status change
        :param username: the username who owns the model run
        :param is_published: whether model run is published
        :param is_public: whether model run is public
        :return: nothing
        :raises AssertionError: if the two don't match
        """
        assert_that(model_run_json_dict[JSON_MODEL_RUN_ID], is_(model_id), "model run id")
        assert_that(model_run_json_dict[JSON_USER_NAME], is_(username), "username")
        assert_that(model_run_json_dict[JSON_IS_PUBLISHED], is_(is_published), "the model is published")
        assert_that(model_run_json_dict[JSON_IS_PUBLIC], is_(is_public), "the model is public")
        assert_that(model_run_json_dict[JSON_LAST_STATUS_CHANGE], is_(convert_time_to_standard_string(last_status_change)), "last changed")
