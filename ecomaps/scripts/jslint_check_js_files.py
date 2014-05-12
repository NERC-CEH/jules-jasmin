'''
Created on 20 Nov 2009

@author: pnorton
'''
import os
import pkg_resources

JS_LINT_COMMAND = './jslint'

def jsLintCheckFiles(files):
    
    jsDir = os.path.join(pkg_resources.resource_filename('ecomaps',''), 'public/js')
    
    for f in files:
        filePath = os.path.join(jsDir,f)
        
        
        cmd = 'jslint %s' % (filePath)
        ret = os.system(cmd)
        
        if ret != 0:
            print "Error(s) found in file %s" % filePath
            break
    

if __name__ == '__main__':
    from ecomaps.lib.js_files_list import getJSFilesForPage
    javascript_files = getJSFilesForPage('wmsviz')
        
    jsLintCheckFiles(javascript_files)