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


from joj.model.meta import Base
from sqlalchemy import Column, String, SmallInteger, Boolean
from joj.utils import constants


class CodeVersion(Base):
    """The version of the Jules code to be run
    """

    __tablename__ = 'code_versions'

    id = Column(SmallInteger, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))
    is_default = Column(Boolean)
    url_base = Column(String(constants.DB_URL_STRING_SIZE))

    def __repr__(self):
        """String representation of the code version"""

        return "<CodeVersion(name=%s)>" % self.name
