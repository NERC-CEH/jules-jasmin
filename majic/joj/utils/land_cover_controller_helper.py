"""
header
"""
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
        tmpl_context.land_cover_values = self.land_cover_service.get_land_cover_values()
        tmpl_context.land_cover_categories = self.land_cover_service.get_land_cover_categories(
            model_run.driving_dataset_id)

    def save_land_covers(self, values, errors, model_run):
        """
        Validate and Save requested land cover actions
        :param values: POST dictionary of form values
        :param errors: Object to add errors to
        :param model_run: The model run being created
        :return:
        """
        self._validate_values(values, errors, model_run.driving_dataset)
        if len(errors) == 0:
            land_cover_actions = []
            actions = []
            for key in values:
                actions += re.findall("^action_(\d+)", key)
            for index in set(actions):
                lcra = LandCoverAction()
                lcra.region_id = int(values['action_%s_region' % index])
                lcra.value_id = int(values['action_%s_value' % index])
                lcra.order = int(values['action_%s_order' % index])
                land_cover_actions.append(lcra)
            self.land_cover_service.save_land_cover_actions_for_model(model_run, land_cover_actions)

    def _validate_values(self, values, errors, driving_data):
        # Check that:
        # - Values correspond to known land cover types
        # - Region IDs correspond to recognised regions for the current driving_data
        land_cover_values = self.land_cover_service.get_land_cover_values()
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
        land_cover_values = self.land_cover_service.get_land_cover_values()
        land_cover_value_ids = [lc_type.id for lc_type in land_cover_values]

        for action in land_cover_actions:
            if action.value_id not in land_cover_value_ids:
                errors['land_cover_actions'] = "Land Cover Value does not correspond to a valid land cover type"
            if not action.region.category.driving_dataset_id == model_run.driving_dataset_id:
                errors['land_cover_actions'] = "Your saved Land Cover edits are not valid for the chosen driving data"

    def _does_region_belong_to_driving_data(self, region_id, driving_data):
        land_cover_region = self.land_cover_service.get_land_cover_region_by_id(region_id)
        return land_cover_region.category.driving_dataset_id == driving_data.id
