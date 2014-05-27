# header

import logging
from pylons.controllers.util import redirect
import formencode
from pylons.decorators import jsonify

from joj.services.user import UserService
from joj.lib.base import BaseController, c, request, response, render, session, abort
from pylons import tmpl_context as c, url
from formencode import htmlfill
import tempfile
from paste.fileapp import FileApp
import os
import urlparse

#from pylons import request, response, session, tmpl_context as c, url
#from pylons.controllers.util import abort, redirect
from services.model_run_service import ModelRunService

log = logging.getLogger(__name__)

class ModelRunController(BaseController):
    """Provides operations for model runs"""

    def __init__(self, user_service=UserService(), model_run_service=ModelRunService()):
        """Constructor
            Params:
                user_service: service to access user details
                model_run_service: service to access model runs
        """
        super(ModelRunController, self).__init__(user_service)
        self._model_run_service = model_run_service

    def create(self):
        """
        Controller for creating a new run
        """

        c.all_models = self._model_run_service.get_model_being_created(self.current_user)

        return render('model_run/create.html')

