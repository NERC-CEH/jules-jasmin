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
from formencode import Invalid


from hamcrest import *
from job_runner.tests import TestController
from job_runner.utils import constants
from job_runner.model.bjobs_parser import BjobsParser

header = "JOBID   USER    STAT  QUEUE      FROM_HOST   EXEC_HOST   JOB_NAME   SUBMIT_TIME"


class TestJulesLogFileParser(TestController):

    def setUp(self):
        self.lines = []
        self.parser = BjobsParser(self.lines)


    def test_GIVEN_no_output_WHEN_parse_THEN_return_empty_list(self):

        result = self.parser.parse()

        assert_that(len(result), is_(0), "No jobs in dictionary")

    def test_GIVEN_no_jobs_output_WHEN_parse_THEN_return_empty_list(self):
        self.lines.append('No unfinished job found')

        result = self.parser.parse()

        assert_that(len(result), is_(0), "No jobs in dictionary")

    def test_GIVEN_one_running_job_in_list_WHEN_parse_THEN_return_that_job_as_running(self):
        self.lines.append(header)
        self.lines.append('402753  jholt01 RUN  lotus      jules-bd1-d 8*host041.j *> out.log Jul  2 12:13')

        result = self.parser.parse()

        assert_that(len(result), is_(1), "Jobs in dictionary")
        assert_that(result[402753], is_(constants.MODEL_RUN_STATUS_RUNNING), "job status")

    def test_GIVEN_one_pending_job_in_list_WHEN_parse_THEN_return_that_job_as_pending(self):
        self.lines.append(header)
        self.lines.append('402753  jholt01 PEND lotus      jules-bd1-d 8*host041.j *> out.log Jul  2 12:13')

        result = self.parser.parse()

        assert_that(len(result), is_(1), "Jobs in dictionary")
        assert_that(result[402753], is_(constants.MODEL_RUN_STATUS_PENDING), "job status")

    def test_GIVEN_one_unknown_job_in_list_WHEN_parse_THEN_return_that_job_as_pending(self):
        self.lines.append(header)
        self.lines.append('402753  jholt01 BLAH lotus      jules-bd1-d 8*host041.j *> out.log Jul  2 12:13')

        result = self.parser.parse()

        assert_that(len(result), is_(1), "Jobs in dictionary")
        assert_that(result[402753], is_(constants.MODEL_RUN_STATUS_UNKNOWN), "job status")

    def test_GIVEN_multiple_jobs_in_list_WHEN_parse_THEN_return_that_jobs(self):
        self.lines.append(header)
        self.lines.append('402753  jholt01 BLAH lotus      jules-bd1-d 8*host041.j *> out.log Jul  2 12:13')
        self.lines.append('402754  jholt01 PEND lotus      jules-bd1-d 8*host041.j *> out.log Jul  2 12:13')
        self.lines.append('                                jules-bd1-d 16*host042.j *> out.lo Jul  2 12:13')
        self.lines.append('402755  jholt01 RUN  lotus      jules-bd1-d 8*host041.j *> out.log Jul  2 12:13')

        result = self.parser.parse()

        assert_that(len(result), is_(3), "Jobs in dictionary")
        assert_that(result[402753], is_(constants.MODEL_RUN_STATUS_UNKNOWN), "job status")
        assert_that(result[402754], is_(constants.MODEL_RUN_STATUS_PENDING), "job status")
        assert_that(result[402755], is_(constants.MODEL_RUN_STATUS_RUNNING), "job status")
