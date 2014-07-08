"""
header
"""

from formencode import Schema, validators


class ModelRunExtentSchema(Schema):
    """Used to validate data for the model run extents page"""

    allow_extra_fields = True
    filter_extra_fields = False

    lat_n = validators.Number(not_empty=True)
    lat_s = validators.Number(not_empty=True)
    lon_e = validators.Number(not_empty=True)
    lon_w = validators.Number(not_empty=True)
    start_date = validators.DateConverter(not_empty=True, month_style='yyyy/mm/dd')
    end_date = validators.DateConverter(not_empty=True, month_style='yyyy/mm/dd')
