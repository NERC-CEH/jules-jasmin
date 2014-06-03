# header

import logging
import urllib2
from pylons.decorators import jsonify
from joj.lib.base import BaseController, render, request, c
from joj.services.user import UserService
from joj.services.model_run_service import ModelRunService
from joj.utils import constants

log = logging.getLogger(__name__)


class MapController(BaseController):
    """
    Controller for the map view page
    """

    _user_service = None
    _model_run_service = None

    def __init__(self, user_service=UserService(), model_run_service=ModelRunService()):
        """
        Constructor
        arguments:
        user_service -- Service to access user data
        model_run_service -- Service to access model runs
        """

        super(MapController, self).__init__()

        self._user_service = user_service
        self._model_run_service = model_run_service

    def index(self):
        """Default action for the map controller"""

        user = self._user_service.get_user_by_username(request.environ['REMOTE_USER'])

        c.model_runs = self._model_run_service.get_models_for_user(user)

        return render('map.html')

    @jsonify
    def test(self):
        """
            Tests the connection to the map server
        """
        try:
            response = urllib2.urlopen(constants.THREDDS_SERVER_URL, timeout=constants.THREDDS_SERVER_TIMEOUT).read()
            return True
        except:
            return False