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
        if start_time < self._start_bound:
            raise InvalidTemporalExtent("Start date cannot be earlier than %s" % self._start_bound.strftime("%Y-%m-%d"))
        elif start_time > self._end_bound:
            raise InvalidTemporalExtent("Start date cannot be later than %s" % self._end_bound.strftime("%Y-%m-%d"))
        elif start_time > self._end:
            raise InvalidTemporalExtent("Start date cannot be later than the end date")
        self._start = start_time

    def set_end(self, end_time):
        """
        Set the end time
        :param end_time: end Datetime
        :return:
        """
        if end_time < self._start_bound:
            raise InvalidTemporalExtent("End date cannot be earlier than %s" % self._start_bound.strftime("%Y-%m-%d"))
        elif end_time > self._end_bound:
            raise InvalidTemporalExtent("End date cannot be later than %s" % self._end_bound.strftime("%Y-%m-%d"))
        elif end_time < self._start:
            raise InvalidTemporalExtent("End date cannot be earlier than the start date")
        self._end = end_time

    def get_temporal_extent(self):
        """
        Get the selected time extent as an array
        :return:
        """
        return [self._start, self._end]