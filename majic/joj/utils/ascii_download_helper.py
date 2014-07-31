"""
header
"""


class AsciiDownloadHelper(object):
    """
    Class to manage the downloading of ASCII driving data files
    """

    def get_driving_data_file_gen(self, driving_data, lat, lon, start, end):
        """
        Get the correctly formatted contents of the ascii driving data download file
        :param driving_data: Driving data to get data from
        :param lat: Latitude of position to get data at
        :param lon: Longitude of position to get data at
        :param start: Earliest date/time to get data at
        :param end:  Latest date/time to get data at
        :return: Contents of file
        """
        # TODO this
        string = "abcdefghijklmnopqrstuvwxyz"
        for i in string:
            yield i

    def get_driving_data_filename(self, driving_data, lat, lon, start, end):
        """
        Get an appropriate filename for the file being downloaded
        :param driving_data: Driving data to get data from
        :param lat: Latitude of position to get data at
        :param lon: Longitude of position to get data at
        :param start: Earliest date/time to get data at
        :param end:  Latest date/time to get data at
        :return:
        """
        # TODO this
        return "driving.txt"

    def get_driving_data_filesize(self, driving_data, start, end):
        # TODO this
        return 1024