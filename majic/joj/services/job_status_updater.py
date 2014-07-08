"""
header
"""

import logging
from joj.services.model_run_service import ModelRunService
from joj.services.general import DatabaseService
from joj.model import ModelRun, ModelRunStatus, Session
from joj.utils import constants
from joj.utils.utils import KeyNotFound, find_by_id_in_dict


log = logging.getLogger(__name__)


class JobStatusUpdaterService(DatabaseService):
    """
    Service to update the job status in the database based on the status returned by the job runner
    """

    def __init__(self, job_runner_client, session=Session, model_run_service=ModelRunService()):
        """
        Initiate
        :param session: the session to use
        :param model_run_service: the model run service
        :param job_runner_client: the job runner client
        :return:npthing
        """
        super(JobStatusUpdaterService, self).__init__(session)
        self._job_runner_client = job_runner_client
        self._model_run_service = model_run_service

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
            self._update_model_run_status(job_statuses, model_id)

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
            model_ids = [model_run.id for model_run in model_runs]
        return model_ids

    def _update_model_run_status(self, job_statuses, model_id):
        """
        Find the new status and update it for a model
        :param job_statuses: a list of new job statuses
        :param model_id: the model id
        :return:nothing
        """
        with self.transaction_scope() as session:
            model_run = session.query(ModelRun) \
                .filter(ModelRun.id == model_id) \
                .one()

            try:
                job_status = find_by_id_in_dict(job_statuses, model_run.id)
                model_run.change_status(session, job_status['status'], job_status['error_message'])
            except KeyNotFound:
                log.error("No status returned from job runner for model run %s", model_id)
                model_run.change_status(session, constants.MODEL_RUN_STATUS_UNKNOWN,
                                        constants.ERROR_MESSAGE_NO_STATUS_RETURNED)
