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

COMPLETED_SUBJECT_TEMPLATE = "Majic: {name} has completed"
COMPLETED_MESSAGE_TEMPLATE = \
    """
Hi {users_name},

Majic has successfully finished your model run.

   Name: {name}
   Description: {description}
   Link: {url}

Regards,

Majic
"""

FAILED_SUBJECT_TEMPLATE = "Majic: {name} has encountered an error"
FAILED_MESSAGE_TEMPLATE = \
    """
Hi {users_name},

Majic has encountered an error when running your model run.

   Name: {name}
   Description: {description}
   Link: {url}
   Error: {error_message}

Regards,

Majic
"""

UNKNOWN_SUBJECT_TEMPLATE = "Majic: {name} has encountered an unexpected problem"
UNKNOWN_MESSAGE_TEMPLATE = \
    """
Hi {users_name},

Majic has encountered an unexpected problem when running your model run.

   Name: {name}
   Description: {description}
   Link: {url}
   Unknown problem: {error_message}

Regards,

Majic
"""

GROUP_SPACE_FULL_ALERT_SUBJECT = "Majic: The group space is almost full"
GROUP_SPACE_FULL_ALERT_MESSAGE = \
    """
Hi Admin,

The group space that Majic uses to store model runs is almost full. Please delete some data or request more group space.

The size of the group space is the quota allocated to the system user.

Current space in GB: {current_quota}
Current used space in GB: {used_space}

Regards,

Majic
"""

ACCOUNT_REQUESTED_USER = "Dear %s,\r\n\r\n" \
                         "Your request for a Majic account has been passed on to the Majic admin team. " \
                         "Once it has been approved you will receive an email letting you know that an " \
                         "account has been created for you," \
                         "\r\n\r\nThanks for registering your interest with Majic!"

ACCOUNT_REQUESTED_ADMIN = "Dear Majic admin,\r\n\r\nThe following request for a Majic " \
                          "account has been received:\r\n\r\n" \
                          "Name: {first_name} {last_name}\r\n" \
                          "Email: {email}\r\n" \
                          "Institution: {institution}\r\n" \
                          "Expected usage: {usage}\r\n\r\n" \
                          "Please follow this link to review this user's request: \r\n" \
                          "{link}\r\n"

ACCOUNT_REQUEST_FULL = "Dear %s,\r\n\r\n" \
                       "Unfortunately we are unable to accept any more account requests for today. We're " \
                       "sorry for the inconvenience, please try again tomorrow."

ACCOUNT_REQUEST_REJECTED_SUBJECT = "Rejection of your Majic account request"
ACCOUNT_REQUEST_REJECTED_MESSAGE = """
Dear {first_name} {last_name},

Sorry your request for a Majic account has been rejected. The reason for reject was:

    {reason}

Regards,

Majic Admin Team
"""

ACCOUNT_REQUEST_ACCEPTED_SUBJECT = "Majic account creation"
ACCOUNT_REQUEST_ACCEPTED_MESSAGE = """
Dear {first_name} {last_name},

We have created you an account in Majic. To access the account please follow this link:

{link}

This link is only valid for the next 24 hours but if you visit this page after that time a new link will be sent to you.
If you did not request an account please ignore this email.

We hope you enjoy using the system.

Regards,

Majic Admin Team
"""

PASSWORD_RESET_SUBJECT = "Majic account password reset request"
PASSWORD_RESET_MESSAGE = """
Dear {name},

You may now reset your password in Majic. To do this please follow this link:

{link}

This link is only valid for the next 24 hours but if you visit this page after that time a new link will be sent to you.
If you did not request a password reset for this account please ignore this email.

Regards,

Majic Admin Team
"""

FAILED_SUBMIT_SUPPORT_SUBJECT_TEMPLATE = "Majic: Has failed to submit a job"
FAILED_SUBMIT_SUPPORT_MESSAGE_TEMPLATE = \
    """
Hi Support,

Majic has encountered an error when submitting a job:

   ID: {id}
   Name: {name}
   Description: {description}
   Error: {error_message}

This might be because the job runner is down temporarily or something more serious you should consider investigating.

Regards,

Majic
"""
