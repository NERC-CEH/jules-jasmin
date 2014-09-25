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
import formencode

__author__ = 'Chirag Mistry (Tessella)'


class UpdateUserForm(formencode.Schema):
    """
    Schema used to validate update users form
    """
    allow_extra_fields = True
    filter_extra_fields = False

    first_name = formencode.validators.String(not_empty=True, max=50)
    last_name = formencode.validators.String(not_empty=True, max=50)
    email = formencode.validators.Email(not_empty=True, max=255)
    is_admin = formencode.validators.Bool()
    storage_quota = formencode.validators.Int(not_empty=True, min=1)


class CreateUserForm(UpdateUserForm):
    """Used to validate data from the Create New User page"""

    allow_extra_fields = False
    filter_extra_fields = True

    user_name = formencode.validators.String(not_empty=True)