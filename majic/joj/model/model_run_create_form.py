"""
header
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
