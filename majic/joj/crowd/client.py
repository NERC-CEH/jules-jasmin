"""
#header
"""
import base64
import datetime
import logging
from joj.crowd.models import UserRequest
import urllib2
import simplejson
from simplejson import JSONDecodeError

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
    """
    Raised if crowd can not be contacted
    """
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

        self.crowd_user = app_name
        self.crowd_password = app_pwd
        self.crowd_api = api_url
        self.use_crowd = None
        self.external_opener = urllib2.build_opener(urllib2.HTTPHandler(), urllib2.ProxyHandler({}))

    def config(self, config):
        """
        Configure the crowd client
        :param config:
        :return:nothing
        """
        self.crowd_user = config['crowd_app_name']
        self.crowd_password = config['crowd_app_password']
        self.crowd_api = config['crowd_api_url']
        self.use_crowd = config['crowd_use_crowd'].lower() != 'false'
        try:
            self.external_opener = urllib2.build_opener(
                urllib2.ProxyHandler({'http': config['external_http_proxy'],
                                      'https': config['external_https_proxy']})
            )
            log.info("installed proxied external opener for crowd client")
        except KeyError:
            self.external_opener = urllib2.build_opener(urllib2.HTTPHandler(), urllib2.ProxyHandler({}))
            log.info("installed non-proxied external opener for crowd client")

    def check_authenticated(self, user_name, password):
        """
        Checks if the user in question is in the crowd system

        :param user_name: Login name of the user to check
        :param password: That user's password
        :return: User information as JSON if session valid,
                raises exception if not
        """
        return self._make_request('authentication?username=%s' % user_name, '{ "value": "%s" }' % password)

    def create_user_session(self, user_name, password, remote_addr):
        """
        Asks the crowd provider for a user session token
        :param user_name: Login name of the user
        :param password: Password of the user
        :param remote_addr: IP address the user is requesting from
        :return: User object in JSON containing a 'token' from Crowd
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
        """
        Checks the supplied token against active Crowd sessions
        :param token: The Crowd session ID to verify
        :return: User information as JSON if session valid,
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
        """
        Invalidates the specified session

        :param token: Session identifier to invalidate
        :return:Nothing
        """
        if token in self._token_cache:
            del[self._token_cache[token]]
        self._make_request('session/' + token, method='DELETE')

    def get_user_info(self, username):
        """
        Gets a user object from Crowd

        :param username: Name of user to get info for
        :return: User JSON
        """

        return self._make_request('user?username=%s' % username)

    def create_user(self, username, first_name, last_name, email, password):
        """
        Asks the client to create a user with the given information
        :param username: login name for the user
        :param first_name: The name given to the user for use in an informal setting
        :param last_name: The name of the user's family
        :param email: Email address
        :param password: User's desired password
        :return: nothing
        """

        req = UserRequest()
        req.username = username
        req.first_name = first_name
        req.last_name = last_name
        req.email = email
        req.password = password

        return self._make_request('user', data=req.new_user_json())

    def update_user(self, username, first_name, last_name, email, password):
        """
        Asks the client to update the user record
        :param username: login name for the user
        :param first_name: The name given to the user for use in an informal setting
        :param last_name: The name of the user's family
        :param email: Email address
        :param password: User's desired password
        :return: nothing
        """

        req = UserRequest()
        req.username = username
        req.first_name = first_name
        req.last_name = last_name
        req.email = email
        req.password = password

        return self._make_request('user?username=%s' % username, data=req.new_user_json(), method='PUT')

    def update_users_password(self, username, password):
        """
        Update a users password
        :param username: the username
        :param password: the new password
        :return:nothing
        """
        data = simplejson.dumps(
            {
                'value': password
            })
        return self._make_request('user/password?username=%s' % username, data=data, method='PUT')

    def delete_user(self, username):
        """
        Performs a delete on a user

        :param username: The login name of the user to delete
        :return: nothing
        """

        self._make_request('user?username=%s' % username, method='DELETE')

    def _make_request(self, resource, data=None, method=None):
        """
        Helper function for making requests to the Crowd REST API

        :param resource: The REST resource to access
        :param data: Optional JSON payload
        :param method: The HTTP verb used for the request
        :return: The JSON response from the Crowd server, or
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
            if self.use_crowd:
                # We're finally ready to make the request...

                f = self.external_opener.open(request)

                # 204 is officially "No Content", so we won't have
                # any JSON to load! This is expected for 'DELETE'
                # operations for example
                if f.code != 204:
                    response = f.read()

                    response_object = simplejson.loads(response) if response else None

                    f.close()
                else:
                    response_object = None
            else:

                response_object = {
                    'name': 'johhol',
                    'token': 'atoken',
                    'display-name': 'John',
                    'email': 'ceh.ac.uk',
                    'first-name': 'John',
                    'last-name': 'Holt',
                    'user': {'name': 'johhol'}
                }
            return response_object

        except urllib2.HTTPError as h_ex:

            if hasattr(h_ex, "read"):
                response_text = "<None>"
                try:
                    # Interrogate the error response...
                    response_text = h_ex.read()
                    err_response = simplejson.loads(response_text)

                    # Use this info to look up the exception we should raise
                    reason = err_response['reason']
                    raise self._errorMap[reason]()
                except ClientException as ex:
                    raise ex
                except JSONDecodeError:
                    log.exception("Failure to json decode error crowd response '%s'" % response_text)
                    raise ClientException
                except:
                    log.exception("Failure to get error in crowd request")
                    raise ClientException
            else:
                log.error("CROWD ERROR: %s" % h_ex)
                raise h_ex
        except JSONDecodeError as ex:
            log.exception("Failure to json decode crowd response")
            raise ex
        except Exception as ex:
            log.exception("Failure to get crowd response")
            raise ex