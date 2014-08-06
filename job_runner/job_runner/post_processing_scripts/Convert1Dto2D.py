"""
header
"""

import os
from os.path import isfile, join
from postProcessingRes0p5 import convert1Din2D

print "Converting Files from 1D to 2D"


OUTPUT_PATH = 'output'
PROCESSED_PATH = 'processed'

if not os.path.exists(OUTPUT_PATH):
    print "[FATAL ERROR] No output directory"

if not os.path.exists(PROCESSED_PATH):
    os.mkdir(PROCESSED_PATH)

onlyfiles = [f for f in os.listdir(OUTPUT_PATH) if isfile(join(OUTPUT_PATH, f)) and f.endswith('.nc') and 'dump' not in f]

for file in onlyfiles:
    # If you don't want text on your screen, turn "verbose" off
    # by setting verbose=False

    print "-------------------------------------------------------"
    print file
    print
    convert1Din2D(OUTPUT_PATH, PROCESSED_PATH, file, verbose=True)

