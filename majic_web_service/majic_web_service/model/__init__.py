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

from sqlalchemy import exc, event
from sqlalchemy.pool import Pool
from contextlib import contextmanager
import logging

log = logging.getLogger(__name__)

"""The application's model objects"""
from majic_web_service.model.meta import Session, Base
from majic_web_service.model.model_run_status import ModelRunStatus
from majic_web_service.model.model_run import ModelRun
from majic_web_service.model.user import User


def init_model(engine):
    """
    Call me before using any of the tables or classes in the model
    :param engine: engine to bind for the session
    """
    Session.configure(bind=engine)


@contextmanager
def session_scope(session_class=Session):
    """
    Provide a transactional scope that we can wrap around calls to the database
    use ``with session_scope() as session``
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


@contextmanager
def readonly_scope(session_class=Session):
    """
    Use this scope in a with block for a session that returns
        expunged objects - i.e. objects we can continue to access
        after the session is closed, ideal for reading data and
        displaying
    :param session_class: session class to create a session from
    :return: nothing
    :yield: the session variable
    """

    session = session_class()
    try:
        yield session
    except:
        raise
    finally:
        # This will call session.expunge_all() internally
        session.close()


# noinspection PyUnusedLocal
@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    """
    Test the sql connection before using it to avoid  "MySQL Connection not available" see JOJ101
    see http://stackoverflow.com/questions/7912731/
        mysql-server-has-gone-away-disconnect-handling-via-checkout-event-handler-does
    :param dbapi_connection: sql connection
    :param connection_record: record
    :param connection_proxy: proxy
    :return: nothing
    :yield: the session variable
    """
    logging.debug("ping_connection")
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        logging.debug("DISCONNECTION ERROR")
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        # connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()
    cursor.close()