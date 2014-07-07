"""
header
"""
from hamcrest import assert_that, is_
from joj.utils import constants

JULES_YEARLY_PERIOD = -2
JULES_MONTHLY_PERIOD = -1
JULES_DAILY_PERIOD = 24 * 60 * 60
TIMESTEP_DESCRIPTION = 'Hourly'  # The description used on the web page for output_period == timestep.


def add_selected_outputs_to_template_context(template_context, model_run):
    """
    Helper method to add any output_variables that have already been selected (and their chosen output periods)
    to the template context for rendering.
    :param template_context: Pylons template context to add selected output variable lists to
    :param model_run: The model run currently being used
    :return: nothing
    """
    template_context.selected_output_ids = []
    template_context.yearly_output_ids = []
    template_context.monthly_output_ids = []
    template_context.daily_output_ids = []
    template_context.timestep_output_ids = []
    template_context.timestep_description = TIMESTEP_DESCRIPTION

    # Get the list of ParameterValues for the JULES params 'var' and 'output_period'
    selected_vars = model_run.get_parameter_values(constants.JULES_PARAM_VAR)
    selected_output_periods = model_run.get_parameter_values(constants.JULES_PARAM_OUTPUT_PERIOD)

    # For each selected output variable we need to get the param_id,
    # and identify the corresponding selected time periods:
    for selected_var in selected_vars:
        # Get the parameter id
        param_id = [output_variable.id for output_variable in template_context.output_variables
                    if output_variable.name == selected_var.get_value_as_python()][0]
        template_context.selected_output_ids.append(param_id)

        # Go through the selected output period and see which ones are for this output variable
        for output_period in selected_output_periods:
            if output_period.group_id == selected_var.group_id:
                period = output_period.get_value_as_python()
                if period == JULES_YEARLY_PERIOD:
                    template_context.yearly_output_ids.append(param_id)
                elif period == JULES_MONTHLY_PERIOD:
                    template_context.monthly_output_ids.append(param_id)
                elif period == JULES_DAILY_PERIOD:
                    template_context.daily_output_ids.append(param_id)
                else:
                    template_context.timestep_output_ids.append(param_id)


def create_output_variable_groups(post_values, model_run_service, model_run):
    """
    Helper method to process the output page POST data and create groups of parameters and values to be saved
    to the database
    :param post_values: Dictionary of POST values
    :param model_run_service: Model run service to use
    :param model_run: Model run to use
    :return: List of output variable groups, where each group contains a list of parameters to set and values
    (also as a list)
    """
    # If the timestep is not set we expect an error thrown here:
    timestep = model_run.get_python_parameter_value(constants.JULES_PARAM_TIMESTEP_LEN)
    # The daily time period needs to be a multiple of the timestep so check this here to raise errors
    # before they are sent to JULES
    assert_that(JULES_DAILY_PERIOD % timestep, is_(0), "The duration of a day (24 * 60 * 60 seconds) as used for the "
                                                       "output variables is not divisible by the timestep length. "
                                                       "You should set JULES_TIME::timestep_len to be a factor of "
                                                       "86400 or JULES won't run correctly.")
    output_variable_groups = []
    for value in post_values:
        if "ov_select_" in value:
            output_id = int(value.split("ov_select_")[1])
            output_param_name = model_run_service.get_output_variable_by_id(output_id).name
            if "ov_yearly_" + str(output_id) in post_values:
                output_variable_group = [
                    [constants.JULES_PARAM_VAR, output_param_name],
                    [constants.JULES_PARAM_OUTPUT_PERIOD, JULES_YEARLY_PERIOD],
                    [constants.JULES_PARAM_PROFILE_NAME, output_param_name + "_yearly"]
                ]
                output_variable_groups.append(output_variable_group)
            if "ov_monthly_" + str(output_id) in post_values:
                output_variable_group = [
                    [constants.JULES_PARAM_VAR, output_param_name],
                    [constants.JULES_PARAM_OUTPUT_PERIOD, JULES_MONTHLY_PERIOD],
                    [constants.JULES_PARAM_PROFILE_NAME, output_param_name + "_monthly"]
                ]
                output_variable_groups.append(output_variable_group)
            if "ov_daily_" + str(output_id) in post_values:
                output_variable_group = [
                    [constants.JULES_PARAM_VAR, output_param_name],
                    [constants.JULES_PARAM_OUTPUT_PERIOD, JULES_DAILY_PERIOD],
                    [constants.JULES_PARAM_PROFILE_NAME, output_param_name + "_daily"]
                ]
                output_variable_groups.append(output_variable_group)
            if "ov_timestep_" + str(output_id) in post_values:
                output_variable_group = [
                    [constants.JULES_PARAM_VAR, output_param_name],
                    [constants.JULES_PARAM_OUTPUT_PERIOD, timestep],
                    [constants.JULES_PARAM_PROFILE_NAME, output_param_name + "_timestep"]
                ]
                output_variable_groups.append(output_variable_group)
    return output_variable_groups