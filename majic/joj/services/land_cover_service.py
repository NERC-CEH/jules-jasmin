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
from sqlalchemy import asc
from sqlalchemy.orm import subqueryload, eagerload

from joj.services.general import DatabaseService, ServiceException
from joj.model import LandCoverRegion, LandCoverValue, LandCoverRegionCategory, LandCoverAction
from joj.utils import constants
from joj.services.dap_client.dap_client_factory import DapClientFactory
from joj.services.dataset import DatasetService
from joj.services.dap_client.base_dap_client import DapClientException
from joj.services.parameter_service import ParameterService


class LandCoverService(DatabaseService):
    """
    Provides access to operations on the land cover regions
    """

    def __init__(self, dap_client_factory=DapClientFactory(), dataset_service=DatasetService(),
                 parameter_service=ParameterService()):
        super(LandCoverService, self).__init__()
        self.dap_client_factory = dap_client_factory
        self.dataset_service = dataset_service
        self.parameter_service = parameter_service

    def get_land_cover_region_by_id(self, id):
        """
        Get a specified land cover region
        :param id: Database ID of the land cover region requested
        :return: LandCoverRegion
        """
        with self.readonly_scope() as session:
            return self._get_land_cover_region_by_id_in_session(id, session)

    def get_land_cover_values(self, python_parameter_values, return_ice=True):
        """
        Return all available land cover values
        :param python_parameter_values: an object on which get_python_parameter_value can be called to get a value
        :return: List of Land Cover Values
        :param return_ice: Whether to return the ice value
        """
        with self.readonly_scope() as session:
            land_cover_values = session.query(LandCoverValue).all()
        ice_index_from_parameters = None
        if python_parameter_values is not None:
            ice_index_from_parameters = python_parameter_values.get_python_parameter_value(
                constants.JULES_PARAM_MODEL_LEVELS_ICE_INDEX)
        has_ice = ice_index_from_parameters is None and ice_index_from_parameters != -1
        if return_ice and has_ice:
            return land_cover_values

        ice_index = self.find_ice_index(land_cover_values)
        if ice_index is None:
            return ice_index

        non_ice_values = []
        for land_cover_value in land_cover_values:
            if land_cover_value.index != ice_index:
                non_ice_values.append(land_cover_value)
        return non_ice_values

    def _get_land_cover_categories_in_session(self, driving_data_id, session):
        """
        Return all available land cover categories for a given driving dataset
        :param driving_data_id: Database ID of chosen driving dataset
        :return: List of LandCoverCategories (with Regions loaded)
        """
        return session.query(LandCoverRegionCategory) \
            .filter(LandCoverRegionCategory.driving_dataset_id == driving_data_id) \
            .options(subqueryload(LandCoverRegionCategory.regions)) \
            .all()

    def get_land_cover_categories(self, driving_data_id):
        """
        Return all available land cover categories for a given driving dataset
        :param driving_data_id: Database ID of chosen driving dataset
        :return: List of LandCoverCategories (with Regions loaded)
        """
        with self.readonly_scope() as session:
            return self._get_land_cover_categories_in_session(driving_data_id, session)

    def get_land_cover_regions(self, driving_data_id):
        """
        Return all available land cover regions for a given driving dataset
        :param driving_data_id: Database ID of chosen driving dataset
        :return: List of LandCoverRegions (with Categories loaded)
        """
        with self.readonly_scope() as session:
            return session.query(LandCoverRegion)\
                .join(LandCoverRegionCategory)\
                .filter(LandCoverRegionCategory.driving_dataset_id == driving_data_id)\
                .options(eagerload(LandCoverRegion.category))\
                .all()

    def save_land_cover_actions_for_model(self, model_run, land_cover_actions):
        """
        Save a list of LandCoverActions against a model run
        :param model_run: Model run to save against
        :param land_cover_actions: List of LandCoverActions
        :return:
        """
        with self.transaction_scope() as session:
            session.query(LandCoverAction)\
                .filter(LandCoverAction.model_run_id == model_run.id)\
                .delete()
            for land_cover_action in land_cover_actions:
                land_cover_action.model_run = model_run
                session.add(land_cover_action)

    def get_land_cover_actions_for_model(self, model_run):
        """
        Get all land cover actions saved for a model run
        :param model_run: Model run to retrieve for
        :return: List of land cover actions
        """
        with self.readonly_scope() as session:
            return session.query(LandCoverAction)\
                .filter(LandCoverAction.model_run_id == model_run.id)\
                .options(subqueryload(LandCoverAction.region)
                         .subqueryload(LandCoverRegion.category))\
                .options(subqueryload(LandCoverAction.value))\
                .order_by(asc(LandCoverAction.order))\
                .all()

    def save_fractional_land_cover_for_model(self, model_run, fractional_string):
        """
        Save fractional land cover for a model run
        :param model_run:
        :param fractional_string:
        :return:
        """
        with self.transaction_scope() as session:
            model_run.land_cover_frac = fractional_string
            session.merge(model_run)

    def get_default_fractional_cover(self, model_run, user):
        """
        Get the default fractional land cover for a model run
        :param model_run: Model run being created
        :param user: user
        :return: Fractional land cover as a list of floats.
        """
        latlon = model_run.get_python_parameter_value(constants.JULES_PARAM_POINTS_FILE, is_list=True)
        if latlon is None:
            raise ServiceException("Could not get default fractional cover: the model run does not have any "
                                   "saved single cell location information")
        lat, lon = latlon
        driving_dataset = self._get_best_matching_dataset_to_use(lat, lon, user, model_run)
        if driving_dataset is not None:
            try:
                land_cover_url, land_cover_key = self._get_land_cover_url_and_key_for_driving_dataset(driving_dataset)
                land_cover_client = self.dap_client_factory.get_land_cover_dap_client(land_cover_url, land_cover_key)
                return land_cover_client.get_fractional_cover(lat, lon)
            except DapClientException:
                # if we get a dap exception just use the defaults
                pass
        ntypes = len(self.get_land_cover_values(model_run, return_ice=True))
        return ntypes * [0.0]

    def save_default_soil_properties(self, model_run, user):
        """
        Retrieve and save default soil properties for a single cell model run
        :param model_run: Model run to save default soil properties for
        :param user: the user
        :return:
        """
        latlon = model_run.get_python_parameter_value(constants.JULES_PARAM_POINTS_FILE, is_list=True)
        if latlon is None:
            raise ServiceException("Could not get default soil properties: the model run does not have any "
                                   "saved single cell location information")
        lat, lon = latlon
        driving_dataset = self._get_best_matching_dataset_to_use(lat, lon, user, model_run)
        if driving_dataset is not None:
            nvars = driving_dataset.get_python_parameter_value(constants.JULES_PARAM_SOIL_PROPS_NVARS)
            vars = driving_dataset.get_python_parameter_value(constants.JULES_PARAM_SOIL_PROPS_VAR)
            use_file_original = driving_dataset.get_python_parameter_value(constants.JULES_PARAM_SOIL_PROPS_USE_FILE)
            const_val_original = driving_dataset.get_python_parameter_value(constants.JULES_PARAM_SOIL_PROPS_CONST_VAL)
            var_names_in_file = driving_dataset.get_python_parameter_value(constants.JULES_PARAM_SOIL_PROPS_VAR_NAME)
            netcdf_keys = dict(zip(vars, var_names_in_file))
            use_file = nvars * [False]
            soil_file = driving_dataset.get_python_parameter_value(constants.JULES_PARAM_SOIL_PROPS_FILE)
            try:
                url = self.dap_client_factory.get_full_url_for_file(soil_file)
                soil_props_client = self.dap_client_factory.get_soil_properties_dap_client(url)
                soil_props = soil_props_client.get_soil_properties(
                    lat,
                    lon,
                    var_names_in_file,
                    use_file_original,
                    const_val_original)
                if soil_props is not None:
                    soil_prop_vals = [soil_props[netcdf_keys[key]] for key in vars]  # Use the netCDF key
                    params_vals = [[constants.JULES_PARAM_SOIL_PROPS_NVARS, nvars],
                                   [constants.JULES_PARAM_SOIL_PROPS_VAR, vars],
                                   [constants.JULES_PARAM_SOIL_PROPS_USE_FILE, use_file],
                                   [constants.JULES_PARAM_SOIL_PROPS_CONST_VAL, soil_prop_vals]]
                    old_param_vals = [constants.JULES_PARAM_SOIL_PROPS_NVARS,
                                      constants.JULES_PARAM_SOIL_PROPS_VAR,
                                      constants.JULES_PARAM_SOIL_PROPS_USE_FILE,
                                      constants.JULES_PARAM_SOIL_PROPS_CONST_VAL]
                    self.parameter_service.save_new_parameters(params_vals, old_param_vals, model_run.user_id)
            except DapClientException:
                # We don't want to do anything because we'll just leave whatever defaults are already present.
                return

    def find_ice_index(self, land_cover_types):
        """
        Search through a list of land cover types to find the index of the ice type
        :param land_cover_types: List of land cover types
        :return: The 1-based index of the ice type; or None if not found
        """
        for type in land_cover_types:
            if type.name == constants.FRACTIONAL_ICE_NAME:
                return type.index
        return None

    def update_regions_and_categories_in_session(self, session, driving_dataset, regions):
        """
        Create or modify the regions and categories for a driving dataset
        :param session: the session to use
        :param driving_dataset: the driving dataset that the categories belong to
        :param regions: a regions list containing parameter dictionaries
        :return: nothing
        """

        categoies = self._get_land_cover_categories_in_session(driving_dataset.id, session)
        for region in regions:
            category = self._get_or_create_category(categoies, driving_dataset, region["category"])
            self._update_or_create_region(category, region, session)

        # remove empty categories
        for category in categoies:
            if len(category.regions) == 0:
                session.delete(category)

    def _get_best_matching_dataset_to_use(self, lat, lon, user, model_run):
        user_upload_ds_id = self.dataset_service.get_id_for_user_upload_driving_dataset()
        if model_run.driving_dataset.id != user_upload_ds_id:
            return self.dataset_service.get_driving_dataset_by_id(model_run.driving_dataset_id)
        usable_datasets = []
        driving_datasets = self.dataset_service.get_driving_datasets(user)
        for dataset in driving_datasets:
            if dataset.id == user_upload_ds_id:
                continue
            if not dataset.boundary_lat_north >= lat >= dataset.boundary_lat_south:
                continue
            if not dataset.boundary_lon_east >= lon >= dataset.boundary_lon_west:
                continue
            usable_datasets.append(dataset)
        sorted_results = sorted(usable_datasets, key=lambda ds: ds.usage_order_index)
        if len(sorted_results) > 0:
            # Reload the driving dataset to get all the parameters
            driving_dataset = self.dataset_service.get_driving_dataset_by_id(sorted_results[0].id)
            return driving_dataset
        else:
            return None

    def _get_land_cover_url_and_key_for_driving_dataset(self, driving_dataset):

        frac_file = driving_dataset.get_python_parameter_value(constants.JULES_PARAM_FRAC_FILE)
        frac_name = driving_dataset.get_python_parameter_value(constants.JULES_PARAM_FRAC_NAME)
        url = self.dap_client_factory.get_full_url_for_file(frac_file)

        return url, frac_name

    def _get_land_cover_region_by_id_in_session(self, id, session):
        """
        Get the land cover region by id using a specific session
        :param id: id of the land cover
        :param session: session
        :return: land cover region
        """
        return session.query(LandCoverRegion) \
            .filter(LandCoverRegion.id == id) \
            .options(subqueryload(LandCoverRegion.category)) \
            .one()

    def _get_or_create_category(self, categoies, driving_dataset, category_name):
        """
        Gets a category with the given name. Either by finding it or creating it
        :param categoies: current list of categories (updated if new one is added)
        :param driving_dataset: the driving dataset to set for the category
        :param category_name: the name of the category
        :return: the category
        """
        found_category = None
        for category in categoies:
            if category.name == category_name:
                found_category = category
                break
        if found_category is None:
            found_category = LandCoverRegionCategory(name=category_name)
            found_category.driving_dataset = driving_dataset
            categoies.append(found_category)
        return found_category

    def _update_or_create_region(self, category, region, session):
        """
        Update or create a land cover region
        :param category: category for the region
        :param region: a dictionry of region parameters
        :param session: the session
        :return: nothing
        """
        existing_region_id = region.get("id")
        if existing_region_id is not None and existing_region_id is not "":
            region_in_db = self._get_land_cover_region_by_id_in_session(existing_region_id, session)
        else:
            region_in_db = LandCoverRegion()
        region_in_db.category = category
        region_in_db.name = region["name"]
        region_in_db.mask_file = region["path"]
