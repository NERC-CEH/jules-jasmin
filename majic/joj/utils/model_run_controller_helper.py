"""
# header
"""
from pylons import url
from joj.lib.base import redirect
from joj.lib import helpers
from joj.utils import constants, utils


class ModelRunControllerHelper(object):
    """
    Helper for general functions in the model run controller
    """

    def __init__(self, user_service, model_run_service):
        """
        Create a model run controller helper
        :param user_service: the user service
        :param model_run_service: the model run service
        :return:nothing
        """
        self._user_service = user_service
        self._model_run_service = model_run_service

    def check_model_get(self, current_user, action):
        """
        Check that the user can create a new model run
        :param current_user: the current user
        :param action; the name of the action for this page
        :return: the model run being created
        """
        total = 0
        for user_id, status_name, storage_in_mb in self._model_run_service.get_storage_used(current_user):
            if status_name != constants.MODEL_RUN_STATUS_PUBLISHED:
                total += storage_in_mb

        total_in_gb = utils.convert_mb_to_gb_and_round(total)

        storage_percent_used = round(total_in_gb / current_user.storage_quota_in_gb * 100.0, 0)

        if storage_percent_used >= constants.QUOTA_ABSOLUTE_LIMIT_PERCENT:
            helpers.error_flash(constants.ERROR_MESSAGE_QUOTA_EXCEEDED)
            redirect(url(controller="model_run", action="index"))

        self._user_service.set_current_model_run_creation_action(current_user, action)