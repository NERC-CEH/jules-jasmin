"""
# header
"""
import urllib
import logging
from decorator import decorator
from pylons import config
from joj.lib.base import render, c
from joj.lib.wmc_util import create_request_and_open_url

log = logging.getLogger(__name__)


@decorator
def must_be_admin(func, self, *args, **kwargs):
    """
    Decorator to add to an action in a controller which means that if
    the user is not an admin the not found page is rendered
    :param func: function that is decorated
    :param args: arguments for the function
    :param kwargs: dictionary for the functions
    :return: rendered html
    """
    access_is_ok = False
    try:
        access_is_ok = self.current_user is not None and self.current_user.is_admin()
    except Exception:
        log.exception("Exception when accessing a admin only page")

    # call to render page must be outside exception block otherwise redirects do not work
    if access_is_ok:
        return func(self, *args, **kwargs)

    return render('not_found.html')


def put_errors_in_table_on_line(errors, error_key, field_name):
    """
    Make a set of errors which are in one category onto one input
    :param errors: the errors list
    :param error_key: main key for the error, e.g. region which would be a list of region error dictionaries
    :param field_name: name of the field to add the errors too
    """

    region_errors = errors.get(error_key)
    if region_errors is not None:
        for region_error, index in zip(region_errors, range(len(region_errors))):
            if len(region_error) is not 0:
                errors["{}-{}.{}".format(error_key, index, field_name)] = "Please correct"
        del errors[error_key]


def remove_deleted_keys(values, count_key, var_prefix, fieldnames):
    """
    Remove from values any indexes from deleted keys. I.e. if there are 3 entries but index 1 isn't present. reset to
     2 entries and rename values from 2 to 1.
     :param values: dictionary of values
     :param count_key: the ket in that dictionary of the count of variables
     :param var_prefix: the prefix for the variables
     :param fieldnames: the fields associated with the prefix
    """

    try:
        current_count = int(values[count_key])
    except (KeyError, ValueError):
        current_count = 0

    new_index = 0
    for i in range(current_count):
                name = "{}-{}.{}"
                if name.format(var_prefix, i, fieldnames[0]) in values:
                    if new_index != i:
                        for field in fieldnames:
                            value_name = name.format(var_prefix, i, field)
                            value_new_name = name.format(var_prefix, new_index, field)
                            value = values[value_name]
                            del values[value_name]
                            values[value_new_name] = value
                    new_index += 1
    values[count_key] = new_index


@decorator
def show_error_if_thredds_down(func, self, *args, **kwargs):
    """
    Renders an error page if the THREDDS server cannot be contacted
    :param func: Function that is decorated
    :param args: Arguments for the function
    :param kwargs: Named key word arguments
    :return: Rendered HTML
    """
    if is_thredds_up(config):
        return func(self, *args, **kwargs)
    else:
        c.admin_email = config["email.admin_address"]
        page = render("map_down.html")
        return page


def is_thredds_up(config):
    """
    Is the THREDDS Server running?
    :param config: Pylons configuration
    :return:
    """
    try:
        create_request_and_open_url(
            config['thredds.server_url'],
            timeout=int(config['thredds.server_timeout'])).read()
        return True
    except:
        return False
