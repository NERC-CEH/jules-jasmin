# header


class InvalidSpatialExtent(Exception):
    """
    Exception class representing an invalid spatial extent
    """


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
        self._lat_n = self._bound_lat_n = lat_n
        self._lat_s = self._bound_lat_s = lat_s
        self._lon_w = self._bound_lon_w = lon_w
        self._lon_e = self._bound_lon_e = lon_e

    def set_lon(self, lon_w, lon_e):
        """
        Set the longitudinal extents. Extent area is from west to east
        :param lon_w: Western bounding longitude
        :param lon_e: Eastern longitude
        :raise InvalidSpatialExtent: If the requested extent is out of bounds
        """
        if not (-180 <= lon_e <= 180 and -180 <= lon_w <= 180):
            raise InvalidSpatialExtent("Longitude must be between -180 and 180")
        # The case where we have -180 -> +180 is a special case where anything is acceptable
        if not (self._bound_lon_w == -180 and self._bound_lon_e == 180):
            # Create some new variables so we can change their value without losing the originals
            _bound_lon_e = self._bound_lon_e
            _bound_lon_w = self._bound_lon_w
            _lon_e = lon_e
            _lon_w = lon_w
            # If the western bounding longitude is bigger than the eastern bounding longitude
            # that means the dateline was crossed somewhere in between
            if _bound_lon_w > self._bound_lon_e:
                # Any lines of longitude that have crossed the dateline need to have 360 degrees added to them
                _bound_lon_e += 360
                if _bound_lon_w > _lon_e:
                    _lon_e += 360
                if _bound_lon_w > _lon_w:
                    _lon_w += 360
            # The points should be in this order:
            if not (_bound_lon_w <= _lon_w <= _lon_e <= _bound_lon_e):
                raise InvalidSpatialExtent("Longitude must not be outside of the spatial extent")
        self._lon_w = lon_w
        self._lon_e = lon_e

    def set_lat(self, lat_n, lat_s):
        """
        Set the latitudinal extents.
        :param lat_n: Northern bounding latitude
        :param lat_s: Southern bounding latitude
        :return: InvalidSpatialExtent: If the requested extent is out of bounds
        """
        if not (-90 <= lat_n <= 90 and -90 <= lat_s <= 90):
            raise InvalidSpatialExtent("Latitude must be between -90 and 90")
        if not (self._bound_lat_s <= lat_s <= self._bound_lat_n and self._bound_lat_s <= lat_n <= self._bound_lat_n):
            raise InvalidSpatialExtent("Latitude must not be outside of the spatial extent")
        if lat_s > lat_n:
            raise InvalidSpatialExtent("The northern extent must be north of the southern extent")
        self._lat_n = lat_n
        self._lat_s = lat_s

    def get_lat_bounds(self):
        """
        Get the latitude bounds as an array
        :return: lat_bounds
        """
        return [self._lat_n, self._lat_s]

    def get_lon_bounds(self):
        """
        Get the longitude bounds as an array
        :return: lon_bounds
        """
        return [self._lon_w, self._lon_e]