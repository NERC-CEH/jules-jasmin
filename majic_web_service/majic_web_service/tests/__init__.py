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
from sqlalchemy.orm.exc import NoResultFound
from webtest import TestApp

from majic_web_service.config.environment import load_environment
from majic_web_service.model import session_scope, ModelRun, User, ModelRunStatus

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

    def add_model_run(self, username, last_status_change, status, model_name="model name", description="a description"):
        with session_scope() as session:
            try:
                user = session.query(User).filter(User.username == username).one()
            except NoResultFound:
                user = User(username=username)
                session.add(user)

            found_status = session.query(ModelRunStatus).filter(ModelRunStatus.name == status).one()

            model_run = ModelRun()
            model_run.name = model_name
            model_run.status = found_status
            model_run.last_status_change = last_status_change
            model_run.description = description
            model_run.user = user
            session.add(model_run)
            session.flush()
            return model_run.id
