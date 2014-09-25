"""
#    Majic
#    Copyright (C) 2014  CEH
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
from datetime import datetime
from mock import Mock
from sqlalchemy.orm.exc import NoResultFound

from hamcrest import *
from joj.model import User, session_scope, Session, ModelRun, ModelRunStatus, Parameter, ParameterValue, Dataset, \
    LandCoverAction
from joj.services.general import ServiceException
from joj.services.model_run_service import ModelRunService
from pylons import config
from joj.utils import constants
from joj.services.job_runner_client import JobRunnerClient
from joj.tests.test_with_create_full_model_run import TestWithFullModelRun


class ModelRunServiceDeleteTest(TestWithFullModelRun):
    def setUp(self):
        super(ModelRunServiceDeleteTest, self).setUp()
        self.job_runner_client = JobRunnerClient(config)
        self.model_run_service = ModelRunService(job_runner_client=self.job_runner_client)
        self.clean_database()

    def test_GIVEN_model_doesnot_exist_WHEN_delete_THEN_not_found(self):
        # Add a user who doesn't have any model runs
        with session_scope(Session) as session:
            user = User()
            user.name = 'Has No Model Runs'
            session.add(user)

        # Get the users model runs
        with self.assertRaises(NoResultFound, msg="Should have thrown a NoResultFound exception"):
            model_runs = self.model_run_service.delete_run_model(10000, user)

    def test_GIVEN_model_belongs_to_someone_else_WHEN_delete_THEN_not_found(self):
        # Add a user who doesn't have any model runs
        other_user = self.login("other_user")
        model = self.create_run_model(10, "test", other_user)

        with session_scope(Session) as session:
            user = User()
            user.name = 'Has No Model Runs'
            session.add(user)

        # Get the users model runs
        with self.assertRaises(NoResultFound, msg="Should have thrown a NoResultFound exception"):
            self.model_run_service.delete_run_model(model.id, user)

    def test_GIVEN_model_WHEN_delete_THEN_model_delete_job_runner_called(self):
        # Add a user who doesn't have any model runs
        user = self.login()
        model = self.create_run_model(10, "test", user)
        self.job_runner_client.delete = Mock()

        self.model_run_service.delete_run_model(model.id, user)

        assert_that(self.job_runner_client.delete.called, is_(True), "Job runner called")
        with self.assertRaises(NoResultFound):
            self.model_run_service.get_model_by_id(user, model.id)

    def test_GIVEN_model_belongs_to_someone_else_and_user_is_an_admin_WHEN_delete_THEN_delete_model(self):
        # Add a user who doesn't have any model runs
        self.job_runner_client.delete = Mock()
        other_user = self.login("other_user")
        model = self.create_run_model(10, "test", other_user)
        user = self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

        self.model_run_service.delete_run_model(model.id, user)

        with self.assertRaises(NoResultFound):
            self.model_run_service.get_model_by_id(user, model.id)

    def test_GIVEN_model_belongs_to_someone_else_and_is_published_and_user_is_an_admin_WHEN_delete_THEN_delete_model(self):
        self.job_runner_client.delete = Mock()
        # Add a user who doesn't have any model runs
        other_user = self.login("other_user")
        model = self.create_run_model(10, "test", other_user, constants.MODEL_RUN_STATUS_PUBLISHED)
        user = self.login(access_level=constants.USER_ACCESS_LEVEL_ADMIN)

        self.model_run_service.delete_run_model(model.id, user)

        with self.assertRaises(NoResultFound):
            self.model_run_service.get_model_by_id(user, model.id)

    def test_GIVEN_full_model_WHEN_delete_THEN_model_is_deleted(self):

        user = self.login('')
        self.create_model_run_ready_for_submit()
        with session_scope(Session) as session:
            dataset_count = session.query(Dataset).count()
            model = self.model_run_service.get_models_for_user(user)[0]
            dataset = Dataset()
            dataset.model_run_id = model.id
            session.add(dataset)

            region_count = session.query(LandCoverAction).count()
            session.add(LandCoverAction(model_run_id=model.id))

        model_not_to_delete = self.create_run_model(0, "test", user, constants.MODEL_RUN_STATUS_PUBLISHED)
        self.job_runner_client.delete = Mock()

        self.model_run_service.delete_run_model(model.id, user)

        with session_scope(Session) as session:
            count = session.query(ModelRun).filter(ModelRun.id == model.id).count()
        assert_that(count, is_(0), 'Count(Model)')
        with session_scope(Session) as session:
            count = session.query(ModelRun).filter(ModelRun.id == model_not_to_delete.id).count()
        assert_that(count, is_(1), 'Count(Model)')
        with session_scope(Session) as session:
            count = session.query(Dataset).count()
        assert_that(count, is_(dataset_count), 'Count(Datasets)is same as before creating model')
        with session_scope(Session) as session:
            count = session.query(LandCoverAction).count()
        assert_that(count, is_(region_count), 'Count(LandCoverAction)is same as before creating model')

    def test_GIVEN_full_model_WHEN_delete_THEN_parameter_values_are_deleted(self):

        user = self.login('')
        with session_scope(Session) as session:
            pv_count = session.query(ParameterValue).count()

        self.create_model_run_ready_for_submit()
        with session_scope(Session) as session:
            model = self.model_run_service.get_models_for_user(user)[0]
            assert_that(session.query(ParameterValue).count(), greater_than(pv_count), "Creating model run adds parameters")

        self.job_runner_client.delete = Mock()

        self.model_run_service.delete_run_model(model.id, user)

        with session_scope(Session) as session:
            assert_that(session.query(ParameterValue).count(), is_(pv_count), "Parameter values is same as before model was created")

