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
from formencode import Schema, validators
from joj.utils import constants


class ModelRunCreateParameters(Schema):
    """Used to validate data for the model run create form for parameters"""

    allow_extra_fields = True
    filter_extra_fields = True

    def __init__(self, parameters, *args, **kw):
        """
        Constructor

        Arguments:
        parameters -- a list of parameters to create a validation schema for
        """

        super(ModelRunCreateParameters, self).__init__(*args, **kw)
        for parameter in parameters:
            min_value = parameter.min or None
            max_value = parameter.max or None
            if parameter.type == constants.PARAMETER_TYPE_INTEGER:
                validator = validators.Int(not_empty=parameter.required, min=min_value, max=max_value)
            else:
                raise Exception(message='Unknown parameter type %s' % parameter.type)

            self.add_field(name="param" + str(parameter.id), validator=validator)
