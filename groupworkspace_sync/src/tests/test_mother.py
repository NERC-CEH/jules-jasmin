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
import ConfigParser
import os

from src.sync.utils.constants import CONFIG_URL, CONFIG_WS_SECTION
from sync.utils.config_accessor import ConfigAccessor


class ConfigMother(object):
    """
    Test data provider for configuration objects
    """

    @staticmethod
    def raw_test_configuration():
        """
        Read the test configuration
        :return: the test configuration
        """
        config = ConfigParser.SafeConfigParser()
        dir = os.path.dirname(os.path.realpath(__file__))
        test_config_file = os.path.join(dir, os.pardir, os.pardir, "test.ini")
        config.read(test_config_file)
        return config

    @staticmethod
    def incorrect_webservice_configured():
        """
        :return: the test.ini configuration but with an incorrect web service address in as a ConfigAccessor
        """
        config = ConfigMother.raw_test_configuration()
        config.set(CONFIG_WS_SECTION, CONFIG_URL, "https://rubbish")

        return ConfigAccessor(config)

    @staticmethod
    def test_configuration():
        """
        load the test configuration file
        :return: a safe config parser with the test.ini file loaded into it as a ConfigAccessor
        """
        return ConfigAccessor(ConfigMother.raw_test_configuration())