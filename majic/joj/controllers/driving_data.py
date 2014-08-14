"""
# header
"""
import logging
from pylons.controllers.util import redirect
from sqlalchemy.orm.exc import NoResultFound
from pylons import tmpl_context as c, url
from formencode import htmlfill
import formencode

from joj.crowd.client import ClientException
from joj.lib.base import BaseController, request, render
from joj.lib import helpers
from joj.services.user import UserService
from joj.services.dataset import DatasetService
from joj.model.create_new_user_form import CreateUserForm, UpdateUserForm
from joj.utils import constants, utils
from joj.utils.general_controller_helper import must_be_admin
from joj.services.model_run_service import ModelRunService
from joj.services.account_request_service import AccountRequestService
from joj.services.general import ServiceException
from joj.model import DrivingDataset
from joj.services.land_cover_service import LandCoverService
from joj.model.non_database.driving_dataset_jules_params import DrivingDatasetJulesParams

log = logging.getLogger(__name__)


class DrivingDataController(BaseController):
    """Provides operations for driving data page actions"""

    def __init__(self, user_service=UserService(), dataset_service=DatasetService(), landcover_service=LandCoverService()):
        """
        Constructor for the user controller, takes in any services required
        :param user_service: User service to use within the controller
        :param landcover_service: Land cover service to use
        :return: nothing
        """
        super(DrivingDataController, self).__init__(user_service)

        self._dataset_service = dataset_service
        self._landcover_service = landcover_service

    @must_be_admin
    def index(self):
        """
        Allow admins to list the driving data sets
        :return: html to render
        """

        c.driving_data_sets = self._dataset_service.get_driving_datasets()
        return render('driving_data/list.html')

    @must_be_admin
    def edit(self, id=None):
        """
        Allow an admin to edit a driving data se
        :param id: id of the data ste or none for new dataset
        :return: html to render
        """

        values = {}
        errors = {}

        if id is None:
            c.driving_data_set = DrivingDataset()
            c.regions = []
        else:
            c.driving_data_set = self._dataset_service.get_driving_dataset_by_id(id)
            c.regions = self._landcover_service.get_land_cover_regions(id)

        values = c.driving_data_set.__dict__

        c.masks = 0
        for region in c.regions:
            values['id_{}'.format(c.masks)] = region.id
            values['name_{}'.format(c.masks)] = region.name
            values['path_{}'.format(c.masks)] = region.mask_file
            values['category_{}'.format(c.masks)] = region.category.name
            c.masks += 1

        jules_params = DrivingDatasetJulesParams()
        jules_params.create_from(c.driving_data_set)
        jules_params.add_to_dict(values)
        c.nvar = values['drive_nvar']

        html = render('driving_data/edit.html')

        return htmlfill.render(
            html,
            defaults=values,
            errors=errors,
            auto_error_formatter=BaseController.error_formatter)