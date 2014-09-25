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
from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from joj.model.meta import Base
from joj.utils import constants


class LandCoverRegion(Base):
    """
    Represents a land cover mask for a specific region, e.g. 'Wales' or
    'River Thames catchment area'
    """

    __tablename__ = 'land_cover_regions'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_LONG_STRING_SIZE))
    mask_file = Column(String(constants.DB_PATH_SIZE))
    category_id = Column(Integer, ForeignKey('land_cover_region_categories.id'))

    category = relationship("LandCoverRegionCategory", backref=backref("regions", order_by=id))

    def __repr__(self):
        return "<LandCoverRegion(name=%s)>" % self.name
