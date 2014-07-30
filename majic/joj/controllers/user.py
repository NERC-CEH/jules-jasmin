"""
# header
"""
import logging
from pylons.controllers.util import redirect
from sqlalchemy.orm.exc import NoResultFound

from joj.lib.base import BaseController, request, render
from joj.lib import helpers
from joj.services.user import UserService
from joj.services.dataset import DatasetService
from pylons import tmpl_context as c, url
from formencode import htmlfill
import formencode
from joj.model.create_new_user_form import CreateUserForm, UpdateUserForm
from joj.utils import constants, utils
from joj.services.model_run_service import ModelRunService
from joj.services.account_request_service import AccountRequestService

__author__ = 'Chirag Mistry'

log = logging.getLogger(__name__)


class UserController(BaseController):
    """Provides operations for user page actions"""

    _user_service = None
    _dataset_service = None

    def __init__(self,
                 user_service=UserService(),
                 dataset_service=DatasetService(),
                 account_request_service=AccountRequestService()):
        """
        Constructor for the user controller, takes in any services required
        :param user_service: User service to use within the controller
        :param dataset_service: dataset service
        :param account_request_service: accoun requests service
        :return: nothing
        """
        super(UserController, self).__init__(user_service)

        self._dataset_service = dataset_service
        self._model_run_service = ModelRunService()
        self._account_request_service = account_request_service

    def index(self):
        """Allow admin-user to see all users of the system. If user is non-admin, redirect to page not found.
        """

        if self.current_user is not None and self.current_user.is_admin():
            c.all_users = self._user_service.get_all_users()
            user_map = {}
            for user in c.all_users:
                user_map[user.id] = user
                user.storage_in_mb = 0
                user.published_storage_in_mb = 0

            c.storage_total_used_in_gb = 0
            for user_id, status, storage_mb in self._model_run_service.get_storage_used():
                c.storage_total_used_in_gb += int(storage_mb)
                if status == constants.MODEL_RUN_STATUS_PUBLISHED:
                    user_map[user_id].published_storage_in_mb += int(storage_mb)
                else:
                    user_map[user_id].storage_in_mb += int(storage_mb)
            c.storage_total_used_in_gb = utils.convert_mb_to_gb_and_round(c.storage_total_used_in_gb)

            c.core_user = None
            for user in c.all_users:
                if user.username == constants.CORE_USERNAME:
                    c.core_user = user

                user.quota_status = ''
                percentage = round(utils.convert_mb_to_gb_and_round(user.storage_in_mb)
                                   / user.storage_quota_in_gb * 100.0, 1)
                if percentage >= constants.QUOTA_ABSOLUTE_LIMIT_PERCENT:
                    user.quota_status = 'error'
                elif percentage >= constants.QUOTA_WARNING_LIMIT_PERCENT:
                    user.quota_status = 'warning'

            c.core_user.quota_status = 'info'

            c.total_storage_percent_used = c.storage_total_used_in_gb / c.core_user.storage_quota_in_gb * 100.0
            c.bar_class = helpers.get_progress_bar_class_name(c.total_storage_percent_used)

            return render('user/list_of_users.html')

        else:

            return render('not_found.html')

    def create(self):
        """Create a new user
        """

        if not self.current_user.access_level == 'Admin':
            return render('not_found.html')

        if not request.POST:
            return render('new_user.html')

        schema = CreateUserForm()
        c.form_errors = {}

        if request.POST:

            try:
                c.form_result = schema.to_python(request.params)

            except formencode.Invalid, error:

                c.form_result = error.value
                c.form_errors = error.error_dict or {}

            user_email = str(c.form_result.get('email'))

            # Username of the user will be set as the user's email address
            # Generate an error if the email address (and hence username) is already taken
            if self._user_service.get_user_by_email_address(user_email):
                c.form_errors = dict(c.form_errors.items() + {
                    'email': 'Email address is already taken - please choose another.'
                }.items())

            if c.form_errors:
                html = render('new_user.html')
                return htmlfill.render(html,
                                       defaults=c.form_result,
                                       errors=c.form_errors,
                                       prefix_error=False,
                                       auto_error_formatter=BaseController.error_formatter)
            else:

                # By default a user will be an external user
                self._user_service.create(c.form_result.get('user_name'),
                                          c.form_result.get('first_name'),
                                          c.form_result.get('last_name'),
                                          user_email,
                                          constants.USER_ACCESS_LEVEL_ADMIN if c.form_result.get('is_admin')
                                          else constants.USER_ACCESS_LEVEL_CEH)
                return redirect(url(controller="user"))

    def edit(self, id):
        """ Action for updating a single user, denoted by the ID passed in

            @param id: ID of the user to update
        """

        # Kick unauthorized users out straight away
        if not self.current_user.is_admin():
            return render('not_found.html')

        c.user_to_edit = self._user_service.get_user_by_id(id)

        if not c.user_to_edit:
            return render('not_found.html')

        # GET request...
        if not request.method == 'POST':

            return render("user/edit_user.html")

        else:
            # POST
            schema = UpdateUserForm()
            c.form_errors = {}

            try:
                c.form_result = schema.to_python(request.params)

            except formencode.Invalid, error:

                c.form_result = error.value
                c.form_errors = error.error_dict or {}

            user_email = str(c.form_result.get('email'))
            user_id = int(c.form_result.get('user_id'))

            # Username of the user will be set as the user's email address
            # Generate an error if the email address (and hence username) is already taken
            existing_user = self._user_service.get_user_by_email_address(user_email)

            if existing_user and existing_user.id != user_id:
                c.form_errors = dict(c.form_errors.items() + {
                    'email': 'Email address is already taken - please choose another.'
                }.items())

            if c.form_errors:
                html = render('user/edit_user.html')
                return htmlfill.render(html,
                                       defaults=c.form_result,
                                       errors=c.form_errors,
                                       prefix_error=False,
                                       auto_error_formatter=BaseController.error_formatter)
            else:
                # By default a user will be an external user
                self._user_service.update(c.form_result.get('first_name'),
                                          c.form_result.get('last_name'),
                                          user_email,
                                          "Admin" if c.form_result.get('is_admin') else "CEH",
                                          c.form_result.get('user_id'),
                                          c.form_result.get('storage_quota'))

                return redirect(url(controller="user"))

    def requests(self, id):
        """
        List the account requests for approval
        :param id: id to accept or reject or None on get
        :return: nothing
        """

        if self.current_user is None or not self.current_user.is_admin():
            return render('not_found.html')

        if not request.method == 'POST':
            c.account_requests = self._account_request_service.get_account_requests()

            return render('user/requests.html')

        else:
            if id is None:
                helpers.error_flash("Request not accepted or rejected. No id included with reject or accept")
            try:
                action = request.params.getone('action')
                if action == u'accept':
                    pass
                elif action == u'reject':
                    reason_for_rejection = request.params.getone('reason')
                    if len(reason_for_rejection.strip()) == 0:
                        helpers.error_flash(
                            "Request not rejected: A reason must be given to the user for why they are being rejected")
                    else:
                        self._account_request_service.reject_account_request(id, reason_for_rejection)
                        helpers.success_flash("User account request has been rejected and an email has been sent.")
                else:
                    raise KeyError()
            except KeyError:
                helpers.error_flash("Request not accepted or rejected. No action included with reject or accept")
            except NoResultFound:
                helpers.error_flash("Request could not be found, no action taken")

            return redirect(url(controller="user", action="requests"))
