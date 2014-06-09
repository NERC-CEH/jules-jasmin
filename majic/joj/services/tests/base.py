import unittest
from mock import Mock

__author__ = 'Phil Jenkins (Tessella)'

class BaseTest(unittest.TestCase):
    """Base class for service tests"""

    _mock_session = None

    def setUp(self):
        self._mock_session = Mock
