"""
# header
"""


class InvalidSpatialExtent(Exception):
    """
    Exception class representing an invalid spatial extent
    """
    pass


class SpatialExtent(object):
    """
    Represents a geographical spatial extent. Has a boundary area set upon construction and has a user selected
    extent area which is validated to ensure it is contained inside of the boundary area.
    """

    def __init__(self, lat_n, lat_s, lon_w, lon_e):
        """
        Constructor for a new SpatialExtent instance
        :param lat_n: The northern boundary latitude
        :param lat_s: The southern boundary latitude
        :param lon_w: The western boundary longitude
        :param lon_e: The eastern boundary latitude
        :return: a SpatialExtent instance with specified boundaries
        """
        if not lat_n > lat_s:
            raise InvalidSpatialExtent("Northern bounding latitude (%s deg N) must be north of southern "
                                       "bounding latitude (%s deg N)" % (lat_n, lat_s))
        if not (-90 <= lat_n <= 90 and -90 <= lat_s <= 90):
            raise InvalidSpatialExtent("Latitude must be between -90 and 90")
        if not lon_e > lon_w:
            raise InvalidSpatialExtent("Eastern bounding longitude (%s deg E) must be east of western "
                                       "bounding longitude (%s deg E)" % (lon_e, lon_w))
        if not (-180 <= lon_e <= 180 and -180 <= lon_w <= 180):
            raise InvalidSpatialExtent("Longitude must be between -180 and 180")
        self._lat_n = self._bound_lat_n = lat_n
        self._lat_s = self._bound_lat_s = lat_s
        self._lon_w = self._bound_lon_w = lon_w
        self._lon_e = self._bound_lon_e = lon_e

    def set_lon_e(self, lon_e):
        """
        Set the Eastern longitudinal extent
        :param lon_e: Eastern longitudinal extent
        :raise InvalidSpatialExtent: If the requested extent is out of bounds
        """
        if not (-180 <= lon_e <= 180):
            raise InvalidSpatialExtent("Longitude must be between -180 and 180")
        if lon_e > self._bound_lon_e:
            raise InvalidSpatialExtent("Eastern longitude (%s deg E) cannot be east of %s deg E"
                                       % (lon_e, self._bound_lon_e))
        if lon_e < self._bound_lon_w:
            raise InvalidSpatialExtent("Eastern longitude (%s deg E) cannot be west of %s deg E"
                                       % (lon_e, self._bound_lon_w))
        if lon_e < self._lon_w:
            raise InvalidSpatialExtent("Eastern longitude cannot be west of the western longitude")
        self._lon_e = lon_e

    def set_lon_w(self, lon_w):
        """
        Set the Western longitudinal extent
        :param lon_w: Western longitudinal extent
        :raise InvalidSpatialExtent: If the requested extent is out of bounds
        """
        if not (-180 <= lon_w <= 180):
            raise InvalidSpatialExtent("Longitude must be between -180 and 180")
        if lon_w > self._bound_lon_e:
            raise InvalidSpatialExtent("Western longitude (%s deg E) cannot be east of %s deg E"
                                       % (lon_w, self._bound_lon_e))
        if lon_w < self._bound_lon_w:
            raise InvalidSpatialExtent("Western longitude (%s deg E) cannot be west of %s deg E"
                                       % (lon_w, self._bound_lon_w))
        if lon_w > self._lon_e:
            raise InvalidSpatialExtent("Western longitude cannot be east of the eastern longitude")
        self._lon_w = lon_w

    def set_lat_n(self, lat_n):
        """
        Set the Northern latitudinal extent
        :param lat_n: Northern latitudinal extent
        :raise InvalidSpatialExtent: If the requested extent is out of bounds
        """
        if not (-90 <= lat_n <= 90):
            raise InvalidSpatialExtent("Latitude must be between -90 and 90")
        if lat_n > self._bound_lat_n:
            raise InvalidSpatialExtent("Northern latitude (%s deg N) cannot be north of %s deg N"
                                       % (lat_n, self._bound_lat_n))
        if lat_n < self._bound_lat_s:
            raise InvalidSpatialExtent("Northern latitude (%s deg N) cannot be south of %s deg N"
                                       % (lat_n, self._bound_lat_s))
        if lat_n < self._lat_s:
            raise InvalidSpatialExtent("Northern latitude cannot be south of the southern latitude")
        self._lat_n = lat_n

    def set_lat_s(self, lat_s):
        """
        Set the Southern latitudinal extent
        :param lat_s: Southern latitudinal extent
        :raise InvalidSpatialExtent: If the requested extent is out of bounds
        """
        if not (-90 <= lat_s <= 90):
            raise InvalidSpatialExtent("Latitude must be between -90 and 90")
        if lat_s > self._bound_lat_n:
            raise InvalidSpatialExtent("Southern latitude (%s deg N) cannot be north of %s deg N"
                                       % (lat_s, self._bound_lat_n))
        if lat_s < self._bound_lat_s:
            raise InvalidSpatialExtent("Southern latitude (%s deg N) cannot be south of %s deg N"
                                       % (lat_s, self._bound_lat_s))
        if lat_s > self._lat_n:
            raise InvalidSpatialExtent("Southern latitude cannot be north of the northern latitude")
        self._lat_s = lat_s

    def get_lat_bounds(self):
        """
        Get the latitude bounds as an array
        :return: lat_bounds [South, North]
        """
        return [self._lat_s, self._lat_n]

    def get_lon_bounds(self):
        """
        Get the longitude bounds as an array
        :return: lon_bounds [West, East]
        """
        return [self._lon_w, self._lon_e]