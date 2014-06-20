# header
from pylons.controllers.util import abort


def abort_with_error(error_message):
    """
    Abort with an error message
    :param error_message:
    """
    abort(status_code=500, detail=error_message)