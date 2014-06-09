#header

from contextlib import contextmanager
import unittest
from joj.model.meta import Base, Session
from joj.model import initialise_session, User, session_scope
from paste.deploy import loadapp
from joj.tests import conf_dir

class ORMTests(unittest.TestCase):
    """Verifies that the ORM definitions work correctly on a fresh database"""

    def __init__(self, *args, **kwargs):

        wsgiapp = loadapp('config:test.ini', relative_to=conf_dir)
        config = wsgiapp.config
        super(ORMTests,self).__init__(*args, **kwargs)
        initialise_session(None, manual_connection_string=config['sqlalchemy.url'])


    def tearDown(self):
        """Gets rid of the tables in the connected database"""

        # Blow the model away
        Base.metadata.drop_all(bind=Session.bind)


    def setUp(self):
        """Verifies that each of the model classes derived from declarative_base can be created"""

        Base.metadata.drop_all(bind=Session.bind)
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