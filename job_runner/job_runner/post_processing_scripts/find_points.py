import netCDF4 as nc
import numpy as np
import sys

def create_points_file(infile, maskfile, outfile):

    inf=nc.Dataset(infile,'r')

    mf=nc.Dataset(maskfile,'r')

    nxin=len(inf.dimensions['x'])
    nyin=len(inf.dimensions['y'])

    latin=inf.variables['latitude'][:].flatten()
    lonin=inf.variables['longitude'][:].flatten()

    latm=mf.variables['lat'][:]
    lonm=mf.variables['lon'][:]

    thresh=5e-5

    outf=open(outfile,'w')

    for i in range(nxin*nyin):
        indx=np.where(np.logical_and(np.abs(latm-latin[i])<thresh,np.abs(lonm-lonin[i])<thresh))
        if len(indx[0])==0:
            print "Error: point %d (%s %s) not found"%(i,latin[i],lonin[i])
            sys.exit(2)
        elif len(indx[0])>1:
            print "Error: point %d (%s %s) been found %d times"%(i,latin[i],lonin[i],len(indx[0]))
            sys.exit(3)
        else:
            outf.write('%d %d\n'%indx)


    outf.close()

