from contextlib import contextmanager
import unittest
from ecomaps.model.meta import Base, Session
from ecomaps.model import initialise_session, User, session_scope

__author__ = 'Phil Jenkins (Tessella)'



class ORMTests(unittest.TestCase):
    """Verifies that the ORM definitions work correctly on a fresh database"""

    _connectionstring = 'mysql+mysqlconnector://ecomaps-admin:U7gb1HmW@localhost/ecomaps_test'
    #_app_user_connectionstring = 'mysql+mysqlconnector://ecomaps-app:ecomapsx@localhost/ecomaps_test'

    def __init__(self, *args, **kwargs):

        super(ORMTests,self).__init__(*args, **kwargs)
        initialise_session(None, manual_connection_string=self._connectionstring)


    def tearDown(self):
        """Gets rid of the tables in the connected database"""

        # Blow the model away
        Base.metadata.drop_all(bind=Session.bind)


    def setUp(self):
        """Verifies that each of the model classes derived from declarative_base can be created"""

        Base.metadata.create_all(bind=Session.bind)

    def test_app_user_can_create(self):
        """Can the application user perform inserts?"""

        with session_scope(Session) as session:

            user = User()
            user.name = "Test User"
            session.add(user)

        with session_scope(Session) as another_session:

            count = another_session.query(User).count()
            self.assertEqual(count, 1, "Expected a single user")