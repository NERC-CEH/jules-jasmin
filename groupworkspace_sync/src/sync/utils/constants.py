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


# Majic web service section name
CONFIG_WS_SECTION = "Majic Webservice"
CONFIG_URL = "url"

CONFIG_MAJIC_WS_CERT_PATH = 'majic_web_service_certificate_path'
CONFIG_MAJIC_WS_USER_CERT_PATH = 'majic_web_service_user_certificate_path'
CONFIG_MAJIC_WS_USER_KEY_PATH = 'majic_web_service_user_key_path'

CONFIG_DATA_SECTION = "Data"
CONFIG_DATA_PATH = "data_path"  # path to which the data to synchronised
CONFIG_DATA_NOBODY_USERNAME = "nobody_username"  # user who owns data for users not in the workbench

# Constants for the names of the dictionary values in the json
JSON_MODEL_RUNS = 'model_runs'
JSON_MODEL_RUN_ID = 'model_run_id'

JSON_USER_NAME = 'user_name'
JSON_IS_PUBLISHED = 'is_published'
JSON_IS_PUBLIC = 'is_public'
JSON_LAST_STATUS_CHANGE = 'last_status_changed'
