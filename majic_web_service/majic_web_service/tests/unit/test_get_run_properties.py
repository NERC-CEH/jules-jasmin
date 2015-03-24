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
from hamcrest import *
from mock import *
from webob.exc import HTTPInternalServerError

from majic_web_service.controllers.run_property_controller import RunPropertyController
from majic_web_service.services.run_property_service import RunPropertyService, ServiceException
from majic_web_service.tests import TestController


class TestDisplayOptionsConfig(TestController):

    def test_GIVEN_database_is_not_up_WHEN_request_run_properties_THEN_return_fail(self):
        runs_properties_service = Mock(RunPropertyService)
        error_message = "Database is not available"
        runs_properties_service.list = Mock(side_effect=ServiceException(error_message))
        runs_properties = RunPropertyController(runs_properties_service)

        assert_that(calling(runs_properties.list), raises(HTTPInternalServerError, error_message))


    #COPY TO FUNCTIONAL TEST
    # def test_GIVEN_nothing_WHEN_duplicate_file_THEN_error(self):
    #     response = self.app.get(
    #         url(controller='job_file', action='duplicate'),
    #         expect_errors=True
    #     )
    #
    #     assert_that(response.status_code, is_(400), "invalid r