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
from joj.model.meta import Base
from joj.utils import constants


class LandCoverValue(Base):
    """
    Represents the different possible land cover types (ice, urban etc).
    """

    __tablename__ = 'land_cover_values'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_LONG_STRING_SIZE))
    index = Column(Integer)

    def __repr__(self):
        return "<LandCoverValue(name=%s)>" % self.name