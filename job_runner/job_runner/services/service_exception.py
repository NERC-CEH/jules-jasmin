"""
header
"""

class ServiceException(Exception):
    """
    Exception class for when the service has a problem
    """
    def __init__(self, message):
        super(ServiceException, self).__init__()
        self.message = message