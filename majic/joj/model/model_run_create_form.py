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

from joj.utils import constants
from formencode import Schema, validators


class ModelRunCreateFirst(Schema):
    """Used to validate data for the model run create form"""

    allow_extra_fields = True
    filter_extra_fields = True

    name = validators.String(not_empty=True, max=constants.DB_STRING_SIZE)
    science_configuration = validators.Int(not_empty=True)
    description = validators.String(max=constants.DB_LONG_STRING_SIZE)
