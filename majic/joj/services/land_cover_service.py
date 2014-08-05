"""
header
"""
from joj.services.general import DatabaseService
from joj.model import LandCoverRegion


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
            return session.query(LandCoverRegion).filter(LandCoverRegion.id == id).one()



    def get_land_cover_types(self):
        # todo write and test
        pass