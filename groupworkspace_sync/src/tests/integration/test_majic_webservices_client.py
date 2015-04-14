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

from src.sync.clients.majic_web_service_client import MajicWebserviceClient, WebserviceClientError
from tests.mother import ConfigMother


class TestMajicWebservicesClient(unittest.TestCase):

    def test_GIVEN_majic_is_down_WHEN_get_file_properties_THEN_exception_thrown(self):
        config = ConfigMother.incorrect_webservice_configured()
        client = MajicWebserviceClient(config)

        assert_that(
            calling(client.get_properties_list),
            raises(WebserviceClientError, "Can not contact Majic Web Service"))



if __name__ == '__main__':
    unittest.main()
