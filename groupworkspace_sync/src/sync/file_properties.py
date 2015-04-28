"""
#    Majic
#    Copyright (C) 2015  CEH
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


class FileProperties(object):
    """
    Important properties of a file needing to be synchronised
    """

    def __init__(self, file_path, owner, is_published, is_public):
        """
        constructor
        :param file_path: path to the file relative to the root
        :param owner: userid of the user who owns the file
        :param is_published: True if the file is published, false otherwise (i.e. readable by majic users)
        :param is_public: True if the file is public, false otherwise (i.e. readable by everyone)
        """
        self.file_path = file_path
        self.owner = owner
        self.is_published = is_published
        self.is_public = is_public

    def __repr__(self):
        return "{} (model_owner:{}, published?:{}, public?:{})"\
            .format(self.file_path, self.owner, self.is_published, self.is_public)

    def __cmp__(self, other):
        """
        Compare two File properties
        Order is filepath, model_owner, is_publoshed, is_publis
        :param other: other File Property to compare
        :return: negative integer if self < other, zero if self == other, a positive integer if self > other
        """
        if self.file_path != other.file_path:
            if self.file_path < other.file_path:
                return -1
            else:
                return 1

        if self.owner != other.owner:
            if self.owner < other.owner:
                return -1
            else:
                return 1

        result = self.is_published.__cmp__(other.is_published)
        if result == 0:
            result = self.is_public.__cmp__(other.is_public)
        return result