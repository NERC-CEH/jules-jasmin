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
from sqlalchemy import Column, Integer, String, Boolean
from joj.model import Base
from joj.utils import constants


class OutputVariable(Base):
    """
    JULES Output variable
    """

    __tablename__ = 'output_variables'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))
    description = Column(String(constants.DB_LONG_STRING_SIZE))
    depends_on_nsmax = Column(Boolean, default=False)

    def __repr__(self):
        """String representation"""

        return "<Parameter(name=%s)>" % self.name