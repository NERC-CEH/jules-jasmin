"""
header
"""
import logging
from dateutil.parser import parse
import re
from job_runner.utils import constants

log = logging.getLogger(__name__)


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
        self.start_time = None
        self.end_time = None
        self.storage_in_mb = 0

    def parse(self):
        """
        Parse the log file this will set the status and error message
        :return: nothing
        """

        found_a_line = False
        errors = []
        post_process_errors = []
        for line in self._lines:
            found_a_line = True
            error_line = line.split(constants.JULES_FATAL_ERROR_PREFIX)
            post_process_error_line = line.split(constants.JULES_POST_PROCESS_ERROR_PREFIX)
            if constants.JULES_RUN_COMPLETED_MESSAGE in line:
                self.status = constants.MODEL_RUN_STATUS_COMPLETED
            elif len(error_line) > 1:
                errors.append(error_line[1].strip())
            elif len(post_process_error_line) > 1:
                post_process_errors.append(post_process_error_line[1].strip())
            elif line.startswith(constants.JULES_START_TIME_PREFIX):
                time = line[len(constants.JULES_START_TIME_PREFIX):].strip()
                try:
                    self.start_time = parse(time)
                except (ValueError, TypeError):
                    log.exception('Start time can not be converted from jules run script. Line is "%s"' % line)
            elif line.startswith(constants.JULES_END_TIME_PREFIX):
                time = line[len(constants.JULES_END_TIME_PREFIX):].strip()
                try:
                    self.end_time = parse(time)
                except (ValueError, TypeError):
                    log.exception('End time can not be converted from jules run script. Line is "%s"' % line)
            elif line.startswith(constants.JULES_STORAGE_PREFIX):
                storage = re.match("\s*(\d+).*", line[len(constants.JULES_STORAGE_PREFIX):])
                if storage is not None:
                    self.storage_in_mb = int(storage.group(1))
                else:
                    log.exception('Storage can not be converted from jules run script. Line is "%s"' % line)

        if not found_a_line:
            self.status = constants.MODEL_RUN_STATUS_FAILED
            self.error_message = constants.ERROR_MESSAGE_OUTPUT_IS_EMPTY
            return

        if len(post_process_errors) != 0:
            self.status = constants.MODEL_RUN_STATUS_FAILED
            self.error_message = "Post processing error:" + ", ".join(post_process_errors)
        elif self.status != constants.MODEL_RUN_STATUS_COMPLETED:
            self.status = constants.MODEL_RUN_STATUS_FAILED
            if len(errors) == 0:
                self.error_message = constants.ERROR_MESSAGE_UNKNOWN_JULES_ERROR
            else:
                self.error_message = "Jules error:" + ", ".join(errors)
