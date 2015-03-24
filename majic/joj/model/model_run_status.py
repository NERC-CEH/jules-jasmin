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

from joj.model.meta import Base
from sqlalchemy import Column, String, SmallInteger
from joj.utils import constants


class ModelRunStatus(Base):
    """
    The status of the model run

    IMPORTANT: This table is used by the majic web service too so if it changes make sure the changes do not conflict
    """

    __tablename__ = 'model_run_statuses'

    def __init__(self, name):
        """initialise
           -- name the name for the status
        """
        self.name = name

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))

    def is_published(self):
        """
        Is the ModelRunStatus published?
        :return: True if published, false otherwise
        """
        return self.name == constants.MODEL_RUN_STATUS_PUBLISHED

    def allow_publish(self):
        """
        Does the ModelRunStatus allow the ModelRun to be published?
        :return: True if a ModelRun can be published, false otherwise
        """
        return self.name == constants.MODEL_RUN_STATUS_COMPLETED

    def allow_visualise(self):
        """
        Does the ModelRunStatus allow the ModelRun to be visualised on the map?
        :return: True if the ModelRun can be visualised, false otherwise
        """
        return self.name == constants.MODEL_RUN_STATUS_COMPLETED or self.name == constants.MODEL_RUN_STATUS_PUBLISHED

    def allow_delete(self, user_is_admin):
        """
        Can a model run with this status be deleted
        :param user_is_admin: True if the user is an admin
        :return:True if run can be deleted, false otherwise
        """

        if self.name == constants.MODEL_RUN_STATUS_PUBLISHED:
            return user_is_admin

        return not (
            self.name == constants.MODEL_RUN_STATUS_PENDING or
            self.name == constants.MODEL_RUN_STATUS_SUBMITTED or
            self.name == constants.MODEL_RUN_STATUS_RUNNING)

    def get_display_color(self):
        """
        Gets the appropriate display color for the ModelRunStatus to be used on the User Interface
        :return: The ModelRunStatus display color as a hex string (#xxyyzz)
        """
        return {
            constants.MODEL_RUN_STATUS_COMPLETED: '#38761d',
            constants.MODEL_RUN_STATUS_PUBLISHED: '#711780',
            constants.MODEL_RUN_STATUS_SUBMITTED: '#f6b26b',
            constants.MODEL_RUN_STATUS_RUNNING: '#f6b26b',
            constants.MODEL_RUN_STATUS_PENDING: '#f6b26b',
            constants.MODEL_RUN_STATUS_FAILED: '#990000',
            constants.MODEL_RUN_STATUS_SUBMIT_FAILED: '#990000',
            constants.MODEL_RUN_STATUS_UNKNOWN: '#990000',
        }.get(self.name, '#000000')

    def __repr__(self):
        """String representation"""

        return "<ModelRunStatus(name=%s)>" % self.name
