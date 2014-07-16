"""
# header
"""
import formencode

__author__ = 'Chirag Mistry (Tessella)'


class UpdateUserForm(formencode.Schema):
    """
    Schema used to validate update users form
    """
    allow_extra_fields = True
    filter_extra_fields = False

    first_name = formencode.validators.String(not_empty=True, max=50)
    last_name = formencode.validators.String(not_empty=True, max=50)
    email = formencode.validators.Email(not_empty=True, max=255)
    is_admin = formencode.validators.Bool()
    storage_quota = formencode.validators.Int(not_empty=True, min=1)


class CreateUserForm(UpdateUserForm):
    """Used to validate data from the Create New User page"""

    allow_extra_fields = False
    filter_extra_fields = True

    user_name = formencode.validators.String(not_empty=True)