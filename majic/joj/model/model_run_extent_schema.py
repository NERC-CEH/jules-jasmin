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


class ModelRunExtentSchema(Schema):
    """Used to validate data for the model run extents page"""

    allow_extra_fields = True
    filter_extra_fields = False
    lat = validators.Number(if_missing=None, not_empty=True)
    lon = validators.Number(if_missing=None, not_empty=True)
    lat_n = validators.Number(if_missing=None, not_empty=True)
    lat_s = validators.Number(if_missing=None, not_empty=True)
    lon_e = validators.Number(if_missing=None, not_empty=True)
    lon_w = validators.Number(if_missing=None, not_empty=True)
    start_date = validators.DateConverter(not_empty=True, month_style='yyyy/mm/dd')
    end_date = validators.DateConverter(not_empty=True, month_style='yyyy/mm/dd')
