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
from sys import argv

import os
from postProcessingRes0p5 import convert1Din2D
from postProcessBNG import ProcessingError, PostProcessBNG

PP_ID_LINE_START = 'id ='

PROCESSED_PATH = 'processed'

NCML_FILE = \
"""<?xml version="1.0" encoding="UTF-8"?>

<netcdf xmlns="http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2">
    <aggregation dimName="Time" type="joinExisting" >
        <scan location="." subdirs="false" regExp="^{netcdf_file_name_patern}.*\.nc$"/>
    </aggregation>
</netcdf>
"""

print "-----------------------------------"
print "Post processing File"

file_to_process = str(argv[1])
print
print file_to_process

# check to see which script to use
post_processing_script_id = None
try:
    f = open('post_processing.nml', 'r')
    for line in f:
        if line.strip().startswith(PP_ID_LINE_START):
            post_processing_script = line.strip()[len(PP_ID_LINE_START):]
            if post_processing_script.strip().isdigit():
                post_processing_script_id = int(post_processing_script.strip())
    f.close()
except Exception:
    print "[POST PROCESS ERROR] Exception when getting script id"
    exit()
if post_processing_script_id is None:
    print "[POST PROCESS ERROR] Post processing script id not found"
    exit()

# can not just check that the dir exists because in parallel this introduces a race condition so catch the error instead
import errno
try:
    os.makedirs(PROCESSED_PATH)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise  # raises the error again


try:
    basename = os.path.basename(file_to_process)
    dirname = os.path.dirname(file_to_process)
    if post_processing_script_id == 0:
        print "No conversion"
    elif post_processing_script_id == 1:
        print "Watch conversion"
        convert1Din2D(os.path.dirname(file_to_process), PROCESSED_PATH, basename, verbose=True)
    elif post_processing_script_id == 2:
        print "Chess conversion"
        p = PostProcessBNG()
        p.open(os.path.dirname(file_to_process), PROCESSED_PATH, basename)
        p.convert_jules_1d_to_thredds_2d_for_chess(verbose=True)
        p.close()
    elif post_processing_script_id == 3:
        print "Single cell conversion"
        convert1Din2D(os.path.dirname(file_to_process), PROCESSED_PATH, basename, verbose=True)
    else:
        print "[POST PROCESS ERROR] Post processing script id not recognised"
        exit()
except ProcessingError as ex:
    print("[POST PROCESS ERROR] {}".format(ex.message))
    exit()

# create ncml file if needed
parts = basename.split('.')
netcdf_file_name_pattern = ".".join(parts[:2])
ncml_filename = os.path.join(dirname, netcdf_file_name_pattern + '.ncml')

if not os.path.exists(ncml_filename):
    print "Creating ncml file " + ncml_filename

    f = open(ncml_filename, 'w')
    f.writelines(NCML_FILE.format(netcdf_file_name_patern=netcdf_file_name_pattern))
    f.close()

print "Post processing finished"
