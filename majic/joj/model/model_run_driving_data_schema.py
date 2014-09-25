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

from formencode import Schema, validators
from joj.utils import constants


class ModelRunDrivingDataSchema(Schema):
    """
    Validates data from the driving data page
    """
    allow_extra_fields = True
    filter_extra_fields = False
    driving_dataset = validators.Int(not_empty=True)
    lat = validators.Number(if_missing=None, not_empty=True)
    lon = validators.Number(if_missing=None, not_empty=True)
    dt_start = validators.String(if_missing=None, not_empty=True, max=constants.DB_STRING_SIZE)
    dt_end = validators.String(if_missing=None, not_empty=True, max=constants.DB_STRING_SIZE)
