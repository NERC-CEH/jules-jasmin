#load all required libraries

require(nlme)
require(mgcv)
library(ncdf)
#library(chron)
#library(RColorBrewer)
library(gdata)


#set contrasts to match those used in SAS as CS has always used this approach
options(contrasts = c(factor = "contr.SAS",ordered = "contr.poly"))

#########################################################################################################################################


### read in input data from Simon's Python Script.
#####dat=read.csv("T://PEHN//EcoMAPS//InputRDataFile.csv")
dat=read.csv("N://SMW//Python//EcoMaps//Python//20140131//CSV//InputRDataFile.csv")

summary(dat)


#specify the file server and file to pull the netdcdf file off
linkfiles <- c("http://thredds-prod.nerc-lancaster.ac.uk/thredds/fileServer/LCM2007_1kmDetail/LCM2007_GB_1K_DOM_TAR.nc")

#the following would be specified by the user
#####mult_year="year"; rand_grp="SERIES_NUM.x";model_variable="LOI";data_type="Cont"
mult_year="year"; rand_grp="SERIES_NUM";model_variable="loi";data_type="Cont"


##table must have x, y coordinates names as "X" and "Y" - this is for doing some geostats alongside modelling. Ignored at this stage!

##function with options would start here!


  #create new dataset so that we do not over-write the input one
  newdat=dat[dat$year==2007,]

  ## specify the response tvariable to include in the models
  newdat$response=newdat[,which(names(newdat)==model_variable)]

  ###need to know which variables are factors



  #####mod=gamm(response~as.factor(BROAD_HABITAT)+s(NORTHING),random=list(SERIES_NUM.x=~1),data=newdat)
  mod=gamm(response~as.factor(BROAD_HABITAT)+s(northing),random=list(SERIES_NUM=~1),data=newdat)


  ### output the model summary or similar to see effect of the variables
  print(summary(mod$gam))



##set up empty vectors for storage
n_north = n_east= spat_res = nm_var = c()
tmp.array=north=east=list()


for(i in 1:length(linkfiles)){

    #download the files locally to enable easy reading in
    #####download.file(url=linkfiles[i],destfile="temp.nc", mode="wb")
    download.file(url=linkfiles[i],destfile="N://SMW//Python//EcoMaps//Python//20140131//netCDF//temp.nc", mode="wb")

    #####cov_dat <- open.ncdf("temp.nc")
    cov_dat <- open.ncdf("N://SMW//Python//EcoMaps//Python//20140131//netCDF//temp.nc")

    nm_var[i] <- names(cov_dat$var)[1]

    #save the spatial dimensions
    north[[i]] <- get.var.ncdf(cov_dat,"y")
    n_north[i] <- dim(north)
    east[[i]] <- get.var.ncdf(cov_dat,"x")
    n_east[i] <- dim(east)

    spat_res[i] <- abs(mean(diff(north[[i]])))

    #Next, the data are read using the get.var.ncdf()function, and some “attributes” are read, like the long name of the variable and its missing value.  Then the missing values in the data array are replaced by R/S+ "data not available" values.

    # get the data and attributes
    tmp.array[[i]] <- get.var.ncdf(cov_dat,nm_var)


    ###retrieve meta-data from netcdf files

    #dlname <- att.get.ncdf(lcm1km07,nm_var,"long_name")$value
    #dunits <- att.get.ncdf(lcm1km07,nm_var,"units")$value
    fillvalue <- att.get.ncdf(cov_dat,nm_var,"_FillValue")

    # replace fillvalues with NAs
    #tmp.array[tmp.array==fillvalue$value] <- NA
    #tmp.array[tmp.array==0] <- NA

    # done with the netCDF file, so close it
    close.ncdf(cov_dat)

}


###convert all onto common scale by choosing the finest resolution

std_res <- spat_res[which.min(spat_res)]
scale_res <- spat_res/std_res

