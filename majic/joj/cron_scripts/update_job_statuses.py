"""
header
"""
import logging
from paste.deploy import loadapp
import os
import sys

from joj.services.job_status_updater import JobStatusUpdaterService
from joj import model
from joj.services.job_runner_client import JobRunnerClient
from joj.lib.wmc_util import set_http_openers


log = logging.getLogger(__name__)
here_dir = os.path.dirname(os.path.abspath(__file__))
conf_dir = os.path.dirname(os.path.dirname(here_dir))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) is not 2 or sys.argv[1] == '-h':
        print "Usage: update_job_statueses <config filename>"
        print "       updates the job statuses in the database from the jobs service"
        print "       config filename: filename of the configuration file e.g. development.ini"
        exit()

    log.debug("setup")
    wsgiapp = loadapp('config:' + sys.argv[1], relative_to=conf_dir)
    config = wsgiapp.config
    model.initialise_session(config)
    set_http_openers(config)

    job_runner_client = JobRunnerClient(config)
    job_status_updater = JobStatusUpdaterService(job_runner_client, config)

    try:
        log.info("Getting and setting statuses")
        job_status_updater.update()
        log.info("Statuses updated")
    except Exception, ex:
        log.exception("Cron job throw an exception: %s" % ex.message)
        exit(-1)
