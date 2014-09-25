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

from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from joj.model.meta import Base
from joj.utils import constants


class ModelFile(Base):
    """ Represents an input or output file used in a model run """

    __tablename__ = 'model_files'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))
    path = Column(String(constants.DB_PATH_SIZE))
    is_input = Column(Boolean)
    model_run_id = Column(Integer, ForeignKey('model_runs.id'))

    def __repr__(self):
        """ String representation of the Model File"""

        return "<ModelFile(name=%s, path=%s)>" % (self.name, self.path)