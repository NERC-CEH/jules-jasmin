"""
# header
"""


class InvalidTemporalExtent(Exception):
    """
    Exception class representing an invalid temporal extent
    """
    pass


class TemporalExtent(object):
    """
    Represents a temporal extent. Has boundary times set upon construction and has a user selected
    time extent which is validated to ensure it is contained inside of the boundary times.
    """

    def __init__(self, start_bound, end_bound):
        self._start_bound = self._start = start_bound
        self._end_bound = self._end = end_bound

    def set_start(self, start_time):
        """
        Set the starting time
        :param start_time: start Datetime
        :return:
        """
        if not self._start_bound <= start_time <= self._end_bound:
            raise InvalidTemporalExtent("Start time is outside the acceptable range")
        if not start_time <= self._end:
            raise InvalidTemporalExtent("Start time must be before the end time")
        self._start = start_time

    def set_end(self, end_time):
        """
        Set the end time
        :param end_time: end Datetime
        :return:
        """
        if not self._start_bound <= end_time <= self._end_bound:
            raise InvalidTemporalExtent("End time is outside the acceptable range")
        if not end_time >= self._start:
            raise InvalidTemporalExtent("Start time must be before the end time")
        self._end = end_time