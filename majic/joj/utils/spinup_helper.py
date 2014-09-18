"""
header
"""
import datetime as dt
from dateutil.relativedelta import relativedelta
import math
from joj.utils import constants


class SpinupHelper(object):
    """
    Manages spin-up for model runs
    """

    def calculate_spinup_start(self, driving_start, run_start):
        """
        Calculate the spin-up start time for a run
        :param driving_start: Driving data start (datetime)
        :param run_start: Run start (datetime)
        :return: Spin-up start (datetime)
        """
        spinup_length = relativedelta(years=constants.SPINUP_DURATION_YEARS)
        spinup_start = run_start - spinup_length
        return max(driving_start, spinup_start)

    def calculate_spinup_end(self, spin_start, driving_end):
        """
        Calculate the spin-up end time for a run
        :param spin_start: Spin-up start (datetime)
        :param driving_end: Driving data end (datetime)
        :return: Spin-up start (datetime)
        """
        spinup_length = relativedelta(years=constants.SPINUP_DURATION_YEARS)
        spinup_start = spin_start + spinup_length
        return min(driving_end, spinup_start)

    def calculate_spinup_cycles(self, spin_start, spin_end):
        """
        Calculate the number of spin cycles to carry out
        :param spin_start: Spin-up start (datetime)
        :param spin_end:  Spin-up end (datetime)
        :return: Number of cycles to run
        """
        cycle_duration_secs = (spin_end - spin_start).total_seconds()
        desired_total_duration_secs = dt.timedelta(days=365 * constants.SPINUP_DURATION_YEARS).total_seconds()
        return int(math.ceil(float(desired_total_duration_secs) / cycle_duration_secs))