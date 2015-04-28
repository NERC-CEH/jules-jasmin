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

import unittest

from hamcrest import *
from mock import Mock

from src.sync.clients.majic_web_service_client import MajicWebserviceClient, WebserviceClientError
from tests.test_mother import ConfigMother
from sync.synchroniser import Synchroniser


class TestMajicWebservicesClient(unittest.TestCase):

    def test_GIVEN_majic_client_throws_a_known_exception_WHEN_synch_THEN_error_code_returned(self):
        error_message = "error_message"
        config = ConfigMother.incorrect_webservice_configured()

        client = Mock(MajicWebserviceClient)
        client.get_properties_list_with_filtered_users = Mock(side_effect=WebserviceClientError(error_message))
        sync = Synchroniser(config, client)

        result = sync.synchronise()

        assert_that(result, is_not(0), "error code")

    def test_GIVEN_majic_client_throws_an_unknown_exception_WHEN_synch_THEN_error_code_returned(self):
        error_message = "error_message"
        config = ConfigMother.incorrect_webservice_configured()

        client = Mock(MajicWebserviceClient)
        client.get_properties_list_with_filtered_users = Mock(side_effect=Exception(error_message))
        sync = Synchroniser(config, client)

        result = sync.synchronise()

        assert_that(result, is_not(0), "error code")


if __name__ == '__main__':
    unittest.main()
