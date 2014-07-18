"""
# Header
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
    def check_email_needs_sending(session, code):
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
