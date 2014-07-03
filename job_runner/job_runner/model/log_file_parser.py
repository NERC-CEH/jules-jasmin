"""
header
"""
from job_runner.utils import constants


class LogFileParser(object):
    """
    Class to parse a Jules log file
    """

    def __init__(self, lines):
        """
        Initiate
        :param lines: the log file lines to parse
        :return:nothing
        """
        self._lines = lines
        self.status = None
        self.error_message = None

    def parse(self):
        """
        Parse the log file this will set the status and error message
        :return: nothing
        """
        if len(self._lines) == 0:
            self.status = constants.MODEL_RUN_STATUS_FAILED
            self.error_message = constants.ERROR_MESSAGE_OUTPUT_IS_EMPTY
            return

        for line in self._lines:
            if constants.JULES_RUN_COMPLETED_MESSAGE in line:
                self.status = constants.MODEL_RUN_STATUS_COMPLETED
                return

        self.status = constants.MODEL_RUN_STATUS_FAILED
        self.error_message = constants.ERROR_MESSAGE_UNKNOWN_JULES_ERROR