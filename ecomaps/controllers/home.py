import logging

from ecomaps.lib.base import BaseController, c, request, response, render, session, abort
from ecomaps.services.user import UserService

#from pylons import request, response, session, tmpl_context as c, url
#from pylons.controllers.util import abort, redirect

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class HomeController(BaseController):
    """Provides operations for home page actions"""

    _user_service = None

    def index(self):
        """Default action, shows the home page"""

        c.name = self.current_user.first_name

        return render("home.html")

    def about(self):
        """Action for when the user selects the about tab"""

        return render("about.html")