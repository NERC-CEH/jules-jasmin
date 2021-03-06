"""
#    Majic
#    Copyright (C) 2014  CEH
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
import datetime as dt
from dateutil.relativedelta import relativedelta
import math

from joj.utils import constants


class SpinupHelper(object):
    """
    Manages spin-up for model runs
    """

    def calculate_spinup_start(self, driving_start, run_start, duration_in_years):
        """
        Calculate the spin-up start time for a run
        :param driving_start: Driving data start (datetime)
        :param run_start: Run start (datetime)
        :param duration_in_years: Duration in years
        :return: Spin-up start (datetime)
        """
        duration = min(duration_in_years, constants.SPINUP_MAX_TIME_RANGE_YEARS)
        spinup_length = relativedelta(years=duration)
        spinup_start = run_start - spinup_length
        return max(driving_start, spinup_start)

    def calculate_spinup_end(self, spin_start, driving_end, duration_in_years):
        """
        Calculate the spin-up end time for a run
        :param spin_start: Spin-up start (datetime)
        :param driving_end: Driving data end (datetime)
        :param duration_in_years: Duration in years
        :return: Spin-up start (datetime)
        """
        duration = min(duration_in_years, constants.SPINUP_MAX_TIME_RANGE_YEARS)
        spinup_length = relativedelta(years=duration)
        spinup_end = spin_start + spinup_length
        return min(driving_end, spinup_end)

    def calculate_spinup_cycles(self, spin_start, spin_end, duration_in_years):
        """
        Calculate the number of spin cycles to carry out
        :param spin_start: Spin-up start (datetime)
        :param spin_end:  Spin-up end (datetime)
        :param duration_in_years: Duration in years
        :return: Number of cycles to run
        """
        cycle_duration_secs = (spin_end - spin_start).total_seconds()
        desired_total_duration_secs = dt.timedelta(days=365 * duration_in_years).total_seconds()
        return int(math.ceil(float(desired_total_duration_secs) / cycle_duration_secs))