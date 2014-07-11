"""
# header
"""

import logging
from sqlalchemy.orm import subqueryload
from joj.services.model_run_service import ModelRunService
from joj.services.general import DatabaseService
from joj.services.email_service import EmailService
from joj.model import ModelRun, ModelRunStatus, Session, Dataset, DatasetType, DrivingDatasetLocation
from joj.utils import constants
from joj.utils.utils import KeyNotFound, find_by_id_in_dict
from joj.services.dap_client_factory import DapClientFactory

log = logging.getLogger(__name__)


class JobStatusUpdaterService(DatabaseService):
    """
    Service to update the job status in the database based on the status returned by the job runner
    """

    COMPLETED_SUBJECT_TEMPLATE = "Majic: {name} has completed"
    COMPLETED_MESSAGE_TEMPLATE = \
        """
Hi {users_name},

Majic has successfully finished your model run.

   Name: {name}
   Description: {description}
   Link: {url}

Regards,

Majic
"""

    FAILED_SUBJECT_TEMPLATE = "Majic: {name} has encountered an error"
    FAILED_MESSAGE_TEMPLATE = \
        """
Hi {users_name},

Majic has encountered an error when running your model run.

   Name: {name}
   Description: {description}
   Link: {url}
   Error: {error_message}

Regards,

Majic
"""

    UNKNOWN_SUBJECT_TEMPLATE = "Majic: {name} has encountered an unexpected problem"
    UNKNOWN_MESSAGE_TEMPLATE = \
        """
Hi {users_name},

Majic has encountered an unexpected problem when running your model run.

   Name: {name}
   Description: {description}
   Link: {url}
   Unknown problem: {error_message}

Regards,

Majic
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
            run_model = self._update_model_run_status(job_statuses, model_id)
            self._send_email(run_model)

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

            msg = self.COMPLETED_MESSAGE_TEMPLATE.format(
                name=model_run.name,
                description=model_run.description,
                url=self._config['model_run_summary_url_template'].format(model_run_id=model_run.id),
                users_name=model_run.user.name)
            subject = self.COMPLETED_SUBJECT_TEMPLATE.format(name=model_run.name)

        elif model_run.status.name == constants.MODEL_RUN_STATUS_FAILED:

            msg = self.FAILED_MESSAGE_TEMPLATE.format(
                name=model_run.name,
                description=model_run.description,
                url=self._config['model_run_summary_url_template'].format(model_run_id=model_run.id),
                users_name=model_run.user.name,
                error_message=model_run.error_message)
            subject = self.FAILED_SUBJECT_TEMPLATE.format(name=model_run.name)

        elif model_run.status.name == constants.MODEL_RUN_STATUS_UNKNOWN:

            msg = self.UNKNOWN_MESSAGE_TEMPLATE.format(
                name=model_run.name,
                description=model_run.description,
                url=self._config['model_run_summary_url_template'].format(model_run_id=model_run.id),
                users_name=model_run.user.name,
                error_message=model_run.error_message)
            subject = self.UNKNOWN_SUBJECT_TEMPLATE.format(name=model_run.name)
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
        selected_output_profile_names = model_run.get_parameter_values(constants.JULES_PARAM_OUTPUT_PROFILE_NAME)
        selected_output_variables = {}
        for var in model_run.get_parameter_values(constants.JULES_PARAM_OUTPUT_VAR):
            selected_output_variables[var.group_id] = var.get_value_as_python()

        dataset_type = session.query(DatasetType).filter(DatasetType.type == constants.DATASET_TYPE_COVERAGE).one()
        thredds_server = self._config['thredds.server_url'].rstrip("/")

        for selected_output_profile_name in selected_output_profile_names:
            filename = "{output_dir}/{run_id}.{profile_name}.nc".format(
                run_id=run_id,
                profile_name=selected_output_profile_name.get_value_as_python(),
                output_dir=constants.OUTPUT_DIR)
            is_input = False

            self._create_dataset(dataset_type, filename, is_input, model_run, session, thredds_server)

        input_locations = session \
            .query(DrivingDatasetLocation) \
            .filter(DrivingDatasetLocation.driving_dataset_id == model_run.driving_dataset_id) \
            .all()

        for input_location in input_locations:
            filename = input_location.base_url
            is_input = True
            self._create_dataset(dataset_type, filename, is_input, model_run, session, thredds_server)

    def _create_dataset(self, dataset_type, filename, is_input, model_run, session, thredds_server):
        """
        Create a single dataset
        :param dataset_type: the dataset type
        :param filename: filename of the dataset
        :param is_input: true if this is an input dataset
        :param model_run: the model run
        :param session: the session
        :param thredds_server: url of the thredds server
        :return:
        """
        dataset = Dataset()
        dataset.model_run_id = model_run.id
        dataset.dataset_type = dataset_type
        dataset.is_categorical = False
        dataset.is_input = is_input
        dataset.viewable_by_user_id = model_run.user.id
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
        dataset.name = dap_client.get_longname()
        dataset.data_range_from, dataset.data_range_to = dap_client.get_data_range()
        session.add(dataset)
