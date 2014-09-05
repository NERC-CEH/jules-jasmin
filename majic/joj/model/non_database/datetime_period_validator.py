"""
header
"""
from joj.model.non_database.datetime_validator import DatetimeValidator


class DatetimePeriodValidator(object):
    """
    Validator for a date time period
    """

    def __init__(self, errors):
        """
        Initialise
        :param errors: a dictionary of errors to add to if there is a validation problem
        :return:
        """
        self._errors = errors
        self._dateTimeValidator = DatetimeValidator(errors)

    def get_valid_start_end_datetimes(self, start_key, end_key, values):
        """
        Retunr a start end datetime pair
        if there is an error add it to the error dictionary returning None for invalid date if there is one
        :param start_key: key the the start datetime
        :param end_key: key for the end datetime
        :param values: values dictionary
        :return: valid start end date pair or None if date can not be converted
        """

        start_date = self._dateTimeValidator.get_valid_datetime(start_key, values)
        end_date = self._dateTimeValidator.get_valid_datetime(end_key, values)

        if end_date is not None and start_date is not None:
            if start_date > end_date:
                self._errors[end_key] = 'End date must not be before the start date'

        return start_date, end_date