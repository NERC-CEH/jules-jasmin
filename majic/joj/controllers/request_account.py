"""
#    Majic
#    Copyright (C) 2014  CEH
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
from pylons.decorators import validate
from pylons import request
from pylons import tmpl_context as c

from joj.lib.base import BaseController, render
from joj.services.account_request_service import AccountRequestService
from joj.model import AccountRequest
from joj.model.request_account_form import RequestAccountForm


class RequestAccountController(BaseController):
    """
    Controller for the 'request account' page
    """

    _account_request_service = None

    def __init__(self, account_request_service=AccountRequestService()):
        """
        Construct a new RequestAccountController
        :param account_request_service: Access to AccountRequest database
        :return:
        """
        self._account_request_service = account_request_service
        super(RequestAccountController, self).__init__()

    def license(self):
        """
        Show the Majic license
        :return: rendered license page
        """

        return render('request_account/license.html')

    @validate(schema=RequestAccountForm(), form='request', post_only=False, on_get=False, prefix_error=False,
              auto_error_formatter=BaseController.error_formatter)
    def request(self):
        """
        Process a request for a new account
        :return: rendered form or success page
        """
        if not request.POST:
            return render('request_account/request.html')

        account_request = AccountRequest()
        account_request.first_name = self.form_result['first_name']
        account_request.last_name = self.form_result['last_name']
        account_request.email = self.form_result['email']
        account_request.institution = self.form_result['institution']
        account_request.usage = self.form_result['usage']
        self._account_request_service.add_account_request_with_email(account_request)

        c.account_request = account_request
        return render('request_account/request_made.html')
