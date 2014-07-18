"""
header
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
