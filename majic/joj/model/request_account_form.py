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


class RequestAccountForm(Schema):
    """
    Validates data from the 'request account' form
    """

    allow_extra_fields = True
    filter_extra_fields = True

    first_name = validators.String(
        not_empty=True,
        max=constants.DB_STRING_SIZE,
        messages={'empty': 'Please enter a first name', 'missing': 'Please enter a first name'})
    last_name = validators.String(
        not_empty=True,
        max=constants.DB_STRING_SIZE,
        messages={'empty': 'Please enter a last name', 'missing': 'Please enter a last name'})
    email = validators.Email(not_empty=True, max=constants.DB_STRING_SIZE,
                             messages={'empty': 'Please enter an email',
                                       'missing': 'Please enter an email',
                                       'noAt': 'Please enter a valid email',
                                       'badUsername': 'Please enter a valid email',
                                       'badDomain': 'Please enter a valid email'})
    institution = validators.String(not_empty=True, max=constants.DB_STRING_SIZE,
                                    messages={'empty': 'Please enter your institution',
                                              'missing': 'Please enter your institution'})
    usage = validators.String(not_empty=True, max=constants.DB_LONG_STRING_SIZE,
                              messages={'empty': 'Please describe how you will use Majic',
                                        'missing': 'Please describe how you will use Majic'})
    license = validators.String(not_empty=True,
                                messages={'empty': 'You must agree to the Majic license',
                                          'missing' : 'You must agree to the Majic license'})