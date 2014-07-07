import logging

from joj.lib.base import BaseController, c, request, response, render, session, abort
from joj.services.user import UserService

#from pylons import request, response, session, tmpl_context as c, url
#from pylons.controllers.util import abort, redirect

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)


class HomeController(BaseController):
    """
    Provides operations for home page actions
    """

    """
    NOTE: Access to the home controller is currently NOT restricted by the Repoze challenge decider.
    Any new actions added to this controller WILL be accessible without authentication and MUST check for
    a logged in user if needed.
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