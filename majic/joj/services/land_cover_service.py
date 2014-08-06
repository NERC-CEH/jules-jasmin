"""
header
"""
from sqlalchemy.orm import subqueryload
from joj.services.general import DatabaseService
from joj.model import LandCoverRegion, LandCoverValue


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
        :return:
        """
        with self.readonly_scope() as session:
            return session.query(LandCoverValue).all()