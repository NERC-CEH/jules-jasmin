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

from src.sync.utils.constants import CONFIG_URL, CONFIG_WS_SECTION, CONFIG_DATA_PATH, CONFIG_DATA_SECTION, \
    CONFIG_DATA_NOBODY_USERNAME, JSON_MODEL_RUN_ID, JSON_USER_NAME, JSON_IS_PUBLISHED, JSON_IS_PUBLIC
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

    @staticmethod
    def test_configuration_with_values(data_path=None, nobody_username=None):
        """
        load the test configuration file but override the data path
        :param data_path: data path to set, defualt use standard
        :param nobody_username: name for the nobodyuser, default use standard
        :return: a safe config parser with the test.ini file loaded into it as a ConfigAccessor
        """
        config = ConfigMother.raw_test_configuration()
        if data_path is not None:
            config.set(CONFIG_DATA_SECTION, CONFIG_DATA_PATH, data_path)
        if nobody_username is not None:
            config.set(CONFIG_DATA_SECTION, CONFIG_DATA_NOBODY_USERNAME, nobody_username)
        return ConfigAccessor(config)


class RunModelPropertiesMother(object):
    """
    Create file
    """

    @staticmethod
    def create_model_run_properties(run_ids, owner="model_owner", published=False, public=False):
        """
        Create a list of run model properties
        :param run_ids: list fo ids to use
        :param owner: the owner for them
        :param published: whether they are published
        :param public: true if public
        :return: list of dictionaries as if it came from the web service
        """
        return [{JSON_MODEL_RUN_ID: run_id,
                 JSON_USER_NAME: owner,
                 JSON_IS_PUBLISHED: published,
                 JSON_IS_PUBLIC: public} for run_id in run_ids]

