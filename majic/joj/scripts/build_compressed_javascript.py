'''
Created on 20 Nov 2009

@author: pnorton
'''
import pkg_resources
import os
import gzip


COMPRESSED_JS_NAME = 'compressed_client.js'
YUI_COMPRESSOR_PATH = './yuicompressor-2.4.2.jar'

def buildCompressedFile(files):

    outputsDir = os.path.join(pkg_resources.resource_filename('ecomaps',''), 'public/js')
    
    tempOutputFile = os.path.join(outputsDir, COMPRESSED_JS_NAME + '.tmp')
    outputFile = os.path.join(outputsDir, COMPRESSED_JS_NAME)
    outputFH = open(tempOutputFile, 'w')
    
    for f in files:
        fh = open(os.path.join(outputsDir,f))
        data = fh.read() + '\n'
        fh.close()

        outputFH.write(data)

    outputFH.close()
    
    print "wrote outputFile", tempOutputFile

    options = '--type js -v -o %s' % (outputFile,)
    
    cmd = 'java -jar "%s" %s "%s"' % (YUI_COMPRESSOR_PATH, options, tempOutputFile)
    
    print "running ", cmd
    ret = os.system(cmd)
    
    print "returned", ret
    
    if ret == 0:
        os.remove(tempOutputFile)
        
    print "wrote", outputFile
    
    return ret

if __name__ == '__main__':
    
    javascript_files = ['wmsc.js',
                        'utils.js',
                        'endpoint.js',
                        'furtherInfoLink.js',
                        'displayOptionsRetriever.js',
                        'mapControl.js',
                        'layerControl.js',
                        'capabilities.js',
                        'wcs.js',
                        'layerFigureDownload.js',
                        'layerInformation.js',
                        'layerList.js',
                        'layerDisplayOptions.js',
                        'layerDownload.js',
                        'layoutManager.js',
                        'splitAxisConfig.js',
                        'splitAxisSelect.js',
                        'endpointSelection.js',
                        'ajaxRetriever.js',
                        'axisConfigRetriever.js',
                        'layerDimensions.js',
                        'layerParameters.js',
                        'figureBuilder.js',
                        'legendContainer.js',
                        'boundsControl.js',
                        'wmcRetriever.js',
                        'layerDefaultSetter.js',
                        'outlineControl.js']
        
    ret = buildCompressedFile(javascript_files)
    