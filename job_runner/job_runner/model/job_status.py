"""
header
"""

from job_runner.utils import constants
from job_runner.services.job_service import ServiceError


class JobStatus(object):
    """
    A jobs status
    """

    def __init__(self, model_run_id):
        """
        Initiate the job status
        :param model_run_id: the model runs id
        :return:nothing
        """
        self.model_run_id = model_run_id
        self.status = ''
        self.error_message = ''

    def __json__(self):
        """
        How to represent this model as json
        :return: the json representation
        """
        return {
            'id': self.model_run_id,
            'status': self.status,
            'error_message': self.error_message}

    def check(self, job_service, bjobs_list):
        """
        Check the job status by usin gthe bjob output and log file
        :param job_service: the job service to use
        :param bjobs_list: the list of jobs on the system and their statuses
        :return:nothing
        """
        if not job_service.exists_run_dir(self.model_run_id):
            self.status = constants.MODEL_RUN_STATUS_SUBMIT_FAILED
            self.error_message = constants.ERROR_MESSAGE_NO_FOLDER
            return

        run_dir = job_service.get_run_dir(self.model_run_id)
        bsub_id = job_service.get_bsub_id(run_dir)
        if bsub_id is None:
            self.status = constants.MODEL_RUN_STATUS_SUBMIT_FAILED
            self.error_message = constants.ERROR_MESSAGE_NO_JOB_ID
            return

        if bsub_id in bjobs_list:
            self.status = bjobs_list[bsub_id]
            return

        try:
            log_file_parser = job_service.get_output_log_result(run_dir)
            self.status = log_file_parser.status
            if self.status == constants.MODEL_RUN_STATUS_FAILED:
                self.error_message = log_file_parser.error_message
        except ServiceError, ex:
            self.status = constants.MODEL_RUN_STATUS_FAILED
            self.error_message = ex.message
