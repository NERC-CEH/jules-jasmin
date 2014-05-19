import simplejson

__author__ = 'Phil Jenkins (Tessella)'


class UserRequest(object):

    def __init__(self):
        self._user_name = ""
        self._password = ""
        self._validation_factors = []
        self._remote_address = ""
        self._first_name = ""
        self._last_name = ""
        self._email = ""

    @property
    def username(self):
        return self._user_name
    @username.setter
    def username(self, u):
        self._user_name = u

    @property
    def password(self):
        return self._password
    @password.setter
    def password(self, p):
        self._password = p

    @property
    def remote_address(self):
        return self._remote_address
    @remote_address.setter
    def remote_address(self, r):
        self._remote_address = r

    @property
    def first_name(self):
        return self._first_name
    @first_name.setter
    def first_name(self, f):
        self._first_name = f

    @property
    def last_name(self):
        return self._last_name
    @last_name.setter
    def last_name(self, l):
        self._last_name = l

    @property
    def email(self):
        return self._email
    @email.setter
    def email(self, e):
        self._email = e

    def to_json(self):

        return simplejson.dumps(
            {
                'username': self.username,
                'password': self.password,
                'validation-factors': dict(validationFactors=[dict(name="remote_address", value=self.remote_address)])
            }
        )

    def new_user_json(self):

        return simplejson.dumps(
            {
                'name': self.username,
                'first-name': self.first_name,
                'last-name': self.last_name,
                'display-name': "%s %s" % (self.first_name, self.last_name),
                'email': self.email,
                'password': {
                    'value': self.password
                },
                'active': 'true'
            }
        )