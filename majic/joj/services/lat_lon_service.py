"""
header
"""
import math
from joj.services.general import DatabaseService


class LatLonService(DatabaseService):
    """
    Service for working with latitude and longitude in relation to datasets
    """

    def get_nearest_cell_center(self, lat, lon, driving_data_id):
        """
        Get the coordinates of the nearest cell center to a specified point
        :param lat: Latitude of specified point
        :param lon: Longitude of specified point
        :param driving_data_id: Driving data ID
        :return: Tuple (lat, lon) of cell center position.
        """
        def _get_center(i):
            lower = math.floor(2*i) / 2
            upper = math.ceil(2*i) / 2
            if lower == upper:
                upper += 0.5
            return (lower + upper) / 2
        return _get_center(lat), _get_center(lon)


