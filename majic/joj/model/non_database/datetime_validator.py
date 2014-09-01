"""
header
"""
import datetime
from joj.utils import constants


class DatetimeValidator(object):
    """
    Validator for time and date strings
    """

    def __init__(self, errors):
        """
        Initialise
        :param errors: the errors dictionary to add to if there is an error
        :return: nothing
        """
        self._errors = errors

    def get_valid_datetime(self, key, values):
        """
        Return a valid date
        if there is a validation error add it to errors dictionary and return none
        :param key: the  key in values to get the date value
        :param values: values dictionary
        :return: datetime
        """
        if key not in values or values[key] == '':
            self._errors[key] = 'Please enter a date'
        else:
            date_str = values[key]
            try:
                return datetime.datetime.strptime(date_str, constants.USER_UPLOAD_DATE_FORMAT)
            except ValueError:
                self._errors[key] = 'Enter date as YYYY-MM-DD HH:MM'
            return None
