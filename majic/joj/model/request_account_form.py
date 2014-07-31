"""
# header
"""
from formencode import Schema, validators
from joj.utils import constants


class RequestAccountForm(Schema):
    """
    Validates data from the 'request account' form
    """

    allow_extra_fields = True
    filter_extra_fields = True

    first_name = validators.String(
        not_empty=True,
        max=constants.DB_STRING_SIZE,
        messages={'empty': 'Please enter a first name', 'missing': 'Please enter a first name'})
    last_name = validators.String(
        not_empty=True,
        max=constants.DB_STRING_SIZE,
        messages={'empty': 'Please enter a last name', 'missing': 'Please enter a last name'})
    email = validators.Email(not_empty=True, max=constants.DB_STRING_SIZE,
                             messages={'empty': 'Please enter an email',
                                       'missing': 'Please enter an email',
                                       'noAt': 'Please enter a valid email',
                                       'badUsername': 'Please enter a valid email',
                                       'badDomain': 'Please enter a valid email'})
    institution = validators.String(not_empty=True, max=constants.DB_STRING_SIZE,
                                    messages={'empty': 'Please enter your institution',
                                              'missing': 'Please enter your institution'})
    usage = validators.String(not_empty=True, max=constants.DB_LONG_STRING_SIZE,
                              messages={'empty': 'Please describe how you will use Majic',
                                        'missing': 'Please describe how you will use Majic'})
    license = validators.String(not_empty=True,
                                messages={'empty': 'You must agree to the Majic license',
                                          'missing' : 'You must agree to the Majic license'})