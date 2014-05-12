from contextlib import contextmanager
from ecomaps.model import Session

__author__ = 'Phil Jenkins (Tessella)'

class ServiceException(Exception):
    """Custom exception type for service calls"""

    pass


class DatabaseService(object):
    """Base class for all services that talk to a database

        Provides context manager scoped functions to wrap
        around database operations
    """

    _session = None

    def __init__(self, session=Session):
        """Creates a new instance of the database service
            Params:
                session: Session class to use
        """

        self._session = session

    @contextmanager
    def transaction_scope(self):
        """Provides a session instance that gets automatically committed once
            the end of the calling 'with' block is reached.

            e.g. To add and commit a new object to the database...

                with self.transaction_scope() as session:
                    object = Whatever()
                    object.property='1234'
                    session.add(object)

            Will roll back if an exception is encountered
        """

        session = self._session()

        try:
            yield session
            session.commit()
            session.expunge_all()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @contextmanager
    def readonly_scope(self):
        """Use this scope in a with block for a session that returns
            expunged objects - i.e. objects we can continue to access
            after the session is closed, ideal for reading data and
            displaying
        """

        session = self._session()

        try:
            yield session
        except:
            raise
        finally:

            # This will call session.expunge_all() internally
            session.close()