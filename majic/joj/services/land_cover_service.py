"""
header
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
            return session.query(LandCoverRegion)\
                .filter(LandCoverRegion.id == id)\
                .options(subqueryload(LandCoverRegion.category))\
                .one()

    def get_land_cover_values(self, return_ice=True):
        """
        Return all available land cover values
        :return: List of Land Cover Values
        :param return_ice: Whether to return the ice value
        """
        with self.readonly_scope() as session:
            land_cover_values = session.query(LandCoverValue).all()
        if return_ice:
            return land_cover_values
        else:
            ice_index = self.find_ice_index(land_cover_values)
            non_ice_values = []
        for land_cover_value in land_cover_values:
            if land_cover_value.index != ice_index:
                non_ice_values.append(land_cover_value)
        return non_ice_values

    def get_land_cover_categories(self, driving_data_id):
        """
        Return all available land cover categories for a given driving dataset
        :param driving_data_id: Database ID of chosen driving dataset
        :return: List of LandCoverCategories (with Regions loaded)
        """
        with self.readonly_scope() as session:
            return session.query(LandCoverRegionCategory)\
                .filter(LandCoverRegionCategory.driving_dataset_id == driving_data_id)\
                .options(subqueryload(LandCoverRegionCategory.regions))\
                .all()

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

    def get_default_fractional_cover(self, model_run):
        """
        Get the default fractional land cover for a model run
        :param model_run: Model run being created
        :return: Fractional land cover as a list of floats.
        """
        latlon = model_run.get_python_parameter_value(constants.JULES_PARAM_POINTS_FILE, is_list=True)
        if latlon is None:
            raise ServiceException("Could not get default fractional cover: the model run does not have any "
                                   "saved single cell location information")
        lat, lon = latlon
        driving_dataset = self._get_best_matching_dataset_to_use(lat, lon)
        if driving_dataset is not None:
            try:
                land_cover_url, land_cover_key = self._get_land_cover_url_and_key_for_driving_dataset(driving_dataset)
                land_cover_client = self.dap_client_factory.get_land_cover_dap_client(land_cover_url, land_cover_key)
                return land_cover_client.get_fractional_cover(lat, lon)
            except DapClientException:
                pass
        ntypes = len(self.get_land_cover_values(return_ice=True))
        return ntypes * [0.0]

    def save_default_soil_properties(self, model_run):
        """
        Retrieve and save default soil properties for a single cell model run
        :param model_run: Model run to save default soil properties for
        :return:
        """
        latlon = model_run.get_python_parameter_value(constants.JULES_PARAM_POINTS_FILE, is_list=True)
        if latlon is None:
            raise ServiceException("Could not get default soil properties: the model run does not have any "
                                   "saved single cell location information")
        lat, lon = latlon
        driving_dataset = self._get_best_matching_dataset_to_use(lat, lon)
        if driving_dataset is not None:
            nvars = driving_dataset.get_python_parameter_value(constants.JULES_PARAM_SOIL_PROPS_NVARS)
            vars = driving_dataset.get_python_parameter_value(constants.JULES_PARAM_SOIL_PROPS_VAR, is_list=True)
            var_names = driving_dataset.get_python_parameter_value(
                constants.JULES_PARAM_SOIL_PROPS_VAR_NAME, is_list=True)
            netcdf_keys = dict(zip(vars, var_names))
            use_file = nvars * [False]
            soil_file = driving_dataset.get_python_parameter_value(constants.JULES_PARAM_SOIL_PROPS_FILE)
            try:
                url = self.dap_client_factory.get_full_url_for_file(soil_file)
                soil_props_client = self.dap_client_factory.get_soil_properties_dap_client(url)
                soil_props = soil_props_client.get_soil_properties(lat, lon)
                if soil_props is not None:
                    soil_prop_vals = [soil_props[netcdf_keys[key]] for key in vars]  # Use the netCDF key
                    params_vals = [[constants.JULES_PARAM_SOIL_PROPS_NVARS, nvars],
                                   [constants.JULES_PARAM_SOIL_PROPS_VAR, vars],
                                   [constants.JULES_PARAM_SOIL_USE_FILE, use_file],
                                   [constants.JULES_PARAM_SOIL_CONST_VALS, soil_prop_vals]]
                    old_param_vals = [constants.JULES_PARAM_SOIL_PROPS_NVARS,
                                      constants.JULES_PARAM_SOIL_PROPS_VAR,
                                      constants.JULES_PARAM_SOIL_USE_FILE,
                                      constants.JULES_PARAM_SOIL_CONST_VALS]
                    self.parameter_service.save_new_parameters(params_vals, old_param_vals, model_run)
            except DapClientException:
                # We don't want to do anything because we'll just leave whatever defaults are already present.
                return

    def find_ice_index(self, land_cover_types):
        """
        Search through a list of land cover types to find the index of the ice type
        :param land_cover_types: List of land cover types
        :return: The 1-based index of the ice type
        """
        return [type.index for type in land_cover_types if type.name == constants.FRACTIONAL_ICE_NAME][0]

    def _get_best_matching_dataset_to_use(self, lat, lon):
        driving_datasets = self.dataset_service.get_driving_datasets()
        user_upload_ds_id = self.dataset_service.get_id_for_user_upload_driving_dataset()
        usable_datasets = []
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
