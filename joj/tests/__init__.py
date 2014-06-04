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

import pylons
from pylons.i18n.translation import _get_translator
from paste.deploy import loadapp
from pylons import url
from paste.script.appinstall import SetupCommand
from routes.util import URLGenerator
from webtest import TestApp

from joj.config.environment import load_environment
from model import User, ModelRun, Dataset, ParameterValue, session_scope, Session, AccountRequest
from services.user import UserService

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
            session.query(ModelRun).delete()
            session.query(User).delete()
            session.query(ParameterValue).delete()
            session.query(AccountRequest).delete()