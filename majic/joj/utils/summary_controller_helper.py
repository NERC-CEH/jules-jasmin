"""
header
"""
from joj.services.model_run_service import ModelRunService
from joj.services.land_cover_service import LandCoverService
from joj.services.general import ServiceException
from joj.utils import constants
from joj.utils.extents_controller_helper import ExtentsControllerHelper
from joj.utils.land_cover_controller_helper import LandCoverControllerHelper


class SummaryControllerHelper(object):
    """
    Helper class for summary and submit controllers
    """

    def __init__(self, model_run_service=ModelRunService()):
        self._model_run_service = model_run_service

    def add_summary_fields_to_context(self, model_run, context, user):
        """
        Add summary information to a template context, containing basic information
        for each of the pages in the workflow.
        :param model_run: Model run being created
        :param context: Context to summary fields to
        :param user: user
        :return:
        """
        # Create page
        context.model_run = model_run
        context.science_config = self._model_run_service.get_science_configuration_by_id(
            model_run.science_configuration_id)

        # Driving data page
        driving_data = model_run.driving_dataset
        context.driving_data_name = model_run.driving_dataset.name

        # Extents page
        extents_controller_helper = ExtentsControllerHelper()
        context.extents_values = extents_controller_helper.create_values_dict_from_database(model_run, driving_data)

        # Land cover page
        land_cover_service = LandCoverService()
        context.land_cover_actions = land_cover_service.get_land_cover_actions_for_model(model_run)
        land_cover_helper = LandCoverControllerHelper()
        try:
            land_cover_helper.add_fractional_land_cover_to_context(context, {}, model_run, user)
        except ServiceException:
            pass

        # Outputs page
        output_variables = self._model_run_service.get_output_variables()
        output_variable_dict = dict((x.name, x.description) for x in output_variables)
        selected_vars = model_run.get_parameter_values(constants.JULES_PARAM_OUTPUT_VAR)
        selected_output_periods = model_run.get_parameter_values(constants.JULES_PARAM_OUTPUT_PERIOD)
        outputs = {}
        # Each group contains one output variable and one output period
        for selected_var in selected_vars:
            var_name = selected_var.get_value_as_python()
            if var_name not in outputs:
                outputs[var_name] = []
            for output_period in selected_output_periods:
                if output_period.group_id == selected_var.group_id:
                    period = output_period.get_value_as_python()
                    if period == constants.JULES_YEARLY_PERIOD:
                        outputs[var_name].append('Yearly')
                    elif period == constants.JULES_MONTHLY_PERIOD:
                        outputs[var_name].append('Monthly')
                    elif period == constants.JULES_DAILY_PERIOD:
                        outputs[var_name].append('Daily')
                    else:
                        outputs[var_name].append('Hourly')
        context.outputs = []
        for output in outputs:
            context.outputs.append(output_variable_dict[output] + ' - ' + ', '.join(map(str, outputs[output])) + '')
        context.outputs.sort()

        # Downloads
        context.output_variable_dict = output_variable_dict
        context.output_variable_id_dict = dict((x.name, x.id) for x in output_variables)
        context.downloads = outputs
        context.download_formats = ["NetCDF"]
        if context.extents_values['site'] == 'single':
            context.download_formats.append('ASCII')
