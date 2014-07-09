"""
header
"""

import logging
from pylons import config, url
from sqlalchemy.orm import subqueryload
from joj.services.model_run_service import ModelRunService
from joj.services.general import DatabaseService
from joj.services.email_service import EmailService
from joj.model import ModelRun, ModelRunStatus, Session
from joj.utils import constants
from joj.utils.utils import KeyNotFound, find_by_id_in_dict


log = logging.getLogger(__name__)


class JobStatusUpdaterService(DatabaseService):
    """
    Service to update the job status in the database based on the status returned by the job runner
    """

    COMPLETED_SUBJECT_TEMPLATE = "Majic: {name} has completed"
    COMPLETED_MESSAGE_TEMPLATE = \
        """Hi {users_name},

           Majic has successfully finished your model run.

           Name: {name}
           Description: {description}
           Link: {url}

        Regards,

        Majic
        """

    FAILED_SUBJECT_TEMPLATE = "Majic: {name} has encountered an error"
    FAILED_MESSAGE_TEMPLATE = \
        """Hi {users_name},

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
        """Hi {users_name},

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
            session=Session,
            model_run_service=ModelRunService(),
            email_service=EmailService()):
        """
        Initiate
        :param session: the session to use
        :param model_run_service: the model run service
        :param job_runner_client: the job runner client
        :param email_service: the email service to use
        :return:nothing
        """
        super(JobStatusUpdaterService, self).__init__(session)
        self._job_runner_client = job_runner_client
        self._model_run_service = model_run_service
        self._email_service = email_service

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
                url=url(controller='model_run', action='summary', id=model_run.id),
                users_name=model_run.user.name)
            subject = self.COMPLETED_SUBJECT_TEMPLATE.format(name=model_run.name)

        elif model_run.status.name == constants.MODEL_RUN_STATUS_FAILED:

            msg = self.FAILED_MESSAGE_TEMPLATE.format(
                name=model_run.name,
                description=model_run.description,
                url=url(controller='model_run', action='summary', id=model_run.id),
                users_name=model_run.user.name,
                error_message=model_run.error_message)
            subject = self.FAILED_SUBJECT_TEMPLATE.format(name=model_run.name)

        elif model_run.status.name == constants.MODEL_RUN_STATUS_UNKNOWN:

            msg = self.UNKNOWN_MESSAGE_TEMPLATE.format(
                name=model_run.name,
                description=model_run.description,
                url=url(controller='model_run', action='summary', id=model_run.id),
                users_name=model_run.user.name,
                error_message=model_run.error_message)
            subject = self.UNKNOWN_SUBJECT_TEMPLATE.format(name=model_run.name)
        else:
            return

        self._email_service.send_email(
            config['email.from_address'],
            model_run.user.email,
            subject,
            msg)
