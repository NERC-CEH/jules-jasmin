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
from joj.model import Base
from joj.utils import constants


class AccountRequest(Base):
    """A request for a system account"""

    __tablename__ = 'account_request'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(constants.DB_STRING_SIZE))
    last_name = Column(String(constants.DB_STRING_SIZE))
    email = Column(String(constants.DB_STRING_SIZE))
    institution = Column(String(constants.DB_STRING_SIZE))
    usage = Column(String(constants.DB_LONG_STRING_SIZE))

    def __repr__(self):
        """String representation of the account request"""
        return "<AccountRequest(name=%s %s, email=%s)>" % (self.first_name, self.last_name, self.email)