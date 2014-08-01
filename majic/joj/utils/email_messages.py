"""
header
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
                          "Name: %s %s\r\n" \
                          "Email: %s\r\n" \
                          "Institution: %s\r\n" \
                          "Expected usage: %s\r\n\r\n" \
                          "Please login to Majic and review this user request"

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

We hope you enjoying using the system.

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
