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

class DrivingDatasetLocation(Base):
    """Metadata from a map dataset"""

    __tablename__ = 'driving_dataset_locations'

    column_names = []

    id = Column(Integer, primary_key=True)
    base_url = Column(String(constants.DB_URL_STRING_SIZE))
    var_name = Column(String(constants.DB_STRING_SIZE))

    driving_dataset_id = Column(Integer, ForeignKey('driving_datasets.id'))
    driving_dataset = relationship("DrivingDataset", backref=backref('locations', order_by=id))

    dataset_type_id = Column(Integer, ForeignKey('dataset_types.id'))
    dataset_type = relationship("DatasetType", lazy="joined")

    def __repr__(self):
        """String representation of the Dataset class"""

        return "<DrivingDatasetLocation(base_url=%s)>" \
            % (
                self.base_url
            )
