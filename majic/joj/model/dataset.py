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
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship, backref
from joj.model.meta import Base


class Dataset(Base):
    """Metadata from a map dataset"""

    __tablename__ = 'datasets'

    column_names = []

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    wms_url = Column(String(255))
    netcdf_url = Column(String(255))
    low_res_url = Column(String(255))
    dataset_type_id = Column(Integer, ForeignKey('dataset_types.id'))
    viewable_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    data_range_from = Column(Float, default=1)
    data_range_to = Column(Float, default=50)
    is_categorical = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)
    is_input = Column(Boolean, default=False)
    model_run_id = Column(Integer, ForeignKey('model_runs.id'))
    dataset_type = relationship("DatasetType", backref="datasets", lazy="joined")

    model_run = relationship("ModelRun", backref=backref('datasets', order_by=id))

    def __init__(self, id=None):

        self.id = id

    def __repr__(self):
        """String representation of the Dataset class"""

        return "<Dataset(name=%s, wms_url=%s, netcdf_url=%s, dataset_type_id=%s)>" \
            % (
                self.name,
                self.wms_url,
                self.netcdf_url,
                self.dataset_type_id
            )
