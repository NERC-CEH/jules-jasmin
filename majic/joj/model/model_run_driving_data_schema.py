"""
header
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
