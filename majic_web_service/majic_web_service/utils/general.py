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
from majic_web_service.utils.constants import DATA_FORMAT_WITH_TZ


def convert_time_to_standard_string(datetime_to_convert):
    """
    Convert a datetime into a standard format string
    :param datetime_to_convert: the date time to convert
    :return: the converted string, none return an empty string
    """
    if datetime_to_convert is None:
        return ""
    else:
        return datetime_to_convert.strftime(DATA_FORMAT_WITH_TZ)
