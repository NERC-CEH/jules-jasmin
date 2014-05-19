import formencode

__author__ = 'Chirag Mistry (Tessella)'


class ConfigureAnalysisForm(formencode.Schema):
    """Used to validate data from the Configure Analysis page"""

    allow_extra_fields = True
    filter_extra_fields = False

    analysis_name = formencode.validators.String(not_empty=True)
    coverage_dataset_ids = formencode.validators.Set(not_empty=True)
    unit_of_time = formencode.validators.String(not_empty=True)
    random_group = formencode.validators.String(not_empty=True)
    model_variable = formencode.validators.String(not_empty=True)
    data_type = formencode.validators.String(not_empty=True)
    analysis_description = formencode.validators.String(not_empty=True)