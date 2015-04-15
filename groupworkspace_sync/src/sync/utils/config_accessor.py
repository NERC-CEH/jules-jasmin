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
from ConfigParser import NoSectionError

# sentinel to mark the difference between passing None and not passing anything
sentinel = object()


class ConfigAccessor(object):
    """
    Access a configuration object with default values and section setting
    """

    def __init__(self, config):
        self._config = config
        self._section = None

    def _check_section_exists(self, section):
        """
        Check that a section exists in the config
        :param section: section to check for
        :return: nothing
        :raises NoSectionError: when section does not exist
        """
        if not self._config.has_section(section):
            raise NoSectionError(section)

    def set_section(self, section):
        """
        Set the default section to access
        :param section: the section to set
        :return: nothing
        :raises: NoSectionError is the section doesn't exist
        """

        self._check_section_exists(section)
        self._section = section

    def get(self, option, section=sentinel, default=sentinel):
        """
        Returns the value from the config specified by the section and option
        :param option: the name of the option
        :param section: the section name, default is to use the one set in set_section or raise NoSectionError
        :param default: the default value to return if the option is not set. Default raises NoOptionError
            if value not found
        :return: value of the option in the section
        :raises NoOptionError: when option is not found and there is no default
        :raises NoSectionError: if a section is specified but it can not be found or section is not specified
                  and set_section has not been called
        """
        section_to_use = section
        if section is sentinel:
            section_to_use = self._section
        self._check_section_exists(section_to_use)

        if default is not sentinel:
            if not self._config.has_option(section_to_use, option):
                return default
        return self._config.get(section_to_use, option)
