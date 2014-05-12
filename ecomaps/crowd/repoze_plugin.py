import logging
from ecomaps.crowd.client import CrowdClient, ClientException
from zope.interface import directlyProvides
from repoze.who.interfaces import IChallengeDecider

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class CrowdRepozePlugin(object):
    """Implementation of a repoze.who plugin which communicates
        with our Crowd client.

        The functions within will be called by repoze.who
        at various stages of the request/response cycle,
        if the who middleware is active and configured with
        this plugin
    """
    _user = None

    def __init__(self):
        """Constructor"""

        # Set up the bits we need
        self._client = CrowdClient()
        self._cookie_name = 'gwgj9gj38g9d'

    def authenticate(self, environ, identity):
        """Authenticates the user supplied against Crowd
            Params:
                environ: The WSGI environment
                identity: Information about the user,
                            which may include login/password
                             or login/token if a session is active
            Returns:
                Name of successfully authenticated user, or None
        """
        try:

            log.debug("--> Repoze authenticate")

            # Do we have an active session already?
            if 'token' in identity:

                log.debug("--> Already got a token, returning %s" % identity['login'])

                # If so, we can just return the user name
                return identity['login']

            # Otherwise, it's a trip to Crowd to authenticate

            log.debug("--> No token")
            username = identity['login']
            password = identity['password']

            user = self._client.check_authenticated(username, password)

            log.debug("--> Auth result %s" % user)

            self._user = user
            return user['name']

        except KeyError:
            return None
        except ClientException as ex:
            log.error("Error authenticating %s with Crowd: %s" % (identity['login'],ex))
            return None

    def add_metadata(self, environ, identity):
        """Placeholder to add metadata to the user object
            if we so desire"""
        pass

    def identify(self, environ):
        """Verifies the user's identity in crowd
            Params:
                environ: The WSGI environment
            Returns:
                A dictionary containing 'login' and 'token' entries if
                a valid session is active, otherwise None.
        """

        # Do we have an active session?
        token = self._get_token_value(environ)

        if not token:
            return None

        try:

            log.debug("Checking user session with token: %s" % token)
            # Verify the session is still valid...
            user_obj = self._client.verify_user_session(token)

            log.debug("User OK: %s" % user_obj)
            # It is - so return the expected data structure
            return {
                "login": user_obj['user']['name'],
                "token": user_obj['token']
            }
        except ClientException:
            # Session is invalid or deleted
            log.debug("User session no longer valid")
            return None

    def remember(self, environ, identity):
        """Called once authentication is successful, asks us to "remember" the
            details for future identity queries
            Params:
                    environ: WSGI environment
                    identity: May be login/password or login/token
        """
        username = identity['login']

        # We have a token passed in already
        if 'token' in identity:
            token = identity['token']

            # Make sure it is still valid, kick out if not
            if not self.identify(environ):
                return None
        else:
            # No token, so username and password should be present
            password = identity['password']

            # What IP is the user requesting from?
            remote_address = environ['REMOTE_ADDR']

            # Ask Crowd for a session, which gives us a token ID
            user_object = self._client.create_user_session(username, password, remote_address)
            token = user_object['token']

            # Now pull out the user information
            user_info = self._client.get_user_info(username)

            # We'll use these in case we need to add to a local database
            environ['user.name'] = user_info['display-name']
            environ['user.email'] = user_info['email']
            environ['user.username'] = username
            environ['user.first-name'] = user_info['first-name']
            environ['user.last-name'] = user_info['last-name']

        # Set a cookie in the user's browser by returning the correct header instruction
        cookie_val = "%s" % token
        set_cookie = '%s=%s; Path=/;' % (self._cookie_name, cookie_val)
        return [(str('Set-Cookie'), str(set_cookie))]

    def forget(self, environ, identity):
        """Reverse of remember, will remove any reference to a previously-active
        Crowd Session
            Params:
                environ: WSGI environment
                identity: User info (not used)
        """

        # Pull out the session token
        token = self._get_token_value(environ)

        if token:
            # Ask Crowd to invalidate this session
            self._client.delete_session(token)

        # return a expires Set-Cookie header to the browser
        expired = ('%s=""; Path=/; Expires=Sun, 10-May-1971 11:59:00 GMT' %
                   self._cookie_name)
        return [('Set-Cookie', expired)]

    def _get_token_value(self, environ):
        """Gets the token value stored in the cookie"""

        from paste.request import get_cookies
        cookies = get_cookies(environ)
        cookie = cookies.get(self._cookie_name)

        if cookie is None:
            return None

        token = cookie.value

        return token

def crowd_challenge_decider(environ, status, headers):
    """Inspects each request and decides whether to challenge for authentication
    this is an implementation for repoze.who
        Params:
            environ: WSGI environment
            status: The HTTP status message
            headers: Any HTTP headers in the request
        Returns:
            True if a challenge should be made, otherwise False
    """

    # Are we logging in anyway? So we don't get caught in an infinite loop,
    # don't challenge for the login controller
    if 'login' in environ.get('PATH_INFO'):
        return False
    else:
        # The middleware should populate REMOTE_USER
        # if a valid user is logged in, so raise a challenge
        # if this is not found
        return (status.startswith('401') or
                environ.get('REMOTE_USER') is None)

# Let zope know we're a challenge decider
directlyProvides(crowd_challenge_decider, IChallengeDecider)