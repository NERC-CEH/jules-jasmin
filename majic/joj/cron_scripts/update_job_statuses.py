"""
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
"""
import logging
from paste.deploy import loadapp
import os
import sys

from joj.services.job_status_updater import JobStatusUpdaterService
from joj import model
from joj.services.job_runner_client import JobRunnerClient
from joj.lib import wmc_util


log = logging.getLogger(__name__)
here_dir = os.path.dirname(os.path.abspath(__file__))
conf_dir = os.path.dirname(os.path.dirname(here_dir))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) is not 2 or sys.argv[1] == '-h':
        print "Usage: update_job_statuses <config filename>"
        print "       updates the job statuses in the database from the jobs service"
        print "       config filename: filename of the configuration file e.g. development.ini"
        exit()

    log.debug("setup")
    wsgiapp = loadapp('config:' + sys.argv[1], relative_to=conf_dir)
    config = wsgiapp.config
    model.initialise_session(config)
    wmc_util.set_http_openers(config)

    job_runner_client = JobRunnerClient(config)
    job_status_updater = JobStatusUpdaterService(job_runner_client, config)

    try:
        log.info("Getting and setting statuses")
        job_status_updater.update()
        log.info("Statuses updated")
    except Exception, ex:
        log.exception("Cron job throw an exception: %s" % ex.message)
        exit(-1)
