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
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from joj.model.meta import Base
from joj.utils import constants


class LandCoverRegionCategory(Base):
    """
    Represents a category of land cover regions e.g. 'River catchments' or 'Countries'
    """

    __tablename__ = 'land_cover_region_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_LONG_STRING_SIZE))
    driving_dataset_id = Column(Integer, ForeignKey('driving_datasets.id'))

    driving_dataset = relationship("DrivingDataset", backref=backref("land_cover_region_categories", order_by=id))

    def __repr__(self):
        return "<LandCoverRegionType(name=%s)>" % self.name
