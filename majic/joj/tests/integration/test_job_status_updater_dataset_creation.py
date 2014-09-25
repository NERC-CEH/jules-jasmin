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
from hamcrest import *
from mock import Mock

from joj.model import session_scope, Session, Dataset
from joj.utils import constants
from joj.services.model_run_service import ModelRunService
from joj.tests.test_with_create_full_model_run import TestWithFullModelRun
from joj.services.dap_client.dap_client import DapClientException


class TestJobDataUpdaterCreation(TestWithFullModelRun):
    """
    Test for the JobDataUpdater
    """

    def setUp(self):
        super(TestJobDataUpdaterCreation, self).setUp()

    def test_GIVEN_one_pending_job_in_the_database_which_has_completed_WHEN_update_THEN_model_run_data_is_in_datasets(self):

        self.create_model_run_ready_for_submit()
        model_run_service = ModelRunService()
        model_run = model_run_service.get_model_run_being_created_or_default(self.user)
        with session_scope(Session) as session:
            model_run.change_status(session, constants.MODEL_RUN_STATUS_RUNNING)

        self.running_job_client.get_run_model_statuses = Mock(
            return_value=[{'id': model_run.id,
                           'status': constants.MODEL_RUN_STATUS_COMPLETED,
                           'error_message': ''
                           }])

        self.job_status_updater.update()

        with session_scope() as session:
            datasets = session.query(Dataset)\
                .filter(Dataset.model_run_id == model_run.id)\
                .filter(Dataset.is_input == False)\
                .all()
            assert_that(len(datasets), is_(3), "Number of output datasets")
            dataset_names = [dataset.name for dataset in datasets]
            assert_that(dataset_names, contains_inanyorder(
                contains_string('Monthly'), contains_string('Yearly'), contains_string('Hourly')))
            dataset_wms_urls = [dataset.wms_url for dataset in datasets]
            assert_that(dataset_wms_urls, contains_inanyorder(
                contains_string('output/majic.fch4_wetl_yearly.ncml'),
                contains_string('output/majic.fch4_wetl_monthly.ncml'),
                contains_string('output/majic.albedo_land_hourly.ncml')))

            datasets = session.query(Dataset)\
                .filter(Dataset.model_run_id == model_run.id)\
                .filter(Dataset.is_input == True)\
                .all()
            assert_that(len(datasets), is_(2), "Number of input datasets")

    def test_GIVEN_one_pending_job_in_the_database_which_has_completed_WHEN_update_dap_client_not_availiable_THEN_model_run_status_is_not_updated(self):

        self.dap_client_factory.get_dap_client = Mock(side_effect=DapClientException("trouble"))
        self.create_model_run_ready_for_submit()
        model_run_service = ModelRunService()
        model_run = model_run_service.get_model_run_being_created_or_default(self.user)
        with session_scope(Session) as session:
            model_run.change_status(session, constants.MODEL_RUN_STATUS_RUNNING)

        self.running_job_client.get_run_model_statuses = Mock(
            return_value=[{'id': model_run.id,
                           'status': constants.MODEL_RUN_STATUS_COMPLETED,
                           'error_message': ''
                           }])

        self.job_status_updater.update()

        model_run = model_run_service.get_model_by_id(self.user, model_run.id)
        assert_that(model_run.status.name, is_(constants.MODEL_RUN_STATUS_RUNNING), "model status")
        with session_scope() as session:
            datasets = session.query(Dataset)\
                .filter(Dataset.model_run_id == model_run.id)\
                .filter(Dataset.is_input == False)\
                .all()
            assert_that(len(datasets), is_(0), "Number of output datasets")

            datasets = session.query(Dataset)\
                .filter(Dataset.model_run_id == model_run.id)\
                .filter(Dataset.is_input == True)\
                .all()
            assert_that(len(datasets), is_(0), "Number of input datasets")