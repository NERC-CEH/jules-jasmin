from bisect import bisect_left
from contextlib import contextmanager
import os
import tempfile
import shutil

__author__ = 'Phil Jenkins (Tessella)'


class WorkingDirectory(object):
    """
        A representation of a temporary working directory
    """

    _working_dir = None

    def __init__(self):
        """Constructor for our temporary directory
        """
        self._working_dir = os.path.join(tempfile.mkdtemp(), "working")

    @property
    def root_folder(self):

        return self._working_dir


@contextmanager
def working_directory(working_dir, root_dir):
    """Provides a temporary copy of a given root directory, deletes when done
        Params:
            working_dir: The WorkingDirectory instance to use
    """

    try:
        temp_dir = working_dir.root_folder

        #working_dir = EcomapsAnalysisWorkingDirectory(os.path.join(temp_dir, 'working'))
        shutil.copytree(root_dir, temp_dir)

        # copytree() doesn't set the permissions properly on the copied files
        # so we'll have to do it manually instead
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for dir in dirs:
                os.chmod(os.path.join(root, dir), 0755)
            for file in files:
                os.chmod(os.path.join(root,file), 0755)

        yield working_dir

    finally:

        # Clean up after ourselves
        shutil.rmtree(temp_dir)

def find_closest(list, value):

    # Sort list
    list = sorted(list)
    pos = bisect_left(list, value)

    if pos==0:
        return list[0]
    if pos == len(list):
        return list[-1]
    before = list[pos - 1]
    after = list[pos]
    if after - value < value - before:
       return after
    else:
       return before