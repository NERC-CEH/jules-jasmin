"""
header
"""
import logging

from joj.services.job_status_updater import JobStatusUpdaterService
from joj import model
from paste.deploy import loadapp
import os
from joj.services.job_runner_client import JobRunnerClient

log = logging.getLogger(__name__)
here_dir = os.path.dirname(os.path.abspath(__file__))
conf_dir = os.path.dirname(os.path.dirname(here_dir))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    logging.debug("setup")
    wsgiapp = loadapp('config:development.ini', relative_to=conf_dir)
    config = wsgiapp.config
    model.initialise_session(config)

    job_runner_client = JobRunnerClient(config)
    job_status_updater = JobStatusUpdaterService(job_runner_client)

    try:
        log.info("Getting and setting statuses")
        job_status_updater.update()
        log.info("Statuses updated")
    except Exception, ex:
        log.error("Cron job throw an exception: %s" % ex.message)
