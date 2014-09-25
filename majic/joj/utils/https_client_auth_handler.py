"""
#    Majic
#    Copyright (C) 2014  CEH
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
import urllib2
import httplib


# noinspection PyClassicStyleClass
class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    """
    Class to act as authentication in a urllib2 situation which needs certificate authentication
    see http://stackoverflow.com/questions/1875052/using-paired-certificates-with-urllib2
    """
    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self._key = key
        self._cert = cert

    def https_open(self, req):
        """
         Rather than pass in a reference to a connection class, we pass in
         a reference to a function which, for all intents and purposes,
         will behave as a constructor
        :param req: request
        :return: function to open a url
        """
        return self.do_open(self.get_connection, req)

    def get_connection(self, host, timeout=300):
        """
        return a new connection
        :param host: host name with port
        :param timeout: timeout
        :return: a connection
        """
        return httplib.HTTPSConnection(host, key_file=self._key, cert_file=self._cert, timeout=timeout)
