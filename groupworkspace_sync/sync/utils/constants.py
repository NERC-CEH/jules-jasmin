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
# chunk size in bytes to download a file in
DOWNLOAD_CHUNK_SIZE_IN_BYTES = 1000000

#  directory name of output folder parts
MODEL_RUN_DIR_PREFIX = "run"

# Majic web service section name
CONFIG_WS_SECTION = "Majic Webservice"
CONFIG_URL = "url"
CONFIG_MAJIC_WS_TIMEOUT = "timeout"

CONFIG_MAJIC_WS_CERT_PATH = 'majic_web_service_certificate_path'
CONFIG_MAJIC_WS_USER_CERT_PATH = 'majic_web_service_user_certificate_path'
CONFIG_MAJIC_WS_USER_KEY_PATH = 'majic_web_service_user_key_path'

CONFIG_DATA_SECTION = "Data"
CONFIG_DATA_PATH = "data_path"  # path to which the data to synchronised within the root
CONFIG_EXTENSIONS_TO_COPY = "extensions_to_copy"  # space separated extensions that can be copied
CONFIG_CONTENT_TO_IGNORE_REGEX = "content_to_ignore_regex"  # space separated regex of content which should be ignored
CONFIG_EXTRA_DIRS_TO_SYNC = "extra_directories_to_sync"  # space separated list of extra directories to sync

CONFIG_APACHE_SECTION = "Apache"
CONFIG_APACHE_ROOT_PATH = "root_path"  # web address of the data runs are stored in apache
CONFIG_APACHE_PASSWORD = "password"
CONFIG_APACHE_USERNAME = "username"
CONFIG_APACHE_TIMEOUT = "timeout"

CONFIG_FILES_SECTION = "Files"
CONFIG_ROOT_PATH = "root_path"  # root path where all files are synchronised to
CONFIG_NOBODY_USERNAME = "nobody_username"  # user who owns data for users not in the workbench
CONFIG_DELETE_SCRIPT_PATH = "delete_dir_script"  # path to delete script
CONFIG_UPDATE_PERMISSIONS_SCRIPT_PATH = "update_permissions_script"  # path to update permissions script

# Constants for the names of the dictionary values in the json
JSON_MODEL_RUNS = 'model_runs'
JSON_MODEL_RUN_ID = 'model_run_id'

JSON_USER_NAME = 'user_name'
JSON_IS_PUBLISHED = 'is_published'
JSON_IS_PUBLIC = 'is_public'
JSON_LAST_STATUS_CHANGE = 'last_status_changed'