for(k in which(scale_res!=1)){

    mat=matrix(1:(length(east[[k]])*length(north[[k]])),ncol=length(north[[k]]),nrow=length(east[[k]]),byrow=TRUE)
    z=c()

    for(j in 1:length(mat[,1])){

           x=rep(mat[j,],rep(scale_res[k],length(mat[j,])))
           y=rep(x,scale_res[k])
           z=c(z,y)


    }

    tmp.array[[k]] = matrix(unmatrix(tmp.array[[k]],byrow=TRUE)[z],byrow=TRUE,ncol=1300,nrow=700)

}



##write model results to the assocaites values

  #### predict model
  pred_points<-expand.grid(north[[1]],east[[1]])

  #####newd=data.frame(BROAD_HABITAT=unmatrix(tmp.array[[1]],byrow=TRUE),NORTHING=pred_points[,1],EASTING=pred_points[,2])
  newd=data.frame(BROAD_HABITAT=unmatrix(tmp.array[[1]],byrow=TRUE),northing=pred_points[,1],easting=pred_points[,2])
 
  ##set any values outside the covariate space to NA
  idx=which(!is.element(newd$BROAD_HABITAT,unique(newdat$BROAD_HABITAT)))
  newd$BROAD_HABITAT[idx]=NA
  newd$BROAD_HABITAT=as.factor(as.character(newd$BROAD_HABITAT))

  ##use the model the predict the coverage data
  modpred=predict(mod$gam,newdata=newd,se.fit=TRUE)
  pred_se_tab=data.frame(preds=modpred$fit,sefit=modpred$se.fit)
  pred_se_tab[idx,]=NA
  names(pred_se_tab)=c("Predicted","Standard_Error")

  out.table=cbind(newd,pred_se_tab)

  out_mat_pred = matrix(out.table$Predicted,byrow=TRUE,ncol=1300,nrow=700)
  out_mat_var = matrix(out.table$Standard_Error,byrow=TRUE,ncol=1300,nrow=700)



#####png(height=720,width=700,file="map_output.png")
png(height=720,width=700,file="N://SMW//Python//EcoMaps//Python//20140131//images//map_output.png")
par(mfrow=c(1,2))
brk=c(seq(0,50,by=10),100)
cols=c("lightgoldenrod1","lightgoldenrod3","burlywood3","darkgoldenrod","lightsalmon4","darkorange4")
par(mai=c(0,0,0,0));image(east[[1]],rev(north[[1]]),(out_mat_pred[,1300:1]),asp=1,col=cols,xaxt="n",breaks=brk,xlab="",yaxt="n",ylab="")

brk=c(seq(1,3,length=10),100)
cols=rev(grey(seq(0.1,0.9,len=10)))
par(mai=c(0,0,0,0));image(east[[1]],rev(north[[1]]),(out_mat_var[,1300:1]),asp=1,col=cols,xaxt="n",breaks=brk,xlab="",yaxt="n",ylab="")
dev.off()

##write out the final matrix produced to a netcdf file

#####download.file(url=linkfiles[1],destfile="temp.nc", mode="wb")
download.file(url=linkfiles[1],destfile="N://SMW//Python//EcoMaps//Python//20140131//netCDF//temp.nc", mode="wb")
#####cov_dat <- open.ncdf("temp.nc")
cov_dat <- open.ncdf("N://SMW//Python//EcoMaps//Python//20140131//netCDF//temp.nc")


x <- dim.def.ncdf( "x", "Metres", east[[1]])
y <- dim.def.ncdf( "y", "Metres",(north[[1]]))

soil_loi <- var.def.ncdf(name="LOI", units="Percent", dim=list(x,y), missval=(-999), longname="Topsoil LOI Estimate from CS data")

#####ncnew <- create.ncdf( "soil_loi.nc", soil_loi)
ncnew <- create.ncdf( "N://SMW//Python//EcoMaps//Python//20140131//netCDF//soil_loi.nc", soil_loi)

