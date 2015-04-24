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
from sync.clients.apache_client import ApacheClient, ApacheClientError
from sync.utils.constants import CONFIG_APACHE_DATA_PATH, CONFIG_APACHE_SECTION
from tests.test_mother import ConfigMother


class TestApacheClient(unittest.TestCase):

    def test_GIVEN_root_folder_WHEN_read_THEN_return_list_of_files(self):
        config = ConfigMother.test_configuration()
        client = ApacheClient(config)

        result = client.get_contents(config.get(CONFIG_APACHE_DATA_PATH, CONFIG_APACHE_SECTION))

        assert_that(result, has_length(greater_than(0)))
        assert_that(result, is_not(has_item('Parent Directory')))

    def test_GIVEN_file_WHEN_download_THEN_file_saved_to_filehandle(self):
        config = ConfigMother.test_configuration()
        client = ApacheClient(config)
        filehandle = Mock()
        url = "http://localhost/public/jules_bd/data/WATCH_2D/driving/LWdown_WFD/LWdown_WFD_190101.nc"

        client.download_file(url, filehandle)

        assert_that(filehandle.write.called, is_(True), "Check that something is written to the file handle")

    def test_GIVEN_server_not_available_WHEN_download_THEN_exception(self):
        config = ConfigMother.test_configuration()
        client = ApacheClient(config)
        filehandle = Mock()
        url = "http://rubbish.rubbish"

        assert_that(calling(client.download_file).with_args(url, filehandle),
                    raises(ApacheClientError, "There is a connection error when "))

    def test_GIVEN_server_hit_timeout_WHEN_download_THEN_exception(self):
        config = ConfigMother.test_configuration_with_values(apache_timeout="0.00001")
        client = ApacheClient(config)
        filehandle = Mock()
        url = "http://localhost/public/jules_bd/data/WATCH_2D/driving/LWdown_WFD/LWdown_WFD_190101.nc"

        assert_that(calling(client.download_file).with_args(url, filehandle),
                    raises(ApacheClientError, "Timeout when contacting "))


if __name__ == '__main__':
    unittest.main()
