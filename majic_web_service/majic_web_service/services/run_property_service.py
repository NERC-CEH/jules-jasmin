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
import logging
from sqlalchemy import asc, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from majic_web_service.model import readonly_scope, ModelRun, User, ModelRunStatus
from majic_web_service.utils.constants import MODEL_RUN_STATUS_COMPLETED, MODEL_RUN_STATUS_PUBLISHED, \
    MODEL_RUN_STATUS_PUBLIC

log = logging.getLogger(__name__)


class ServiceException(Exception):
    """
    Exception thrown when there is a problem in the service
    """
    pass


class RunPropertyService(object):
    """
    Service to access model run properties
    """

    def list(self):
        """
        List all the model runs with their properties that are completed or published
        :return: list of model runs with their properties
        """
        with readonly_scope() as session:
            try:
                return session \
                    .query(ModelRun) \
                    .join(User) \
                    .join(ModelRunStatus) \
                    .order_by(asc(ModelRun.last_status_change), asc(ModelRun.id)) \
                    .options(joinedload('user')) \
                    .options(joinedload('status')) \
                    .filter(or_(ModelRunStatus.name == MODEL_RUN_STATUS_COMPLETED,
                                ModelRunStatus.name == MODEL_RUN_STATUS_PUBLISHED,
                                ModelRunStatus.name == MODEL_RUN_STATUS_PUBLIC)) \
                    .all()
            except NoResultFound:
                return []
            except:
                log.exception("Problems accessing model runs in the database")
                raise ServiceException("Problems accessing model runs in the database")
