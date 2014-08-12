"""
header
"""
from sys import argv

import os
from postProcessingRes0p5 import convert1Din2D

PROCESSED_PATH = 'processed'

NCML_FILE = \
"""<?xml version="1.0" encoding="UTF-8"?>

<netcdf xmlns="http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2">
    <aggregation dimName="Time" type="joinExisting" >
        <scan location="." subdirs="false" regExp="^{netcdf_file_name_patern}.*\.nc$"/>
    </aggregation>
</netcdf>
"""


if not os.path.exists(PROCESSED_PATH):
    os.mkdir(PROCESSED_PATH)

print "-----------------------------------"
print "Converting File from 1D to 2D"

file = str(argv[1])
print
print file

basename = os.path.basename(file)
convert1Din2D(os.path.dirname(file), PROCESSED_PATH, basename, verbose=True)

#create ncml file if needed
parts = basename.split('.')
netcdf_file_name_patern = ".".join(parts[:2])
ncml_filename = netcdf_file_name_patern + '.ncml'

if not os.path.exists(ncml_filename):
    print "Creating ncml file " + ncml_filename

    f = open(ncml_filename, 'w')
    f.writelines(NCML_FILE.format(netcdf_file_name_patern=netcdf_file_name_patern))
    f.close()
