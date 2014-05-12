import logging
from pylons.controllers.util import redirect

from ecomaps.lib.base import BaseController, c, request, response, render, session, abort
from ecomaps.services.user import UserService
from ecomaps.services.dataset import DatasetService
from pylons import tmpl_context as c, url
from formencode import htmlfill
import formencode
from ecomaps.model.create_new_user_form import CreateUserForm, UpdateUserForm

__author__ = 'Chirag Mistry'

log = logging.getLogger(__name__)

class UserController(BaseController):
    """Provides operations for user page actions"""

    _user_service = None
    _dataset_service = None

    def __init__(self, user_service=UserService(), dataset_service=DatasetService()):
        """Constructor for the user controller, takes in any services required
            Params:
                user_service: User service to use within the controller
        """
        super(UserController, self).__init__(user_service)

        self._dataset_service = dataset_service

    def index(self):
        """Allow admin-user to see all users of the system. If user is non-admin, redirect to page not found.
        """
        identity = request.environ.get('REMOTE_USER')

        user = self._user_service.get_user_by_username(identity)

        if user.access_level == "Admin":

            c.all_users = self._user_service.get_all_users()

            return render('list_of_users.html')

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
                                       auto_error_formatter=custom_formatter)
            else:



                # By default a user will be an external user
                self._user_service.create(c.form_result.get('user_name'),
                                          c.form_result.get('first_name'),
                                          c.form_result.get('last_name'),
                                          user_email,
                                          "Admin" if c.form_result.get('is_admin') else "CEH")
                return redirect(url(controller="user"))

    def edit(self, id):
        """ Action for updating a single user, denoted by the ID passed in

            @param id: ID of the user to update
        """

        # Kick unauthorized users out straight away
        if not self.current_user.access_level == 'Admin':
            return render('not_found.html')

        c.user_to_edit = self._user_service.get_user_by_id(id)

        if not c.user_to_edit:
            return render('not_found.html')

        # GET request...
        if not request.method == 'POST':

            return render("edit_user.html")

        else:
            schema = UpdateUserForm()
            c.form_errors = {}
            # POST
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
                html = render('edit_user.html')
                return htmlfill.render(html,
                                       defaults=c.form_result,
                                       errors=c.form_errors,
                                       auto_error_formatter=custom_formatter)
            else:
                # By default a user will be an external user
                self._user_service.update(c.form_result.get('first_name'),
                                          c.form_result.get('last_name'),
                                          user_email,
                                          "Admin" if c.form_result.get('is_admin') else "CEH",
                                          c.form_result.get('user_id'))

                return redirect(url(controller="user"))



def custom_formatter(error):
    """Custom error formatter"""
    return '<span class="help-inline">%s</span>' % (
        htmlfill.html_quote(error)
    )