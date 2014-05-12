import logging
import urllib2
from pylons.decorators import jsonify
from ecomaps.lib.base import BaseController, render, request, c
from ecomaps.services.dataset import DatasetService
from ecomaps.services.user import UserService

__author__ = 'Phil Jenkins (Tessella)'

log = logging.getLogger(__name__)

class MapController(BaseController):

    _user_service = None
    _dataset_service = None

    def __init__(self, user_service=UserService(), dataset_service=DatasetService()):

        super(MapController, self).__init__()

        self._dataset_service = dataset_service
        self._user_service = user_service


    def index(self):
        """Default action for the map controller"""

        user = self._user_service.get_user_by_username(request.environ['REMOTE_USER'])

        c.dataset_types = self._dataset_service.get_datasets_for_user(user.id)


        return render('map.html')

    @jsonify
    def test(self):
        """
            Tests the connection to the map server
        """
        try:
            response = urllib2.urlopen("http://thredds-prod.nerc-lancaster.ac.uk/thredds/", timeout=10).read()

            return True
        except:
            return False