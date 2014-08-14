"""
header
"""
from sqlalchemy import asc
from sqlalchemy.orm import subqueryload
from joj.services.general import DatabaseService
from joj.model import LandCoverRegion, LandCoverValue, LandCoverRegionCategory, LandCoverAction
from joj.utils import constants


class LandCoverService(DatabaseService):
    """
    Provides access to operations on the land cover regions
    """

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

    def get_land_cover_values(self):
        """
        Return all available land cover values
        :return: List of Land Cover Values
        """
        with self.readonly_scope() as session:
            return session.query(LandCoverValue).all()

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
        pass

    def get_default_fractional_cover(self, model_run):
        """
        Get the default fractional land cover for a model run
        :param model_run: Model run being created
        :return: Fractional land cover as a list of floats.
        """
        pass

    def find_ice_index(self, land_cover_types):
        """
        Search through a list of land cover types to find the index of the ice type
        :param land_cover_types: List of land cover types
        :return: The 1-based index of the ice type
        """
        return [type.index for type in land_cover_types if type.name == constants.FRACTIONAL_ICE_NAME][0]
