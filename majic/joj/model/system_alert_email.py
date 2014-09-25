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

from joj.model.meta import Base
from sqlalchemy import Column, String, SmallInteger, DateTime, Integer
from joj.utils import constants
from datetime import datetime, timedelta


class SystemAlertEmail(Base):
    """Keeping track of system alerts and when they were sent
    """

    __tablename__ = 'system_alerts_emails'

    GROUP_SPACE_FULL_ALERT = 'GROUP_SPACE_FULL'

    id = Column(SmallInteger, primary_key=True)
    code = Column(String(constants.DB_STRING_SIZE))
    last_sent = Column(DateTime, default=None)
    sent_frequency_in_s = Column(Integer)

    def __repr__(self):
        """String representation"""

        return "<SystemAlertEmail(code=%s)>" % self.code

    @staticmethod
    def check_email_needs_sending(code, session):
        """
        Check whether the system email needs sending, it will not be sent if it was sent within the last sent frequency
        :param code: the email code to look for
        :param session: session to use to lookup the email status
        :return: True if the email needs sending
        """

        email = session.query(SystemAlertEmail) \
            .filter(SystemAlertEmail.code == code) \
            .one()
        return email.last_sent is None \
            or email.last_sent + timedelta(seconds=email.sent_frequency_in_s) < datetime.now()
