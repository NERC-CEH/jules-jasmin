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
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, ForeignKey, Table, SmallInteger, Boolean
from joj.utils import constants

# table for many to many association between code and parameters
_parameter_code_version_association_table = \
    Table(
        'parameter_code_version_association',
        Base.metadata,
        Column('parameter', Integer, ForeignKey('parameters.id')),
        Column('code_version', SmallInteger, ForeignKey('code_versions.id'))
    )


class Parameter(Base):
    """A parameter for the Jules model
    This is the definition of a single parameter which the user may set for a given versions of the code
    """

    __tablename__ = 'parameters'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))
    description = Column(String(constants.DB_LONG_STRING_SIZE))

    default_value = Column(String(constants.DB_PARAMETER_VALUE_STRING_SIZE))
    type = Column(String(constants.DB_STRING_SIZE))
    required = Column(Boolean())
    min = Column(Integer)
    min_inclusive = Column(Boolean())
    max = Column(Integer)
    max_inclusive = Column(Boolean())

    #The url suffix to add to the url from the code version
    url_suffix = Column(String(constants.DB_LONG_STRING_SIZE))

    user_level_id = Column(Integer, ForeignKey('user_levels.id'))
    namelist_id = Column(Integer, ForeignKey('namelists.id'))

    parameter_values = relationship("ParameterValue", backref=backref('parameter', order_by=id))
    driving_data_parameter_values = relationship("DrivingDatasetParameterValue",
                                                 backref=backref('parameter', order_by=id))

    code_versions = relationship("CodeVersion", secondary=_parameter_code_version_association_table,
                                 backref="parameters")

    def __repr__(self):
        """String representation"""

        return "<Parameter(name=%s)>" % self.name
