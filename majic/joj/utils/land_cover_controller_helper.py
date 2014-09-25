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
from decimal import Decimal, InvalidOperation
from math import copysign
import re
from joj.model import LandCoverAction
from joj.services.land_cover_service import LandCoverService


class LandCoverControllerHelper(object):
    """
    Helper class for the land cover controller
    """

    def __init__(self, land_cover_service=LandCoverService()):
        self.land_cover_service = land_cover_service

    def add_land_covers_to_context(self, tmpl_context, errors, model_run):
        """
        Add the available land cover types and regions to the template context object,
        as well as any currently selected land cover region actions. Validates and adds
        any errors to an errors object.
        :param tmpl_context: The Pylons template context object to add to
        :param errors: The object to add any errors to
        :param model_run: The model run being created
        """
        land_cover_actions = self.land_cover_service.get_land_cover_actions_for_model(model_run)
        self._validate_land_cover_actions(errors, land_cover_actions, model_run)
        if 'land_cover_actions' in errors:
            # If there is an error with the saved land cover actions we don't want to show them.
            tmpl_context.land_cover_actions = []
        else:
            tmpl_context.land_cover_actions = land_cover_actions
        tmpl_context.land_cover_values = self.land_cover_service.get_land_cover_values(model_run, return_ice=False)
        tmpl_context.land_cover_categories = self.land_cover_service.get_land_cover_categories(
            model_run.driving_dataset_id)

    def add_fractional_land_cover_to_context(self, tmpl_context, errors, model_run, user):
        """
        Add the fractional land cover fields to the template context object
        :param tmpl_context: Template context object to add fields to
        :param errors: Object to add any errors to
        :param model_run: Model run being created
        :param user: user
        :return:
        """
        fractional_string = model_run.land_cover_frac
        if fractional_string is None:
            raw_frac_vals = self.land_cover_service.get_default_fractional_cover(model_run, user)
            fractional_values = self._neaten_default_fractional_values(raw_frac_vals)
        else:
            fractional_values = [float(v) for v in fractional_string.split()]

        tmpl_context.land_cover_types = self.land_cover_service.get_land_cover_values(model_run)
        ice_index = self.land_cover_service.find_ice_index(tmpl_context.land_cover_types)
        tmpl_context.ice_index = ice_index

        tmpl_context.land_cover_values = {}
        for land_cover_type in tmpl_context.land_cover_types:
            index = land_cover_type.id
            try:
                value = fractional_values[index - 1]
            except IndexError:
                # In case we have somehow the wrong number of values
                value = 0.0
            if index == ice_index:
                if value > 0.0:
                    tmpl_context.land_cover_values['land_cover_ice'] = 1
            else:
                tmpl_context.land_cover_values["land_cover_value_" + str(index)] = 100 * value

    def save_land_cover_actions(self, values, errors, model_run):
        """
        Validate and Save requested land cover actions
        :param values: POST dictionary of form values
        :param errors: Object to add errors to
        :param model_run: The model run being created
        :return:
        """
        self._validate_values(values, errors, model_run.driving_dataset, model_run)
        if len(errors) == 0:
            land_cover_actions = []
            actions = []
            for key in values:
                actions += re.findall("^action_(\d+)", key)
            for index in set(actions):
                lca = LandCoverAction()
                lca.region_id = int(values['action_%s_region' % index])
                lca.value_id = int(values['action_%s_value' % index])
                lca.order = int(values['action_%s_order' % index])
                land_cover_actions.append(lca)
            self.land_cover_service.save_land_cover_actions_for_model(model_run, land_cover_actions)

    def save_fractional_land_cover(self, values, errors, model_run, user):
        """
        Save the fractional land cover (for user uploaded driving data)
        :param values: POST values dictionary
        :param errors: Object to add errors to
        :param model_run: Model being created
        :param user: user
        :return:
        """
        land_cover_val_prefix = "land_cover_value_"
        land_cover_ice_key = "land_cover_ice"

        types = self.land_cover_service.get_land_cover_values(model_run)
        ntypes = len(types)
        ice_index = self.land_cover_service.find_ice_index(types)

        sorted_fractional_values = ntypes * [Decimal(0.0)]
        if land_cover_ice_key in values:
            if ice_index is not None:
                sorted_fractional_values[ice_index - 1] = Decimal(1.0)
        else:
            for key in values:
                if land_cover_val_prefix in key:
                    cover_key = int(key.split(land_cover_val_prefix)[1])
                    try:
                        cover_value = Decimal(values[key]) / 100
                        sorted_fractional_values[cover_key - 1] = cover_value
                        if cover_value < 0:
                            errors[key] = "Please enter a positive number"
                    except InvalidOperation:
                        errors[key] = "Please enter a number"
            if ice_index is not None:
                sorted_fractional_values[ice_index - 1] = Decimal(0.0)

        if not sum(sorted_fractional_values) == 1.0:
            errors['land_cover_frac'] = 'The sum of all the land cover fractions must be 100%'
        if len(errors) == 0:
            fractional_string = '\t'.join([str(val) for val in sorted_fractional_values])
            self.land_cover_service.save_fractional_land_cover_for_model(model_run, fractional_string)
            self.land_cover_service.save_default_soil_properties(model_run, user)

    def _validate_values(self, values, errors, driving_data, model_run):
        # Check that:
        # - Values correspond to known land cover types
        # - Region IDs correspond to recognised regions for the current driving_data
        land_cover_values = self.land_cover_service.get_land_cover_values(model_run)
        land_cover_value_ids = [lc_type.id for lc_type in land_cover_values]
        try:
            for key in values:
                if 'region' in key:
                    if not self._does_region_belong_to_driving_data(int(values[key]), driving_data):
                        errors['land_cover_actions'] = "Land Cover Region not valid for the chosen driving data"
                if 'value' in key:
                    if not int(values[key]) in land_cover_value_ids:
                        errors['land_cover_actions'] = "Land Cover Value does not correspond to a valid land cover type"
        except ValueError:
            errors['land_cover_actions'] = "Value is not an integer"

    def _validate_land_cover_actions(self, errors, land_cover_actions, model_run):
        land_cover_values = self.land_cover_service.get_land_cover_values(model_run)
        land_cover_value_ids = [lc_type.id for lc_type in land_cover_values]

        for action in land_cover_actions:
            if action.value_id not in land_cover_value_ids:
                errors['land_cover_actions'] = "Land Cover Value does not correspond to a valid land cover type"
            if not action.region.category.driving_dataset_id == model_run.driving_dataset_id:
                errors['land_cover_actions'] = "Your saved Land Cover edits are not valid for the chosen driving data"

    def _does_region_belong_to_driving_data(self, region_id, driving_data):
        land_cover_region = self.land_cover_service.get_land_cover_region_by_id(region_id)
        return land_cover_region.category.driving_dataset_id == driving_data.id

    def _neaten_default_fractional_values(self, raw_frac_vals):
        # Sometimes the default fractional cover retrieved from the netCDF file is awkward in that the
        # fractions are long (11 decimal places) and don't add up to precisely 1.0

        # Set missing values (e.g. -9999) to 0
        missing_values = False
        for value in raw_frac_vals:
            if value < 0:
                missing_values = True
                break
        if missing_values:
            return len(raw_frac_vals) * [0.0]

        if sum(raw_frac_vals) < 0.9 or sum(raw_frac_vals) > 1.1:
            # This is more than just a rounding error
            return raw_frac_vals

        rounded_vals = []
        non_zero_indices = []
        for i in range(len(raw_frac_vals)):
            if raw_frac_vals != 0.0:
                rounded_vals.append(int(10000 * raw_frac_vals[i]))
                non_zero_indices.append(i)
        non_zero_indices.sort(key=lambda i: -rounded_vals[i])
        increment = copysign(1, (10000 - sum(rounded_vals)))
        finished = False
        while not finished:
            for i in non_zero_indices:
                if sum(rounded_vals) == 10000:
                    finished = True
                    break
                rounded_vals[i] += increment
        return [val / 10000.0 for val in rounded_vals]

    def reset_fractional_cover(self, model_run):
        """
        Reset the fractional cover as if it had never been set
        :param model_run: Model run to reset
        :return:
        """
        self.land_cover_service.save_fractional_land_cover_for_model(model_run, None)
