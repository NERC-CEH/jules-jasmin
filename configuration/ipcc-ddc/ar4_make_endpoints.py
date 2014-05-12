import os
import re
import sys

collection_template = """[dataset:%(collection_id)s]
title = %(ds_title)s
datasets = %(ds_children)s
"""

scenario_template = """[dataset:%(collection_id)s_%(scenario_id)s]
title = Scenario %(scenario_id)s
keywordData = scenario=%(scenario_id)s
datasets = %(ds_children)s
"""

type_period_template = """[dataset:%(collection_id)s_%(scenario_id)s_%(type_period_id)s]
keywordData = type_period=%(type_period_id)s
endpoints = %(ep_children)s
"""

endpoint_template = """[endpoint:%(collection_id)s_%(model_id)s_%(scenario_id)s_%(type_period_id)s]
wmsURL = %%(baseurl)s/%(collection_id)s_%(model_id)s_%(scenario_id)s_%(type_period_id)s/wms
keywordData = model=%(model_id)s
"""

collectionNames = {
    'ar4_v2': 'ar4'
    }

collectionTitles = {
    'ar4': 'IPCC-DDC 4th Assessment Report'
    }

typeNames = {
    '': 'climatology',
    'change': 'anomaly'
    }

typeShortNames = {
    '': 'clim',
    'change': 'change'
    }

def main():
    if len(sys.argv) < 2:
        print "Usage: make_endpoints.py file_list_file output_file"
        return

    filePatt = "(?P<collection>[^/]*?)/(?P<variable1>[^/]*?)/(?P<model>[^_]*?)_(?P<scenario>[^_]*?)_1_(?P<variable2>[^-_]*?)[-_]((?P<type>[^_]*?)_)?(?P<period>[^.]*?)\.nc$"
    filePattRe = re.compile(filePatt)

    dsDataDict = {}

    collectionDict = {}

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

            periodType = ("%s_%s" % (vtypeShort, years))
##             print("collection %s scenario %s type %s period %s model %s variable %s" %
##                   (collection, scenario, vtype, period, model, variable))

            collectionName = collectionNames.get(collection, collection)

            scenarios = collectionDict.setdefault(collectionName, {})
            periodTypes = scenarios.setdefault(scenario, {})
            models = periodTypes.setdefault(periodType, {})
            m = models.setdefault(model, {})
        else:
            pass
##             print("### %s ###" % fspec)

    print "###### Writing ######"

##     for kc, vc in sortedItems(collectionDict):
##         print("Collection %s" % (kc))
##         for ks, vs in sortedItems(vc):
##             print("  Scenario %s" % (ks))
##             for kp, vp in sortedItems(vs):
##                 print("    Period_type %s" % (kp))
##                 for km, vm in sortedItems(vp):
##                     print("      Model %s" % (km))

    outFile = open(sys.argv[2], "w")

    outFile.writelines(["################################################################################\n",
                        "# Collections\n",
                        "################################################################################\n"])
    for kc, vc in sortedItems(collectionDict):
        ds_children = ', '.join([("%s_%s" % (kc, ks)) for ks in sortedKeys(vc)])
        outFile.write("\n")
        outFile.write(collection_template %
                      {'collection_id': kc, 'ds_title': collectionTitles.get(kc, kc), 'ds_children': ds_children})

    outFile.writelines(["\n",
                        "################################################################################\n",
                        "# Scenarios\n",
                        "################################################################################\n"])
    for kc, vc in sortedItems(collectionDict):
        for ks, vs in sortedItems(vc):
            ds_children = ', '.join([("%s_%s_%s" % (kc, ks, kp)) for kp in sortedKeys(vs)])
            outFile.write("\n")
            outFile.write(scenario_template %
                          {'collection_id': kc, 'scenario_id': ks, 'ds_children': ds_children})

    outFile.writelines(["\n",
                        "################################################################################\n",
                        "# Models for each scenario/period/type\n",
                        "################################################################################\n"])
    for kc, vc in sortedItems(collectionDict):
        for ks, vs in sortedItems(vc):
            for kp, vp in sortedItems(vs):
                outFile.writelines(["\n",
                                    ("########## %s_%s_%s ##########\n" % (kc, ks, kp))])
                ep_children = ', '.join([("%s_%s_%s_%s" % (kc, km, ks, kp)) for km in sortedKeys(vp)])
                outFile.write("\n")
                outFile.write(type_period_template %
                              {'collection_id': kc, 'scenario_id': ks, 'type_period_id': kp, 'ep_children': ep_children})

                for km in sortedKeys(vp):
                    outFile.write("\n")
                    outFile.write(endpoint_template %
                                  {'collection_id': kc, 'model_id': km, 'scenario_id': ks, 'type_period_id': kp})

def sortedKeys(dict):
    keys = dict.keys()
    keys.sort()
    return keys

def sortedItems(dict):
    keys = dict.keys()
    keys.sort()
    for k in keys:
        yield (k, dict[k])

if __name__ == '__main__':
    main()
