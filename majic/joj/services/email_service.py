"""
#header
"""
from _socket import timeout
import logging
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr
from smtplib import SMTP, SMTPException
from pylons import config

log = logging.getLogger(__name__)


class EmailService(object):
    """
    Service to create and send emails
    """

    def __init__(self, configuration=None):
        if configuration is None:
            self._config = config
        else:
            self._config = configuration

    def send_email(self, sender, recipient, subject, body):
        """
        Send an email
        :param sender: the senders address
        :param recipient: the recipients address
        :param subject: the emails subject
        :param body: the body of the email
        :return: nothing
        """
        # Header class is smart enough to try US-ASCII, then the charset we
        # provide, then fall back to UTF-8.
        header_charset = 'ISO-8859-1'

        # We must choose the body charset manually
        body_charset = None
        for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
            try:
                body.encode(body_charset)
            except UnicodeError:
                pass
            else:
                break

        if body_charset is None:
            log.error("Can not encode body of an email")
            raise Exception("Email body encoding problem for email with subject{}".format(subject))

        # Split real name (which is optional) and email address parts
        sender_name, sender_addr = parseaddr(sender)
        recipient_name, recipient_addr = parseaddr(recipient)

        # We must always pass Unicode strings to Header, otherwise it will
        # use RFC 2047 encoding even on plain ASCII strings.
        sender_name = str(Header(unicode(sender_name), header_charset))
        recipient_name = str(Header(unicode(recipient_name), header_charset))

        # Make sure email addresses do not contain non-ASCII characters
        sender_addr = sender_addr.encode('ascii')
        recipient_addr = recipient_addr.encode('ascii')

        # Create the message ('plain' stands for Content-Type: text/plain)
        msg = MIMEText(body.encode(body_charset), 'plain', body_charset)
        msg['From'] = formataddr((sender_name, sender_addr))
        msg['To'] = formataddr((recipient_name, recipient_addr))
        msg['Subject'] = Header(unicode(subject), header_charset)

        try:
            # Send the message via SMTP to localhost:25
            smtp = SMTP(self._config['email.smtp_server'], port=self._config['email.smtp_port'], timeout=1)
            smtp.sendmail(sender, recipient, msg.as_string())
            smtp.quit()
        except KeyError:
            log.warn("There is no smtp server set in the config file.")
        except timeout:
            log.error("There is smtp timeout error message not sent.")
            log.error("Message was %s" % str(msg))
        except SMTPException, ex:
            log.error("There is smtp error. Message not sent: %s." % str(ex))
            log.error("Message was %s" % str(msg))
        except Exception, ex:
            log.error("There is a general exception when sending an email. Message not sent: %s." % str(ex))
            log.error("Message was %s" % str(msg))
