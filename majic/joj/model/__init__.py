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
from sqlalchemy import engine_from_config, create_engine, exc, event
from sqlalchemy.pool import Pool
from joj.model.meta import Session, Base
from contextlib import contextmanager
import logging

#import all the database models in so they can be built
from joj.model.account_request import AccountRequest
from joj.model.model_run_status import ModelRunStatus
from joj.model.model_file import ModelFile
from joj.model.model_run import ModelRun
from joj.model.code_version import CodeVersion
from joj.model.namelist_file import NamelistFile
from joj.model.namelist import Namelist
from joj.model.parameter import Parameter
from joj.model.parameter_value import ParameterValue
from joj.model.user import User
from joj.model.user_level import UserLevel
from joj.model.dataset_type import DatasetType
from joj.model.dataset import Dataset
from joj.model.driving_dataset_location import DrivingDatasetLocation
from joj.model.driving_dataset import DrivingDataset
from joj.model.driving_dataset_parameter_value import DrivingDatasetParameterValue
from joj.model.system_alert_email import SystemAlertEmail
from joj.model.land_cover_region import LandCoverRegion
from joj.model.land_cover_region_category import LandCoverRegionCategory
from joj.model.land_cover_action import LandCoverAction
from joj.model.land_cover_value import LandCoverValue

log = logging.getLogger(__name__)


def initialise_session(config, manual_connection_string=None):
    """
    Sets up our database engine and session

    :param config: The config object containing 'sqlalchemy.blah' items
    :param manual_connection_string: An alternate connection string
    :return:nothing
    """

    # Attach our engine to the session, either from the config file or
    # using a supplied string
    if manual_connection_string:
        engine = create_engine(manual_connection_string)
    else:
        engine = engine_from_config(config, 'sqlalchemy.')

    Session.configure(bind=engine)


@contextmanager
def session_scope(session_class=Session):
    """
    Provide a transactional scope that we can wrap around calls to the database
    use like with session_scope() as session
    :param session_class: session class to create a session from
    :return: nothing
    """

    session = session_class()

    try:
        # Give this session back to the 'with' block
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    """
    Test the sql connection before using it to avoid  "MySQL Connection not available" see JOJ101
    see http://stackoverflow.com/questions/7912731/mysql-server-has-gone-away-disconnect-handling-via-checkout-event-handler-does
    :param dbapi_connection: sql connection
    :param connection_record: record
    :param connection_proxy: proxy
    :return: nothing
    """
    logging.debug("***********ping_connection**************")
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        logging.debug("######## DISCONNECTION ERROR #########")
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        # connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()
    cursor.close()