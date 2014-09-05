"""
# header
"""

import logging
from datetime import datetime

from sqlalchemy.orm import subqueryload
from dateutil.parser import parse

from joj.services.model_run_service import ModelRunService
from joj.services.general import DatabaseService
from joj.services.email_service import EmailService
from joj.model import ModelRun, ModelRunStatus, Session, Dataset, DatasetType, DrivingDatasetLocation, \
    SystemAlertEmail, User
from joj.utils import constants
from joj.utils.utils import KeyNotFound, find_by_id_in_dict
from joj.utils import email_messages, utils
from joj.services.dap_client.dap_client_factory import DapClientFactory
from joj.services.dap_client.dap_client import DapClientException


log = logging.getLogger(__name__)


class JobStatusUpdaterService(DatabaseService):
    """
    Service to update the job status in the database based on the status returned by the job runner
    """

    def __init__(
            self,
            job_runner_client,
            config,
            session=Session,
            model_run_service=ModelRunService(),
            email_service=None,
            dap_client_factory=DapClientFactory()):
        """
        Initiate
        :param session: the session to use
        :param model_run_service: the model run service
        :param job_runner_client: the job runner client
        :param email_service: the email service to use (defaults to one using the config passed in)
        :param dap_client_factory: factory for making dap clients class to use
        :return:nothing
        """
        super(JobStatusUpdaterService, self).__init__(session)
        self._job_runner_client = job_runner_client
        self._model_run_service = model_run_service
        if email_service is None:
            self._email_service = EmailService(config)
        else:
            self._email_service = email_service
        self._dap_client_factory = dap_client_factory
        self._config = config

    def update(self):
        """
        Update the status of all pending model runs
        :return:nothing
        """
        model_ids = self._get_ids_for_submitted_model_runs()
        if len(model_ids) == 0:
            return

        job_statuses = self._job_runner_client.get_run_model_statuses(model_ids)

        for model_id in model_ids:
            try:
                run_model = self._update_model_run_status(job_statuses, model_id)
                self._send_email(run_model)
            except DapClientException, ex:
                log.exception("DAP client threw an exception: %s", ex.message)

        self._check_total_allocation_and_alert()

    def _get_ids_for_submitted_model_runs(self):
        """
        Get the ids of model runs which are submitted but to finished
        :return:list of model ids
        """
        with self.readonly_scope() as session:
            model_runs = session.query(ModelRun) \
                .join(ModelRunStatus) \
                .filter(ModelRunStatus.name.in_([
                    constants.MODEL_RUN_STATUS_PENDING,
                    constants.MODEL_RUN_STATUS_RUNNING,
                    constants.MODEL_RUN_STATUS_SUBMITTED])) \
                .all()
            return [model_run.id for model_run in model_runs]

    def _update_model_run_status(self, job_statuses, model_id):
        """
        Find the new status and update it for a model
        :param job_statuses: a list of new job statuses
        :param model_id: the model id
        :return: model_run
        """
        with self.transaction_scope() as session:
            model_run = session.query(ModelRun) \
                .filter(ModelRun.id == model_id) \
                .options(subqueryload(ModelRun.user)) \
                .one()

            try:
                job_status = find_by_id_in_dict(job_statuses, model_run.id)
                if constants.JSON_STATUS_STORAGE in job_status:
                    model_run.storage_in_mb = job_status[constants.JSON_STATUS_STORAGE]
                else:
                    model_run.storage_in_mb = 0

                model_run.date_started = None
                model_run.time_elapsed_secs = 0
                if constants.JSON_STATUS_START_TIME in job_status \
                        and job_status[constants.JSON_STATUS_START_TIME] is not None:
                    model_run.date_started = parse(job_status[constants.JSON_STATUS_START_TIME])
                    if constants.JSON_STATUS_END_TIME in job_status\
                            and job_status[constants.JSON_STATUS_END_TIME] is not None:
                        end = parse(job_status[constants.JSON_STATUS_END_TIME])
                        model_run.time_elapsed_secs = int((end - model_run.date_started).total_seconds())

                model_run.change_status(session, job_status['status'], job_status['error_message'])
                if job_status['status'] == constants.MODEL_RUN_STATUS_COMPLETED:
                    self._update_datasets(model_run, session)
            except KeyNotFound:
                log.error("No status returned from job runner for model run %s", model_id)
                model_run.change_status(session, constants.MODEL_RUN_STATUS_UNKNOWN,
                                        constants.ERROR_MESSAGE_NO_STATUS_RETURNED)

        return model_run

    def _send_email(self, model_run):
        """
        Send an email if the job has entered a non submitted state
        :param model_run: the run model
        :return:nothing
        """

        if model_run.status.name == constants.MODEL_RUN_STATUS_COMPLETED:

            msg = email_messages.COMPLETED_MESSAGE_TEMPLATE.format(
                name=model_run.name,
                description=model_run.description,
                url=self._config['model_run_summary_url_template'].format(model_run_id=model_run.id),
                users_name=model_run.user.name)
            subject = email_messages.COMPLETED_SUBJECT_TEMPLATE.format(name=model_run.name)

        elif model_run.status.name == constants.MODEL_RUN_STATUS_FAILED:

            msg = email_messages.FAILED_MESSAGE_TEMPLATE.format(
                name=model_run.name,
                description=model_run.description,
                url=self._config['model_run_summary_url_template'].format(model_run_id=model_run.id),
                users_name=model_run.user.name,
                error_message=model_run.error_message)
            subject = email_messages.FAILED_SUBJECT_TEMPLATE.format(name=model_run.name)

        elif model_run.status.name == constants.MODEL_RUN_STATUS_UNKNOWN:

            msg = email_messages.UNKNOWN_MESSAGE_TEMPLATE.format(
                name=model_run.name,
                description=model_run.description,
                url=self._config['model_run_summary_url_template'].format(model_run_id=model_run.id),
                users_name=model_run.user.name,
                error_message=model_run.error_message)
            subject = email_messages.UNKNOWN_SUBJECT_TEMPLATE.format(name=model_run.name)
        else:
            return

        self._email_service.send_email(
            self._config['email.from_address'],
            model_run.user.email,
            subject,
            msg)

    def _update_datasets(self, model_run, session):
        """
        Update all data sets for this model
        :param model_run: the model run to update
        :param session: a session
        :return:nothing
        """

        run_id = model_run.get_python_parameter_value(constants.JULES_PARAM_OUTPUT_RUN_ID)
        single_cell = not model_run.get_python_parameter_value(constants.JULES_PARAM_LATLON_REGION)
        selected_output_profile_names = model_run.get_parameter_values(constants.JULES_PARAM_OUTPUT_PROFILE_NAME)

        selected_output_periods = {}
        for var in model_run.get_parameter_values(constants.JULES_PARAM_OUTPUT_PERIOD):
            selected_output_periods[var.group_id] = var.get_value_as_python()

        dataset_type = session.query(DatasetType).filter(DatasetType.type == constants.DATASET_TYPE_COVERAGE).one()
        thredds_server = self._config['thredds.server_url'].rstrip("/")

        for selected_output_profile_name in selected_output_profile_names:
            filename = "{output_dir}/{run_id}.{profile_name}.ncml".format(
                run_id=run_id,
                profile_name=selected_output_profile_name.get_value_as_python(),
                output_dir=constants.OUTPUT_DIR)
            is_input = False

            profile_name = utils.convert_time_period_to_name(
                selected_output_periods[selected_output_profile_name.group_id])
            self._create_dataset(dataset_type, filename, is_input, single_cell, model_run, session, thredds_server,
                                 profile_name)

        input_locations = session \
            .query(DrivingDatasetLocation) \
            .filter(DrivingDatasetLocation.driving_dataset_id == model_run.driving_dataset_id) \
            .all()

        for input_location in input_locations:
            filename = input_location.base_url
            is_input = True
            self._create_dataset(input_location.dataset_type, filename, is_input, single_cell, model_run, session,
                                 thredds_server)

    def _create_dataset(self, dataset_type, filename, is_input, is_single_cell, model_run, session,
                        thredds_server, frequency=None):
        """
        Create a single dataset
        :param dataset_type: the dataset type
        :param filename: filename of the dataset
        :param is_input: true if this is an input dataset
        :param is_single_cell: Is a single cell dataset
        :param model_run: the model run
        :param session: the session
        :param thredds_server: url of the thredds server
        :param frequency: extra label to append to the name to indicate frequency
        :return:
        """
        dataset = Dataset()
        dataset.model_run_id = model_run.id
        dataset.dataset_type = dataset_type
        dataset.is_categorical = False
        dataset.is_input = is_input
        dataset.viewable_by_user_id = model_run.user.id
        dataset.wms_url = None
        dataset.is_single_cell = is_single_cell
        if not is_single_cell:
            dataset.wms_url = \
                "{thredds_server_url}/wms/model_runs/run{model_run_id}/" \
                "{filename}?service=WMS&version=1.3.0&request=GetCapabilities" \
                .format(
                thredds_server_url=thredds_server,
                model_run_id=model_run.id,
                filename=filename)
        dataset.netcdf_url = \
            "{thredds_server_url}/dodsC/model_runs/run{model_run_id}/{filename}" \
            .format(
            thredds_server_url=thredds_server,
            model_run_id=model_run.id,
            filename=filename)

        dap_client = self._dap_client_factory.get_dap_client(dataset.netcdf_url)
        if frequency:
            dataset.name = "{name} ({frequency})".format(name=dap_client.get_longname(), frequency=frequency)
        else:
            dataset.name = dap_client.get_longname()
        dataset.data_range_from, dataset.data_range_to = dap_client.get_data_range()
        session.add(dataset)

    def _check_total_allocation_and_alert(self):
        """
        Check the total storage use and send an alert email if it is too high
        :return: nothing
        """

        with self.readonly_scope() as session:
            if not SystemAlertEmail.check_email_needs_sending(SystemAlertEmail.GROUP_SPACE_FULL_ALERT, session):
                return

        storage_quota_in_gb, storage_total_used_in_gb, total_storage_percent_used = self._find_storage_use()

        if total_storage_percent_used >= constants.QUOTA_WARNING_LIMIT_PERCENT:
            self._send_alert_email(storage_quota_in_gb, storage_total_used_in_gb)

    def _send_alert_email(self, storage_quota_in_gb, storage_total_used_in_gb):
        """
        Send the alert email and records this in the database
        :param storage_quota_in_gb: the total storage quota
        :param storage_total_used_in_gb: the total space used
        :return: nothing
        """
        msg = email_messages.GROUP_SPACE_FULL_ALERT_MESSAGE.format(current_quota=storage_quota_in_gb,
                                                                   used_space=storage_total_used_in_gb)
        self._email_service.send_email(
            self._config['email.from_address'],
            self._config['email.admin_address'],
            email_messages.GROUP_SPACE_FULL_ALERT_SUBJECT,
            msg)
        with self.transaction_scope() as session:
            email = session.query(SystemAlertEmail) \
                .filter(SystemAlertEmail.code == SystemAlertEmail.GROUP_SPACE_FULL_ALERT) \
                .one()

            email.last_sent = datetime.now()

    def _find_storage_use(self):
        """
        Find the total storage use
        :return: tuple of quota, total used, percent used
        """

        with self.readonly_scope() as session:
            core_user = session.query(User).filter(User.username == constants.CORE_USERNAME).one()

        storage_total_used_in_gb = 0
        for user_id, status, storage_mb in self._model_run_service.get_storage_used():
            if storage_mb is not None:
                storage_total_used_in_gb += int(storage_mb)
        storage_total_used_in_gb = utils.convert_mb_to_gb_and_round(storage_total_used_in_gb)

        total_storage_percent_used = storage_total_used_in_gb / core_user.storage_quota_in_gb * 100.0

        return core_user.storage_quota_in_gb, storage_total_used_in_gb, total_storage_percent_used
