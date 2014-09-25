#!/usr/bin/env python

import netCDF4 as nc
import numpy as np
#import matplotlib.pyplot as plt
import sys
import string


def combine(intmplt, pttmplt, outfile, nyout, nxout):

    segs = [""]
    mapvars = [
        "latitude",
        "longitude",
        "wind",
        "tl1",
        "qw1",
        "lw_down sw_down",
        "precip pstar",
        "surf_roff",
        "sub_surf_roff",
        "fqw_gb",
        "rad_net",
        "ftl_gb gpp_gb",
        "resp_p_gb",
        "tstar_gb",
        "snow_mass_gb",
        "t_soil",
        "smc_tot",
        "smcl",
        "swet_liq_tot"]

    pts=[]
    for seg in segs:
        print "Segment %03d"%seg
        ptfile=pttmplt.substitute(seg="%03d"%seg)
        ptf=open(ptfile)
        ys=[]
        xs=[]
        for lin in ptf.readlines():
            y,x=lin.strip().split()
            ys.append(int(y))
            xs.append(int(x))

        infile=intmplt.substitute(seg="%03d"%seg)
        inf=nc.Dataset(infile,'r')
        #dimlensin={}
        #for dim in inf.dimensions:
            #dimlensin[dim]=len(inf.dimensions[dim])

        if seg==segs[0]:
            outf=nc.Dataset(outfile,'w')
            #dimlensout={}
            for dim in inf.dimensions:
                if dim=='y':
                    dimlen=nyout
                elif dim=='x':
                    dimlen=nxout
                else:
                    dimlen=len(inf.dimensions[dim])
                outf.createDimension(dim,dimlen)

            outdata={}
            for var in inf.variables:
                if '_FillValue' in inf.variables[var].ncattrs():
                    outf.createVariable(var,inf.variables[var].dtype,dimensions=inf.variables[var].dimensions,fill_value=inf.variables[var]._FillValue)
                elif 'fill_value' in inf.variables[var].ncattrs():
                    outf.createVariable(var,inf.variables[var].dtype,dimensions=inf.variables[var].dimensions,fill_value=inf.variables[var].fill_value)
                elif 'missing_value' in inf.variables[var].ncattrs():
                    outf.createVariable(var,inf.variables[var].dtype,dimensions=inf.variables[var].dimensions,fill_value=inf.variables[var].missing_value)
                else:
                    outf.createVariable(var,inf.variables[var].dtype,dimensions=inf.variables[var].dimensions)

                for attr in inf.variables[var].ncattrs():
                    if attr not in ('_FillValue','fill_value','missing_value'):
                        outf.variables[var].setncattr(attr,inf.variables[var].getncattr(attr))
                if var in mapvars:
                    if '_FillValue' in outf.variables[var].ncattrs():
                        mv=outf.variables[var]._FillValue
                    else:
                        mv=-99999.0

                    outdata[var]=np.ma.masked_equal(np.ones(outf.variables[var].shape)*mv,mv)
                else:
                    outf.variables[var][:]=inf.variables[var][:]


        for var in mapvars:
            if len(outf.variables[var].shape)==2:
                outdata[var][ys,xs]=inf.variables[var][:].flatten()
            elif len(outf.variables[var].shape)==3:
                for t in range(outdata[var].shape[0]):
                    outdata[var][t,ys,xs]=inf.variables[var][t,:,:].flatten()
            elif len(outf.variables[var].shape)==4:
                for t in range(outdata[var].shape[0]):
                    for z in range(outdata[var].shape[1]):
                        outdata[var][t,z,ys,xs]=inf.variables[var][t,z,:,:].flatten()
            else:
                print "Error: too many dimensions"
                sys.exit(2)


        inf.close()

    for var in mapvars:
        outf.variables[var][:]=outdata[var][:]

    outf.close()

    print "Done, please look at %s for some lovely mapped data"%outfile
