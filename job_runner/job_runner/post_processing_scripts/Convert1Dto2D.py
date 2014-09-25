"""
header
"""
from sys import argv

import os
from postProcessingRes0p5 import convert1Din2D

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


basename = os.path.basename(file_to_process)
dirname = os.path.dirname(file_to_process)
if post_processing_script_id == 0:
    print "No conversion"
elif post_processing_script_id == 1:
    print "Watch conversion"
    convert1Din2D(os.path.dirname(file_to_process), PROCESSED_PATH, basename, verbose=True)
elif post_processing_script_id == 2:
    print "Chess conversion"
    convert1Din2D(os.path.dirname(file_to_process), PROCESSED_PATH, basename, verbose=True)
elif post_processing_script_id == 3:
    print "Single cell conversion"
    convert1Din2D(os.path.dirname(file_to_process), PROCESSED_PATH, basename, verbose=True)
else:
    print "[POST PROCESS ERROR] Post processing script id not recognised"
    exit()

#create ncml file if needed
parts = basename.split('.')
netcdf_file_name_pattern = ".".join(parts[:2])
ncml_filename = os.path.join(dirname, netcdf_file_name_pattern + '.ncml')

if not os.path.exists(ncml_filename):
    print "Creating ncml file " + ncml_filename

    f = open(ncml_filename, 'w')
    f.writelines(NCML_FILE.format(netcdf_file_name_patern=netcdf_file_name_pattern))
    f.close()

print "Post processing finished"
