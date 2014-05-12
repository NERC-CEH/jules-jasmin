import base64
import datetime
import logging
import os
from ecomaps.crowd.models import UserRequest

import urllib2, simplejson

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class ClientException(Exception):
    """ Base exception for Crowd-based errors """

    def __init__(self):
        pass

class SessionNotFoundException(ClientException):
    """Use this for:
    + User session expiry
    + Nonsense user session etc."""

    def __init__(self):
        pass

class AuthenticationFailedException(ClientException):
    """If the user has entered incorrect details,
    we'll use this exception type"""

    def __init__(self):
        pass

class UserException(ClientException):
    """ Raised if a user already exists on create"""

    def __init__(self):
        pass

class CrowdCommunicationExcpetion(ClientException):

    def __init__(self):
        pass

class CrowdClient(object):
    """Provides a simple interface to a crowd server"""

    # Map the messages we expect back from Crowd in error
    # to an exception type we want to raise
    _errorMap = {
        'INVALID_SSO_TOKEN': SessionNotFoundException,
        'INVALID_USER_AUTHENTICATION': AuthenticationFailedException,
        'INVALID_USER': UserException
    }

    _token_cache = {}

    crowd_user = None
    crowd_password = None

    def __init__(self, api_url=None, app_name=None, app_pwd=None):
        """Constructor function
        Params:
            api_url: The URL to the Crowd API
            app_name: Application login name for Crowd server
            app_pwd: Application password for Crowd server
        """
        # Load up the config from file
        from ConfigParser import SafeConfigParser

        config = SafeConfigParser()
        config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini'))

        self.crowd_user = app_name or config.get('crowd', 'app_name')
        self.crowd_password = app_pwd or config.get('crowd', 'app_password')


        # Fall back to the config value if we haven't explicitly specified a URL
        # for the REST API, do the same for the application user and password too
        self.crowd_api = api_url or config.get('crowd', 'api_url')
        #password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        #password_mgr.add_password(None,
        #                          self.crowd_api,
        #                          app_name or config.get('crowd', 'app_name'),
        #                          app_pwd or config.get('crowd', 'app_password'))

        # Use this credentials for subsequent urllib2 requests to crowd
        #handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        #self.opener = urllib2.build_opener(handler)
        #self.opener_installed = False

    def check_authenticated(self, user_name, password):
        """Checks if the user in question is in the crowd system
            Params:
                user_name: Login name of the user to check
                password: That user's password
            Returns:
                User information as JSON if session valid,
                raises exception if not
        """
        # We'll either get the user back, or
        return self._make_request('authentication?username=%s' % user_name, '{ "value": "%s" }' % password)


    def create_user_session(self, user_name, password, remote_addr):
        """Asks the crowd provider for a user session token
            Params:
                user_name: Login name of the user
                password: Password of the user
                remote_addr: IP address the user is requesting from
            Returns:
                User object in JSON containing a 'token' from Crowd
                raises exception if invalid credentials
        """

        user = UserRequest()
        user.username = user_name
        user.password = password
        user.remote_address = remote_addr

        # Now we have enough information to make
        # a request to the Crowd API for a session
        return self._make_request('session', user.to_json())

    def verify_user_session(self, token):
        """Checks the supplied token against active Crowd sessions
            Params:
                token: The Crowd session ID to verify
            Returns:
                User information as JSON if session valid,
                raises exception if not
        """

        # Look for a user, and last access entry in the
        # cache...
        try:
            user, last_access_time = self._token_cache[token]

            time_since_last_access = datetime.datetime.now() - last_access_time

            if time_since_last_access.seconds > 20:

                del[self._token_cache[token]]

            else:

                log.debug("Found user in cache - no need to call Crowd")

                return {
                    'user': user,
                    'token': token
                }

        except KeyError:

            server_credentials = self._make_request('session/' + token)
            self._token_cache[token] = (server_credentials['user'], datetime.datetime.now())
            return server_credentials

        return self._make_request('session/' + token)

    def delete_session(self, token):
        """Invalidates the specified session
            Params:
                token: Session identifier to invalidate
            Returns: Nothing
        """
        self._make_request('session/' + token, method='DELETE')

    def get_user_info(self, username):
        """Gets a user object from Crowd
            Params:
                username: Name of user to get info for
            Returns: User JSON
        """

        return self._make_request('user?username=%s' % username)

    def create_user(self, username, first_name, last_name,
                    email, password):
        """Asks the client to create a user with the given information
            Params:
                username - login name for the user
                first_name - The name given to the user for use in an informal setting
                last_name - The name of the user's family
                email - Email address
                password - User's desired password
        """

        req = UserRequest()
        req.username = username
        req.first_name = first_name
        req.last_name = last_name
        req.email = email
        req.password = password

        return self._make_request('user', data=req.new_user_json())

    def update_user(self, username, first_name, last_name,
                    email, password):
        """Asks the client to update the user record"""

        req = UserRequest()
        req.username = username
        req.first_name = first_name
        req.last_name = last_name
        req.email = email
        req.password = password

        return self._make_request('user?username=%s' % username, data=req.new_user_json(), method='PUT')


    def delete_user(self, username):
        """ Performs a delete on a user
            Params:
                username: The login name of the user to delete
        """

        self._make_request('user?username=%s' % username, method='DELETE')

    def _make_request(self, resource, data=None, method=None):
        """Helper function for making requests to the Crowd REST API
            Params:
                resource: The REST resource to access
                data: Optional JSON payload
                method: The HTTP verb used for the request
            Returns:
                The JSON response from the Crowd server, or
                raises an exception if a problem was encountered
        """

        # Make sure we specify that we're sending JSON, otherwise Crowd
        # assumes XML
        log.debug("Making a request for %s" % resource)

        if data:
            # Request implicitly becomes a POST if data is attached
            request = urllib2.Request(self.crowd_api + resource, data)
            request.add_header("Content-type", "application/json")

        else:
            # This will be a GET request
            request = urllib2.Request(self.crowd_api + resource)

        # Ask for JSON in return
        request.add_header("Accept", "application/json")
        base64string = base64.encodestring('%s:%s' % (self.crowd_user, self.crowd_password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)

        if method:
            # Fancy verbs (like DELETE) can be dealt with here
            request.get_method = lambda: method

        #if not self.opener_installed:
            # If we haven't connected to Crowd yet,
            # make a dummy request in order to save our
            # application credentials
        #    try:
        #        self.opener.open(self.crowd_api + 'group/membership')
        #    except urllib2.HTTPError as h_ex:
        #        log.error("CROWD CONNECTION ISSUE: %s" % h_ex)
        #        raise CrowdCommunicationExcpetion()

            #urllib2.install_opener(self.opener)
            #self.opener_installed = True

        try:
            # We're finally ready to make the request...

            f = urllib2.urlopen(request)

            # 204 is officially "No Content", so we won't have
            # any JSON to load! This is expected for 'DELETE'
            # operations for example
            if f.code != 204:
                response = f.read()

                response_object = simplejson.loads(response) if response else None

                f.close()
            else:
                response_object = None

            return response_object

        except urllib2.HTTPError as h_ex:

            if hasattr(h_ex, "read"):
                # Interrogate the error response...
                err_response = simplejson.loads(h_ex.read())

                # Use this info to look up the exception we should raise
                reason = err_response['reason']

                try:
                    raise self._errorMap[reason]()
                except:
                    raise ClientException
            else:
                log.error("CROWD ERROR: %s" % h_ex)
                raise h_ex
