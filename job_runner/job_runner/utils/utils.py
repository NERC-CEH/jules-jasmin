"""
header
"""


def insert_before_file_extension(path, string):
    """
    Add a string to a path immediately before the file extension
    :param path: File path to modify
    :param string: String to add
    :return:
    """
    file_extens_idx = path.rfind('.')
    return "".join((path[0:file_extens_idx], string, path[file_extens_idx:]))