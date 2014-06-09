# header
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
