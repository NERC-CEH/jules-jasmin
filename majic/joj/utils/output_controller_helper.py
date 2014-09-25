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
from joj.utils import constants
from joj.utils import utils


def yearly_output_allowed(model_run):
    """
    Determine whether yearly output is allowed for the model run
    :param model_run: Model Run being created
    :return: True if allowed, otherwise False
    """
    run_start = model_run.get_python_parameter_value(constants.JULES_PARAM_RUN_START)
    run_end = model_run.get_python_parameter_value(constants.JULES_PARAM_RUN_END)
    if utils.is_first_of_year(run_start):
        return True
    else:
        next_year = utils.next_first_of_year(run_start)
        return next_year <= run_end


def monthly_output_allowed(model_run):
    """
    Determine whether monthly output is allowed for the model run
    :param model_run: Model Run being created
    :return: True if allowed, otherwise False
    """
    run_start = model_run.get_python_parameter_value(constants.JULES_PARAM_RUN_START)
    run_end = model_run.get_python_parameter_value(constants.JULES_PARAM_RUN_END)
    if utils.is_first_of_month(run_start):
        return True
    else:
        next_month = utils.next_first_of_month(run_start)
        return next_month <= run_end


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
    template_context.hourly_output_ids = []

    # Get the list of ParameterValues for the JULES params 'var' and 'output_period'
    selected_vars = model_run.get_parameter_values(constants.JULES_PARAM_OUTPUT_VAR)
    selected_output_periods = model_run.get_parameter_values(constants.JULES_PARAM_OUTPUT_PERIOD)

    # For each selected output variable we need to get the param_id,
    # and identify the corresponding selected time periods:
    for selected_var in selected_vars:
        # Get the parameter id
        matching_param_ids = [output_variable.id for output_variable in template_context.output_variables
                              if output_variable.name == selected_var.get_value_as_python()]
        # If we can't find a matching parameter ID, forget this parameter.
        if len(matching_param_ids) == 0:
            continue
        param_id = matching_param_ids[0]
        template_context.selected_output_ids.append(param_id)

        # Go through the selected output period and see which ones are for this output variable
        for output_period in selected_output_periods:
            if output_period.group_id == selected_var.group_id:
                period = output_period.get_value_as_python()
                if period == constants.JULES_YEARLY_PERIOD:
                    template_context.yearly_output_ids.append(param_id)
                elif period == constants.JULES_MONTHLY_PERIOD:
                    template_context.monthly_output_ids.append(param_id)
                elif period == constants.JULES_DAILY_PERIOD:
                    template_context.daily_output_ids.append(param_id)
                else:
                    template_context.hourly_output_ids.append(param_id)


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
    multicell = model_run.get_python_parameter_value(constants.JULES_PARAM_LATLON_REGION)
    if multicell:
        collate_period = -2
    else:
        collate_period = 0
    output_variable_groups = []
    for value in post_values:
        if "ov_select_" in value:
            output_id = int(value.split("ov_select_")[1])
            output_param_name = model_run_service.get_output_variable_by_id(output_id).name
            if "ov_yearly_" + str(output_id) in post_values:
                output_variable_group = [
                    [constants.JULES_PARAM_OUTPUT_VAR, output_param_name],
                    [constants.JULES_PARAM_OUTPUT_PERIOD, constants.JULES_YEARLY_PERIOD],
                    [constants.JULES_PARAM_OUTPUT_PROFILE_NAME, output_param_name + "_yearly"],
                    [constants.JULES_PARAM_OUTPUT_FILE_PERIOD, 0]
                ]
                output_variable_groups.append(output_variable_group)
            if "ov_monthly_" + str(output_id) in post_values:
                output_variable_group = [
                    [constants.JULES_PARAM_OUTPUT_VAR, output_param_name],
                    [constants.JULES_PARAM_OUTPUT_PERIOD, constants.JULES_MONTHLY_PERIOD],
                    [constants.JULES_PARAM_OUTPUT_PROFILE_NAME, output_param_name + "_monthly"],
                    [constants.JULES_PARAM_OUTPUT_FILE_PERIOD, 0]
                ]
                output_variable_groups.append(output_variable_group)
            if "ov_daily_" + str(output_id) in post_values:
                output_variable_group = [
                    [constants.JULES_PARAM_OUTPUT_VAR, output_param_name],
                    [constants.JULES_PARAM_OUTPUT_PERIOD, constants.JULES_DAILY_PERIOD],
                    [constants.JULES_PARAM_OUTPUT_PROFILE_NAME, output_param_name + "_daily"],
                    [constants.JULES_PARAM_OUTPUT_FILE_PERIOD, collate_period]
                ]
                output_variable_groups.append(output_variable_group)
            if "ov_hourly_" + str(output_id) in post_values:
                output_variable_group = [
                    [constants.JULES_PARAM_OUTPUT_VAR, output_param_name],
                    [constants.JULES_PARAM_OUTPUT_PERIOD, constants.JULES_HOURLY_PERIOD],
                    [constants.JULES_PARAM_OUTPUT_PROFILE_NAME, output_param_name + "_hourly"],
                    [constants.JULES_PARAM_OUTPUT_FILE_PERIOD, collate_period]
                ]
                output_variable_groups.append(output_variable_group)
    return output_variable_groups