import os
import re
import sys
import tempfile

from csml import csmlscan

cfg_template = """
[dataset]
dsID: %(ds_id)s
dsName: %(ds_name)s

[features]
type: GridSeries
number: many

[files]
selection: %(file_list)s
mapping: onetoseveral
output: %(xml_file)s
printscreen: 0

[spatialaxes]
spatialstorage: fileextract

[values]
valuestorage: fileextract
[time]
timedimension: time
timestorage: inline

[security]
allow: http://aa.ceda.rl.ac.uk/ badc
"""

collectionNames = {
    'ar4_v2': 'ar4'
    }

varNames = {
    'huss': 'Specific Humidity', # specific_humidity
    'pr': 'Precipitation', # precipitation_flux
    'psl': 'Pressure', # air_pressure_at_sea_level
    'rsds': 'Shortwave Flux', # surface_downwelling_shortwave_flux_in_air
    'tas': 'Temperature', # air_temperature
    'tasmax': 'Daily Maximum Temperature', # air_temperature_daily_max
    'tasmin': 'Daily Minimum Temperature', # air_temperature_daily_min
    'uas': 'Wind Eastward', # eastward_wind
    'vas': 'Wind Northward' # northward_wind
    }

typeNames = {
    '': 'climatology',
    'change': 'anomaly'
    }

## typeShortNames = {
##     '': 'clim',
##     'change': 'anom'
##     }
typeShortNames = {
    '': 'clim',
    'change': 'change'
    }

def main():
    if len(sys.argv) < 3:
        print "Usage: scan.py file_list_file data_root_directory csml_directory"
        return

    dataRoot = sys.argv[2]
    csmlDir = sys.argv[3]

    filePatt = "(?P<collection>[^/]*?)/(?P<variable1>[^/]*?)/(?P<model>[^_]*?)_(?P<scenario>[^_]*?)_1_(?P<variable2>[^-_]*?)[-_]((?P<type>[^_]*?)_)?(?P<period>[^.]*?)\.nc$"
    filePattRe = re.compile(filePatt)

    dsDataDict = {}

    filelist = open(sys.argv[1])
    for line in filelist:
        fspec = line.rstrip()
        m = filePattRe.match(fspec)
        if m:
            collection = m.group('collection')
            scenario = m.group('scenario')
            vtype = m.group('type')
            period = m.group('period')
            model = m.group('model')
            variable = m.group('variable2')

            period = period.lstrip('o')
            (start, end) = period.split('-')
            years = (int(end) - int(start) + 1).__str__()

            if vtype is None:
                vtypeName = typeNames.get('', '')
                vtypeShort = typeShortNames.get('', '')
            else:
                vtypeName = typeNames.get(vtype, vtype)
                vtypeShort = typeShortNames.get(vtype, vtype)

##             print("collection %s scenario %s type %s period %s model %s variable %s" %
##                   (collection, scenario, vtype, period, model, variable))

            collectionName = collectionNames.get(collection, collection)
            dsId = ("%s_%s_%s_%s_%s" % (collectionName, model, scenario, vtypeShort, years))
            print dsId

            dsData = dsDataDict.setdefault(dsId,
                                           {'ds_id': dsId,
                                            'collection': collection,
                                            'model': model,
                                            'scenario': scenario,
                                            'vtype': vtypeName,
                                            'years': years,
                                            'file_list': []
                                            })
            dsFileList = dsData['file_list']
            dsFileList.append(os.path.join(dataRoot, fspec))
        else:
            print("### %s ###" % fspec)

    print "###### Scanning ######"

    for dsId, dsData in dsDataDict.iteritems():
        print ">>>>>>    >>>>>>    >>>>>>    >>>>>>    >>>>>>    >>>>>>    >>>>>>    >>>>>>"
        print dsId
        dsData['xml_file'] = os.path.join(csmlDir, dsId + '.xml')
        dsData['file_list'] = " ".join(dsData['file_list'])
        dsType = ("%s year mean %s" % (dsData['years'], dsData['vtype']))
        dsData['ds_name'] = ("Scenario: %s - Model: %s - %s" %
                             (dsData['scenario'], dsData['model'], dsType))
        print dsData['ds_name']
        tmp = tempfile.NamedTemporaryFile(prefix=(dsId + '_'), suffix='.cfg', delete=False,
                                          dir='/home/rwilkinson_local/dev/scantmp')
        tmp.write(cfg_template % dsData)
        tmp.flush()
        tmp.close()
        print tmp.name
        csmlscan.main(['csmlscan', '-c', tmp.name])
        print "<<<<<<    <<<<<<    <<<<<<    <<<<<<    <<<<<<    <<<<<<    <<<<<<    <<<<<<"

if __name__ == '__main__':
    main()