put.var.ncdf( ncnew, soil_loi, unmatrix(out_mat_pred))

##Add projection information (for British National Grid) to the output netCDF files
# projection <- var.def.ncdf(name="transverse_mercator", longname="coordinate_reference_system", prec="integer", missval=(-999), units="", dim=(1))
# put.var.ncdf(projection)
# att.put.ncdf(ncnew, projection, "grid_mapping_name", "transverse_mercator")
# att.put.ncdf(ncnew, projection, "semi_major_axis", "6377563.396")
# att.put.ncdf(ncnew, projection, "semi_minor_axis", "6356256.910")
# att.put.ncdf(ncnew, projection, "inverse_flattening", "299.3249646")
# att.put.ncdf(ncnew, projection, "latitude_of_projection_origin", "49.0")
# att.put.ncdf(ncnew, projection, "longitude_of_projection_origin", "-2.0")
# att.put.ncdf(ncnew, projection, "false_easting", "400000.0")
# att.put.ncdf(ncnew, projection, "false_northing", "-100000.0")
# att.put.ncdf(ncnew, projection, "scale_factor_at_projection_origin", "0.9996012717")

att.put.ncdf( ncnew, 0, "title", "A test map of soil carbon loi")
att.put.ncdf( ncnew, 0, "institution", "Centre for Ecology & Hydrology (CEH) Lancaster")
att.put.ncdf( ncnew, 0, "source", "Centre for Ecology & Hydrology (CEH) Lancaster")
att.put.ncdf( ncnew, 0, "reference", "reference")
att.put.ncdf( ncnew, 0, "description", "Predicted map of LOI")
att.put.ncdf( ncnew, 0, "grid_mapping", "transverse_mercator")
att.put.ncdf( ncnew, 0, "history", "history")
att.put.ncdf( ncnew, 0, "summary", "Predicted map of LOI")
att.put.ncdf( ncnew, 0, "keywords", "Mapping, LOI, Broad Habitat, Northing")
att.put.ncdf( ncnew, 0, "date_created", Sys.Date())
att.put.ncdf( ncnew, 0, "date_modified", Sys.Date())
att.put.ncdf( ncnew, 0, "date_issued", Sys.Date())
att.put.ncdf( ncnew, 0, "creator_name", "Peter Henrys")
att.put.ncdf( ncnew, 0, "creator_url", "http://www.ceh.ac.uk/staffwebpages/drpeterhenrys.html")
att.put.ncdf( ncnew, 0, "creator_email", "pehn@ceh.ac.uk")
att.put.ncdf( ncnew, 0, "geospatial_lon_min", att.get.ncdf(cov_dat,0,"geospatial_lon_min")$value,prec="double")
att.put.ncdf( ncnew, 0, "geospatial_lat_min", att.get.ncdf(cov_dat,0,"geospatial_lat_min")$value,prec="double")
att.put.ncdf( ncnew, 0, "geospatial_lon_max", att.get.ncdf(cov_dat,0,"geospatial_lon_max")$value,prec="double")
att.put.ncdf( ncnew, 0, "geospatial_lat_max", att.get.ncdf(cov_dat,0,"geospatial_lat_max")$value,prec="double")
att.put.ncdf( ncnew, 0, "licence",att.get.ncdf(cov_dat,0,"licence")$value)
att.put.ncdf( ncnew, 0, "publisher_name", "Centre for Ecology & Hydrology")
att.put.ncdf( ncnew, 0, "publisher_url", "http://www.ceh.ac.uk")
att.put.ncdf( ncnew, 0, "publisher_email", "enquiries@ceh.ac.uk")
att.put.ncdf( ncnew, 0, "Conventions", att.get.ncdf(cov_dat,0,"Conventions")$value)
att.put.ncdf( ncnew, 0, "comment", "comment")


close.ncdf(ncnew)

#########################
#########################



