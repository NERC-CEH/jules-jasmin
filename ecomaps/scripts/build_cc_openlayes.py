'''
Created on 10 Dec 2009

@author: pnorton
'''

import pkg_resources
import os
import sys
import pprint


CONFIG_FILE_NAME = 'cc_openlayers_config'

# the single file script uses this name to find its <script> tag and then uses
# that to generate the image + theme import path, changing this name will 
# result in this code breaking and the image + theme imports being incorrect.
OUTPUT_FILE_NAME = 'OpenLayers.js'





if __name__ == '__main__':

    openlayersDir = os.path.join(pkg_resources.resource_filename('ecomaps',''), 'public/js/openlayers')
    buildDir = os.path.join(openlayersDir, 'build')
    buildFile = os.path.join(buildDir, 'build.py')
    
    #add the openlayers tools directory to the path
    #sys.path.append(os.path.join(openlayersDir, "tools"))
    
    os.chdir(buildDir)
    
    pprint.pprint(sys.path)
    import mergejs
    outputsDir = os.path.join(pkg_resources.resource_filename('cowecomaps'), 'public/js/cc_openlayers')
    outputFile = os.path.join(outputsDir, OUTPUT_FILE_NAME)
    
    
    scriptsDir = os.path.join(pkg_resources.resource_filename('cowsclient',''), 'scripts')
    configFile = os.path.join(scriptsDir, CONFIG_FILE_NAME)
    
    cmd = 'python "%s" %s "%s"' % (buildFile, configFile, outputFile)
    print "running ", cmd
    ret = os.system(cmd)
    
    print "returned", ret   
    