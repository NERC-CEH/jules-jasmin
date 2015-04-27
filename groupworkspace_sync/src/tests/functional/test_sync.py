"""
#    Majic
#    Copyright (C) 2015  CEH
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
import unittest

from hamcrest import *

from sync.synchroniser import Synchroniser
from tests.test_mother import ConfigMother


class MyTestCase(unittest.TestCase):

    def test_GIVEN_majic_is_down_WHEN_sync_THEN_error_message_returned(self):
        config = ConfigMother.incorrect_webservice_configured()
        sync = Synchroniser(config)

        result = sync.synchronise()

        assert_that(result, is_not(0))


if __name__ == '__main__':
    unittest.main()
