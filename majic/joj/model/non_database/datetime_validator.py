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
import datetime
from joj.utils import constants


class DatetimeValidator(object):
    """
    Validator for time and date strings
    """

    def __init__(self, errors):
        """
        Initialise
        :param errors: the errors dictionary to add to if there is an error
        :return: nothing
        """
        self._errors = errors

    def get_valid_datetime(self, key, values):
        """
        Return a valid date
        if there is a validation error add it to errors dictionary and return none
        :param key: the  key in values to get the date value
        :param values: values dictionary
        :return: datetime
        """
        if key not in values or values[key] == '':
            self._errors[key] = 'Please enter a date'
        else:
            date_str = values[key]
            try:
                return datetime.datetime.strptime(date_str, constants.USER_UPLOAD_DATE_FORMAT)
            except ValueError:
                pass

            try:
                return datetime.datetime.strptime(date_str, constants.USER_UPLOAD_DATE_FORMAT + ':%S')
            except ValueError:
                self._errors[key] = 'Enter date as YYYY-MM-DD HH:MM'
            return None
