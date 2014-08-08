"""
header
"""
from sys import argv

import os
from postProcessingRes0p5 import convert1Din2D

PROCESSED_PATH = 'processed'

if not os.path.exists(PROCESSED_PATH):
    os.mkdir(PROCESSED_PATH)

print "-----------------------------------"
print "Converting File from 1D to 2D"

file = str(argv[1])
print
print file

convert1Din2D(os.path.dirname(file), PROCESSED_PATH, os.path.basename(file), verbose=True)
