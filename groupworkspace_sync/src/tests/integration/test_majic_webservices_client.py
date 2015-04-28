"""
#    Majic
#    Copyright (C) 2015  CEH
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
import getpass

import unittest

from hamcrest import *
from mock import Mock

from src.sync.clients.majic_web_service_client import MajicWebserviceClient, WebserviceClientError
from tests.test_mother import ConfigMother, RunModelPropertiesMother
from utils.constants import JSON_MODEL_RUNS


class TestMajicWebservicesClient(unittest.TestCase):

    def test_GIVEN_majic_is_down_WHEN_get_file_properties_THEN_exception_thrown(self):
        config = ConfigMother.incorrect_webservice_configured()
        client = MajicWebserviceClient(config)

        assert_that(
            calling(client.get_properties_list),
            raises(WebserviceClientError, "There is a connection error when contacting the Majic Web Service"))

    def test_GIVEN_majic_is_up_WHEN_get_file_properties_THEN_data_returned(self):
        config = ConfigMother.test_configuration()
        client = MajicWebserviceClient(config)

        try:
            result = client.get_properties_list()
        except WebserviceClientError as ex:
            if ex.message.startswith("There is a connection error when contacting the Majic Web Service"):
                raise self.skipTest("Connection error talking with Majic Web service")
            else:
                raise ex

        assert_that(result, is_not(None))

    def test_GIVEN_majic_timesout_WHEN_get_file_properties_THEN_exception_thrown(self):
        config = ConfigMother.test_configuration_with_values(majic_ws_timeout="0.002")
        client = MajicWebserviceClient(config)

        assert_that(
            calling(client.get_properties_list),
            raises(WebserviceClientError, "Timeout when contacting the Majic Web Service"))


    def test_GIVEN_blank_user_in_list_WHEN_get_filtered_THEN_blank_is_replaced_by_default_user(self):
        nobody_username = "nobody"
        config = ConfigMother.test_configuration_with_values(nobody_username=nobody_username)
        client = MajicWebserviceClient(config)
        client.get_properties_list = Mock(return_value={
            JSON_MODEL_RUNS: RunModelPropertiesMother.create_model_run_properties([1], owner="")})

        results = client.get_properties_list_with_filtered_users()

        assert_that(results, is_(RunModelPropertiesMother.create_model_run_properties([1], owner=nobody_username)))

    def test_GIVEN_non_existant_user_in_list_WHEN_get_filtered_THEN_user_is_replaced_by_default_user(self):
        nobody_username = "nobody"
        config = ConfigMother.test_configuration_with_values(nobody_username=nobody_username)
        client = MajicWebserviceClient(config)
        client.get_properties_list = Mock(return_value={
            JSON_MODEL_RUNS: RunModelPropertiesMother.create_model_run_properties([1], owner="non_existant_user")})

        results = client.get_properties_list_with_filtered_users()

        assert_that(results, is_(RunModelPropertiesMother.create_model_run_properties([1], owner=nobody_username)))

    def test_GIVEN_user_in_list_WHEN_get_filtered_THEN_user_kept(self):
        expected_user = getpass.getuser()
        nobody_username = "nobody"
        config = ConfigMother.test_configuration_with_values(nobody_username=nobody_username)
        client = MajicWebserviceClient(config)
        client.get_properties_list = Mock(return_value={
            JSON_MODEL_RUNS: RunModelPropertiesMother.create_model_run_properties([1], owner=expected_user)})

        results = client.get_properties_list_with_filtered_users()

        assert_that(results, is_(RunModelPropertiesMother.create_model_run_properties([1], owner=expected_user)))


if __name__ == '__main__':
    unittest.main()
