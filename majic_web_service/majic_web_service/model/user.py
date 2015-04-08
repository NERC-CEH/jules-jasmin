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
from sqlalchemy import Column, Integer, String

from majic_web_service.model.meta import Base
from majic_web_service.utils import constants


class User(Base):
    """
    A user of the system

    IMPORTANT: This table is based on the one in majic if it changes make sure the changes are reflected
    """

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(constants.DB_STRING_SIZE))
    workbench_username = Column(String(constants.DB_STRING_SIZE))

    def __repr__(self):
        """String representation of the user"""

        return "<User(username=%s, name=%s)>" % (self.username, self.name)
