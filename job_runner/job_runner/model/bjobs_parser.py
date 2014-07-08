"""
header
"""
import re
import logging
from job_runner.utils import constants

log = logging.getLogger(__name__)


class BjobsParser(object):
    """
    Parser for bjobs output.
    """

    def __init__(self, lines):
        """
        Initiate the parser
        :param lines: the lines to parse
        :return: noting
        """
        self._lines = lines

    def parse(self):
        """
        Parse the lines
        :return: a dictionary of job ids and status
        """

        index_of_status = self._get_index_of_status()
        if index_of_status is None:
            return {}

        statuses = {}
        for line in self._lines:
            match = re.search('^\s*(\d+)', line)
            if match is not None:
                job_id = int(match.group(1))
                status = self._match_status(line[index_of_status:])
                if status is not None:
                    statuses[job_id] = status
        return statuses

    def _get_index_of_status(self):
        """
        Return the index of the status field in the header
        :return: status field index
        """

        for line in self._lines:
            index = line.find('STAT')
            if index is not -1:
                return index
        return None

    def _match_status(self, status_as_text):
        """
        Match the status text to a known status
        :param status_as_text: line of text starting with status
        :return: the status
        """
        if status_as_text.startswith('RUN'):
            return constants.MODEL_RUN_STATUS_RUNNING
        if status_as_text.startswith('PEND'):
            return constants.MODEL_RUN_STATUS_PENDING

        log.warn("Unknown job status returned from bjobs. Status %s" % status_as_text)
        return constants.MODEL_RUN_STATUS_UNKNOWN
