"""Setup the majic_web_service application"""
import logging
import os

from majic_web_service.config.environment import load_environment
from majic_web_service.model import ModelRunStatus, session_scope
from majic_web_service.model.meta import Session, Base
from majic_web_service.utils import constants

log = logging.getLogger(__name__)


# noinspection PyUnusedLocal
def setup_app(command, conf, vars):
    """Place any commands to setup majic_web_service here
    :param conf: configuration for the setup
    :param vars: variables
    :param command: commands
    """

    # Don't reload the app if it was loaded under the testing environment
    load_environment(conf.global_conf, conf.local_conf)

    filename = os.path.split(conf.filename)[-1]
    if filename == 'test.ini':
        log.debug("Creating database")
        # Recreate the tables
        Base.metadata.drop_all(bind=Session.bind)
        Base.metadata.create_all(bind=Session.bind)

        with session_scope(Session) as session:
            stat_created = ModelRunStatus(constants.MODEL_RUN_STATUS_CREATED)
            stat_submitted = ModelRunStatus(constants.MODEL_RUN_STATUS_SUBMITTED)
            stat_pending = ModelRunStatus(constants.MODEL_RUN_STATUS_PENDING)
            stat_running = ModelRunStatus(constants.MODEL_RUN_STATUS_RUNNING)
            stat_completed = ModelRunStatus(constants.MODEL_RUN_STATUS_COMPLETED)
            stat_published = ModelRunStatus(constants.MODEL_RUN_STATUS_PUBLISHED)
            stat_public = ModelRunStatus(constants.MODEL_RUN_STATUS_PUBLIC)
            stat_failed = ModelRunStatus(constants.MODEL_RUN_STATUS_FAILED)
            stat_submit_failed = ModelRunStatus(constants.MODEL_RUN_STATUS_SUBMIT_FAILED)
            stat_unknown = ModelRunStatus(constants.MODEL_RUN_STATUS_UNKNOWN)

            map(session.add, [stat_created, stat_submitted, stat_pending, stat_running, stat_completed, stat_published,
                              stat_public, stat_failed, stat_submit_failed, stat_unknown])
