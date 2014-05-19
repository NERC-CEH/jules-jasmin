import formencode

__author__ = 'Phil Jenkins (Tessella)'


class LoginForm(formencode.Schema):
    """Encapsulates the fields in the login form"""

    allow_extra_fields = True
    filter_extra_fields = True

    login = formencode.validators.NotEmpty()
    password = formencode.validators.String(not_empty=True)
