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
from sqlalchemy import Column, String, SmallInteger

from majic_web_service.model.meta import Base
from majic_web_service.utils import constants


class ModelRunStatus(Base):
    """
    The status of the model run

    IMPORTANT: This table is based on the one in majic if it changes make sure the changes are reflected
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
        return self.name == constants.MODEL_RUN_STATUS_PUBLISHED or self.name == constants.MODEL_RUN_STATUS_PUBLIC

    def is_public(self):
        """
        Is the ModelRunStatus public?
        :return: True if public, false otherwise
        """
        return self.name == constants.MODEL_RUN_STATUS_PUBLIC

    def __repr__(self):
        """String representation"""

        return "<ModelRunStatus(name=%s)>" % self.name
