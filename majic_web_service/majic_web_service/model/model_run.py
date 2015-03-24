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

from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, ForeignKey
from majic_web_service.model.meta import Base
from majic_web_service.utils import constants
from majic_web_service.utils.constants import JSON_MODEL_RUN_ID, JSON_LAST_STATUS_CHANGE, JSON_IS_PUBLISHED, \
    JSON_USER_NAME


class ModelRun(Base):
    """
    A single run of a model with just the properties needed for the web service.

    IMPORTANT: This table is based on the one in majic if it changes make sure the changes are reflected
    """

    __tablename__ = 'model_runs'

    id = Column(Integer, primary_key=True)
    name = Column(String(constants.DB_STRING_SIZE))
    description = Column(String(constants.DB_LONG_STRING_SIZE))
    user_id = Column(Integer, ForeignKey('users.id'))
    last_status_change = Column(DateTime)
    status_id = Column(SmallInteger, ForeignKey('model_run_statuses.id'))

    user = relationship("User", backref=backref('model_runs', order_by=id))
    status = relationship("ModelRunStatus", backref=backref('model_runs', order_by=id), lazy="joined")

    def __json__(self):
        return {
            JSON_MODEL_RUN_ID: self.id,
            JSON_USER_NAME: self.user.username,
            JSON_IS_PUBLISHED: self.status.is_published(),
            JSON_LAST_STATUS_CHANGE: self.last_status_change}

    def __repr__(self):
        """ String representation of the model run """
        return "<ModelRun(name=%s, last_changed=%s)>" % (self.name, self.last_status_change)
