"""
#header
"""
from pylons import url, config
from joj.lib import helpers
from datetime import datetime
import logging

from joj.lib.base import BaseController, c, request, render, redirect
from joj.services.general import ServiceException

log = logging.getLogger(__name__)


class HomeController(BaseController):
    """
    Provides operations for home page actions

    **********************************************************************************************
    NOTE: Access to the home controller is currently NOT restricted by the Repoze challenge decider.
    Any new actions added to this controller WILL be accessible without authentication and MUST check for
    a logged in user if needed.
    **********************************************************************************************
    """

    _user_service = None

    def index(self):
        """Default action, shows the home page"""

        user = self.current_user

        if user:
            c.name = self.current_user.first_name

            return render("home.html")
        else:

            return render("landing.html")

    def about(self):
        """Action for when the user selects the about tab"""
        # We want to present slightly different about pages depending on whether the user
        # is logged in or not. The text is the same however.
        if self.current_user:
            return render("about/about-internal.html")
        else:
            return render("about/about-external.html")

    def faq(self):
        """
        Frequently asked questions page
        :return:
        """
        c.admin_email = config["email.admin_address"]
        return render("about/faq.html")

    def cookies(self):
        """
        Cookies policy
        :return:
        """
        return render("about/cookies.html")

    def privacy(self):
        """
        Privacy policy
        :return:
        """
        return render("about/privacy_policy.html")

    def password(self, id=None):
        """
        Action for when the user selects password
        :param id: users id
        :return: html
        """

        # If the user is logged in then request the users password otherwise use the uuid in he query string
        if self.current_user:
            return render("not_found.html")
        else:
            return self._external_user_password(id)

    def _external_user_password(self, id):
        """
        Code for password resets for an external user
        :param id: user id
        :return:html to render
        """
        c.password_one = ""
        c.password_two = ""

        can_reset_password = self._valid_user_and_uuid(id)
        if can_reset_password == 'OK':
            if request.method == 'POST':
                try:
                    self._user_service.reset_password(
                        c.user.id,
                        request.params.getone('password_one'),
                        request.params.getone('password_two'))
                    helpers.success_flash("Password Reset Successful")
                    redirect(url(controller='account', action='login'))
                except ServiceException as ex:
                    helpers.error_flash("Password not reset because %s" % ex.message)
                    return render("user/forgotten_password_external.html")
            else:
                return render("user/forgotten_password_external.html")
        elif can_reset_password == 'EXPIRED':
            self._user_service.set_forgot_password(c.user.id, send_email=True)
            return render("user/expired_forgotten_password_external.html")
        else:
            return render("user/invalid_forgotten_password_external.html")

    def _valid_user_and_uuid(self, id):
        """
        Check if the user and uuid are valid
        :param id: user id
        :return: OK if both are fail, FAIL if not valid, and EXPIRED if valid but have expired
        """

        try:
            if id is None:
                return 'FAIL'

            c.uuid = request.params.getone('uuid')

            c.user = self._user_service.get_user_by_id(id)
            if c.user is None:
                return 'FAIL'
            if c.user.forgotten_password_uuid != c.uuid:
                return 'FAIL'
            if c.user.forgotten_password_expiry_date < datetime.now():
                return 'EXPIRED'
            return 'OK'

        except KeyError:
            pass

        return 'FAIL'
