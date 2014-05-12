#load R libraries that are needed
require(nlme)
require(mgcv)
require(ncdf)
require(ncdf4)
require(gdata)

# PJ ********* Inputs from Python *************
#
#   coverage_setup:
#       Named list of columns, keyed by the URL of each dataset
#   time_slices
#       Named list keyed by column names, with a time index (if the column contains 3D data)
#       e.g. ['LandCover'=3, 'precip'=1]
#   progress_rep_file
#       Location on disk of the progress reporting file
#   user_name
#       Name of the user running the analysis
#   email_address
#       Email address of the user running the analysis
#   csv_file
#       Location of the input CSV file
#   map_image_file
#       Location on disk to write the map image to
#   fit_image_file
#       Location on disk to write the fit image to
#   temp_netcdf_file
#       Location of the temporary netCDF container to use as a temporary store
#   output_netcdf_file
#       Location to write the output netCDF file to
#
########################################################


# Writes a message to the predefined progress file, creates the file
# if it doesn't exist
progress_fn <- function(message) {

    if(!file.exists(progress_rep_file)) {
        file.create(progress_rep_file)
    }

    file_obj <- file(progress_rep_file)
    print(message)
    writeLines(message, file_obj)
    close(file_obj)
}

do_work <- function() {

    progress_fn("Initiating R session and loading libraries")

    #set contrasts to match those used in SAS as CS has always used this approach
    options(contrasts = c(factor = "contr.SAS",ordered = "contr.poly"))

    #specify the file server and file to pull the netdcdf file off  and the variables needed from each
    #covariate_data = list()
    #covariate_data[[1]]=list()
    #covariate_data[[1]]$linkfile="http://thredds-prod.nerc-lancaster.ac.uk/thredds/fileServer/LCM2007_1kmDetail/LCM2007_GB_1K_DOM_TAR.nc"
    #covariate_data[[1]]$vars=c("LandCover")
    #covariate_data[[1]]$tm_slice=NA
    #covariate_data[[2]]=list()
    #covariate_data[[2]]$linkfile="http://thredds-prod.nerc-lancaster.ac.uk/thredds/fileServer/CHESSModel001Run001OutputDetail/CHESS_MODEL001_RUN001_OUT_1971-01.nc"
    #covariate_data[[2]]$vars=c("ta","precip")
    #covariate_data[[2]]$tm_slice=c(1,31)

    covariate_data = list()

    # PJ: Constructing the named list dynamically based on what
    # has been passed in from the Python
    for(i in 1:length(names(coverage_setup))) {

        covariate_data[[i]] = list()
        url = names(coverage_setup)[i]
        covariate_data[[i]]$linkfile = url
        covariate_data[[i]]$vars = c(coverage_setup[[url]])
    }

    #read in concatonated point data (simon's python script does this)
    dat=read.csv(csv_file)

    #user defined inputs. mult year defines if temporal correlation needed. rand_grp defines if random effects needed.
    mult_year <- "year" ; rand_grp <- "SERIES_NUM" ; data_type <- "Cont" ; model_variable="loi"

    ## define the family of distributions to choose from
    poss_fam <- c("gaussian","Gamma","quasibinomial","quasipoisson")

    #create new dataset so that we do not over-write the input one
    newdat=dat

    ## specify the response variable to include in the models
    newdat$response <- newdat[,which(names(newdat)==model_variable)]
    if(!is.null(rand_grp)){newdat$rnd_group <- newdat[,which(names(newdat)==rand_grp)]}
    if(!is.null(mult_year)){newdat$tm_var <- newdat[,which(names(newdat)==mult_year)]}

    progress_fn("Checking distribution of Response Variable")

    #test normality of response if it is continuos.
    if(data_type=="Cont"){
        norm.test.res <- shapiro.test(newdat$response)

        if(norm.test.res$p.value<0.05){
            data_type="ContNonG"
        }
     }

    #select the distribution family to use given the type of data being modelled
    data_fam <- switch(data_type,"Cont"=poss_fam[1],"ContNonG"=poss_fam[2],"Count"=poss_fam[4],"Binary"=poss_fam[3])

    progress_fn("Loading data into R")

    ##set up empty vectors for storage
    n_north = n_east= spat_res = nm_var = dunits = c()
    tmp.array = north = east = list()

    cn <- 1
    for(i in 1:length(covariate_data)){

        #download the files locally to enable easy reading in
        download.file(url=covariate_data[[i]]$linkfile,destfile=temp_netcdf_file, mode="wb")

        cov_dat <- nc_open(temp_netcdf_file)

        for(vn in 1:length(covariate_data[[i]]$vars)){

            nm_var[cn] <- toString(covariate_data[[i]]$vars[vn])

            #save the spatial dimensions
            #north[[cn]] <- get.var.ncdf(cov_dat,"y")
            north[[cn]] <- ncvar_get(cov_dat, "y")
            n_north[cn] <- dim(north)
            #east[[cn]] <- get.var.ncdf(cov_dat,"x")
            east[[cn]] <- ncvar_get(cov_dat, "x")
            n_east[cn] <- dim(east)

            spat_res[cn] <- abs(mean(diff(north[[cn]])))

            #Next, the data are read using the get.var.ncdf()function, and some �attributes� are read, like the long name of the variable and its missing value.  Then the missing values in the data array are replaced by R/S+ "data not available" values.

            # get the data and attributes

            tmp.array[[cn]] <- ncvar_get(cov_dat,toString(nm_var[cn]))

            # PJ: Check the time slices array to see if there's
            # an entry with this column name, extract the slice at
            # the designated index if so
            if(length(time_slices) > 0 && !is.na(time_slices[[nm_var[cn]]])){

                tmp.array[[cn]] <- tmp.array[[cn]][,,(time_slices[[nm_var[cn]]])]
            }

            ###retrieve meta-data from netcdf files

            #dlname <- att.get.ncdf(lcm1km07,nm_var,"long_name")$value
            #dunits[cn] <- att.get.ncdf(cov_dat,nm_var[cn],"units")$hasatt
            dunits[cn] <- ncatt_get(cov_dat, nm_var[cn], "units")$hasatt

            #fillvalue <- att.get.ncdf(cov_dat,nm_var[cn],"_FillValue")
            fillvalue <- ncatt_get(cov_dat, nm_var[cn], "_FillValue")

            #
            if(!is.na(fillvalue$value)){
              var_id_nd <- which(names(newdat)==nm_var[cn])
              newdat[(newdat[,var_id_nd]==fillvalue$value & !is.na((newdat[,var_id_nd]))),var_id_nd]=NA
            }
            # replace fillvalues with NAs
            tmp.array[[cn]][tmp.array[[cn]]==fillvalue$value] <- NA

            cn <- cn +1
        }

        # done with the netCDF file, so close it
        #close.ncdf(cov_dat)
        nc_close(cov_dat)
    }

    progress_fn("Constructing Model formula")

    ###need to know which variables are factors

      factor_vars <- nm_var[dunits==0]
      smooth_vars <- nm_var[dunits!=0]

      factor_form <- paste(paste("as.factor(",factor_vars,")",sep=""),collapse="+")
      smooth_form <- paste(paste("s(",smooth_vars,",k=6)",sep=""),collapse="+")
      #if(is.null(mult_year)){int=1}else{int=mult_year}

      if(length(factor_vars)>0){
         form <- paste("response~1",factor_form,"te(easting,northing)",sep="+")
         if(length(smooth_vars)>0){
            form <- paste(form,smooth_form,sep="+")
         }
      }else{
         if(length(smooth_vars)>0){
             form <- paste("response~1",smooth_form,"te(easting,northing)",sep="+")
         }else{
            form <- paste("response~1","te(easting,northing)",sep="+")
         }
      }


    progress_fn("Running Model")

      x=newdat[newdat$rnd_group==newdat$rnd_group[1] & newdat$tm_var==newdat$tm_var[1],]
      y=newdat[newdat$rnd_group==newdat$rnd_group[1],]

      v=which(apply(x,2,function(X){length(unique(X))})==dim(x)[1])
      w=which(apply(y,2,function(X){length(unique(X))})<(dim(y)[1]-3))
      len_id = apply(newdat[,which(is.element(names(newdat),intersect(names(v),names(w))))],2,function(X){length(unique(X))})
      tmp_nm = names(len_id)[which.max(len_id)]
      newdat$temp_rand = newdat[,which(names(newdat)==tmp_nm)]
      mod_t = "mix_gam"
      if(!is.null(rand_grp) & is.null(mult_year)){
        progress_fn("Applying GAMM, grouped data")
        mod=try(gamm(as.formula(form),random=list(rnd_group=~1),data=newdat,family=data_fam,niterPQL=5))
      }else{
        progress_fn("Applying GAMM, multi-year")
        if(is.null(rand_grp) & !is.null(mult_year)){
          mod=try(gamm(as.formula(form),correlation=corAR1(form=~tm_var|temp_rand),data=newdat,family=data_fam,niterPQL=5))
        }else{
          if(!is.null(rand_grp) & !is.null(mult_year)){
            progress_fn("Applying GAMM, multi-year and grouped")
            mod=try(gamm(as.formula(form),random=list(temp_rand=~1),correlation=corAR1(form=~tm_var|temp_rand),data=newdat,family=data_fam,niterPQL=5))
            if(class(mod)=="try-error" | (summary(mod$gam)$r.sq)<0){
              mod=try(gamm(as.formula(form),random=list(rnd_group=~1),data=newdat,family=data_fam,niterPQL=5))
            }
          }
        }
      }
      if(class(mod)=="try-error" | (summary(mod$gam)$r.sq)<0){
        mod=list() ; mod$gam=try(gam(as.formula(form),data=newdat,family=data_fam))
        mod_t="norm_gam"
        if(class(mod$gam)=="try-error"){class(mod)="try-error"}
     }

    if(class(mod)!="try-error"){

        ###convert all onto common scale by choosing the finest resolution available.
        resuse <- which.min(spat_res)
        std_res <- spat_res[resuse]
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

         ##write model results to the assocaited values

          progress_fn("Predicting model over full spatial grid")

          #### predict model
          pred_points <- expand.grid(north[[resuse]],east[[resuse]])
          newd=data.frame(easting=pred_points[,2],northing=pred_points[,1])

          for(cov_i in 1:length(tmp.array)){
            newd <- cbind(newd,unmatrix(tmp.array[[cov_i]],byrow=TRUE))
          }

          names(newd)[-c(1:2)]=nm_var

          ##set any values outside the covariate space to NA. Particularly important for factors

          for(fv in factor_vars){
            c1=which(names(newd)==fv) ; c2=which(names(newdat)==fv)
            idx=which(!is.element(newd[,c1],unique(newdat[,c2])))
            newd[idx,c1]=NA
            newd[,c1]=as.factor(as.character(newd[,c1]))
          }


          ##use the model the predict the coverage data. ensure model predict the standard error as well - this may be replaced by bootstrap in future
          modpred=predict(mod$gam,newdata=newd,se.fit=TRUE,type="response")

          pred_se_tab=data.frame(preds=modpred$fit,sefit=modpred$se.fit)

          if(exists("idx")) {
            pred_se_tab[idx,]=NA
          }

          names(pred_se_tab)=c("Predicted","Standard_Error")

          out.table=cbind(newd,pred_se_tab)

          out_mat_pred = matrix(out.table$Predicted,byrow=TRUE,ncol=1300,nrow=700)
          out_mat_var = matrix(out.table$Standard_Error,byrow=TRUE,ncol=1300,nrow=700)


        #####png(height=720,width=700,file="map_output.png")
        #####png(height=720,width=700,file="N://SMW//Python//EcoMaps//Python//20140213//images//map_output.png")

        progress_fn("Writing map image")
        png(height=720,width=700,file=map_image_file)
          par(mfrow=c(1,2))
          brk=c(seq(0,50,by=10),100)
          cols=c("lightgoldenrod1","lightgoldenrod3","burlywood3","darkgoldenrod","lightsalmon4","darkorange4")
          par(mai=c(0,0,0.4,0));image(east[[resuse]],rev(north[[resuse]]),(out_mat_pred[,1300:1]),asp=1,main="",col=cols,xaxt="n",breaks=brk,xlab="",yaxt="n",ylab="")
           lb=c()
           labs=as.character((brk)[-length(brk)])
           for(i in 1:length(labs)){
                 lb[i]=paste(as.character(labs[i])," - ",brk[i+1])
           }
           legend("topright",legend=as.character(lb),col=cols,pch=15,pt.cex=2.4,bty="n",title=model_variable,cex=0.75)


          brk=c(seq(1,3,length=10),100)
          cols=rev(grey(seq(0.1,0.9,len=10)))
          par(mai=c(0,0,0.4,0));image(east[[resuse]],rev(north[[resuse]]),(out_mat_var[,1300:1]),asp=1,main="",col=cols,xaxt="n",breaks=brk,xlab="",yaxt="n",ylab="")
          lb=c()
          labs=as.character(round(brk,2)[-length(brk)])
          for(i in 1:length(labs)){
                lb[i]=paste(as.character(labs[i])," - ",round(brk[i+1],2))
          }
          legend("topright",legend=as.character(lb),col=cols,pch=15,pt.cex=2.4,bty="n",title=paste("Variance of ",model_variable,sep=""),cex=0.75)


        dev.off()

        progress_fn("Writing fit image")
        png(height=320,width=700,file=fit_image_file)
          par(mfrow=c(1,2))
          plot(mod$gam$y,mod$gam$fitted.values,xlab="Observed Values",ylab="Fitted Values")
          abline(a=0,b=1,col="red",lwd=2)
          hist(mod$gam$y-mod$gam$fitted.values,main="",xlab="Model Residuals")

        dev.off()
        if(mod_t=="norm_gam"){aic_val <- AIC(mod$gam)}else{aic_val <- AIC(mod$lme)}
        rmse <- sqrt(mean((mod$gam$y-mod$gam$fitted.values)^2))
        r2 <- (summary(mod$gam))$r.sq
        mod_formula <- paste(model_variable," ~ Intercept + ",paste(nm_var,collapse=" + "),sep="")
        mod_sum <- summary(mod$gam)


    }else{

        rmse <- "NA Error"
        r2 <- "NA Error"
        mod_formula <- "NA Error"
        aic_val <- "NA Error"

        png(height=720,width=700,file=map_image_file)
          par(mfrow=c(1,2))
          par(mai=c(0,0,0.4,0))
          plot(c(0,1),c(0,1),type="n",main="Model Error",xaxt="n",yaxt="n",xlab="",ylab="")
          text(expand.grid(seq(0,1,len=5),seq(0,1,len=10)),"error",cex=0.7,col="grey")
          par(mai=c(0,0,0.4,0))
          plot(c(0,1),c(0,1),type="n",main="Model Error",xaxt="n",yaxt="n",xlab="",ylab="")
          text(expand.grid(seq(0,1,len=5),seq(0,1,len=10)),"error",cex=0.7,col="grey")
        dev.off()

        png(height=320,width=700,file=fit_image_file)
          par(mfrow=c(1,2))
          plot(0,type="n",xlab="",ylab="",main="Model Error")
          plot(0,type="n",xlab="",ylab="",main="Model Error")

        dev.off()

        out_mat_pred = matrix(NA,byrow=TRUE,ncol=1300,nrow=700)
        out_mat_var = matrix(NA,byrow=TRUE,ncol=1300,nrow=700)


    }

    ##  Write out the predicted LOI and variance to a single netCDF file.
    ##  Predicted LOI and variance will be written out as netCDF variables, with variance specified as an acillary variable
    ##  (as per the CF 1.6 Convention; see:  http://cf-pcmdi.llnl.gov/documents/cf-conventions/1.6/cf-conventions.html#ancillary-data).

    progress_fn("Writing output to file")


    v=unlist(covariate_data)
    fl=v[which(names(v)[1:which(v==nm_var[resuse])]=="linkfile")]

    download.file(url=fl,destfile=temp_netcdf_file, mode="wb")

    #####cov_dat <- open.ncdf("N://SMW//Python//EcoMaps//Python//20140213//netCDF//temp.nc")
    cov_dat <- nc_open(temp_netcdf_file)

    y <- ncdim_def("y", "m", north[[resuse]], unlim=FALSE, create_dimvar=TRUE, longname="northing - OSGB36 grid reference")
    x <- ncdim_def("x", "m", east[[resuse]],  unlim=FALSE, create_dimvar=TRUE, longname="easting - OSGB36 grid reference")

    pred <- ncvar_def(name=model_variable, units="PercentLOI", dim=list(x, y), missval=(-999), longname="Topsoil LOI Estimate from CS data")
    mod_var <- ncvar_def(name="VAR", units="PercentLOI", dim=list(x, y), missval=(-999), longname="Topsoil LOI Estimate Variance from CS data")
    prj <- ncvar_def(name="transverse_mercator", units="", dim=list(), longname="coordinate_reference_system", prec="integer")

    #####ncnew <- nc_create("N://SMW//Python//EcoMaps//Python//20140213//netCDF//soil_loi.nc", list(soil_loi, soil_var, prj))
    ncnew <- nc_create(output_netcdf_file, list(pred, mod_var, prj))

    #ncnew <- nc_create("C://tester.nc", list(pred, mod_var, prj))

    ncvar_put(ncnew, pred, unmatrix(out_mat_pred))
    ncvar_put(ncnew, mod_var, unmatrix(out_mat_var))

    ncatt_put(ncnew, "y", "standard_name", "projection_y_coordinate")
    ncatt_put(ncnew, "y", "point_spacing", "even")
    ncatt_put(ncnew, "x", "standard_name", "projection_x_coordinate")
    ncatt_put(ncnew, "x", "point_spacing", "even")

    ncatt_put(ncnew, model_variable, "coordinates", "x y")
    ncatt_put(ncnew, model_variable, "grid_mapping", "transverse_mercator")
    ncatt_put(ncnew, model_variable, "valid_min", min(unmatrix(out_mat_pred), na.rm = TRUE), prec="float")
    ncatt_put(ncnew, model_variable, "valid_max", max(unmatrix(out_mat_pred), na.rm = TRUE), prec="float")
    ncatt_put(ncnew, model_variable, "missing_value", -999, prec="float")
    ncatt_put(ncnew, model_variable, "ancillary_variables", "VAR")

    ncatt_put(ncnew, "VAR", "coordinates", "x y")
    ncatt_put(ncnew, "VAR", "grid_mapping", "transverse_mercator")
    ncatt_put(ncnew, "VAR", "valid_min", min(unmatrix(out_mat_var), na.rm = TRUE), prec="float")
    ncatt_put(ncnew, "VAR", "valid_max", max(unmatrix(out_mat_var), na.rm = TRUE), prec="float")
    ncatt_put(ncnew, "VAR", "missing_value", -999, prec="float")

    ncatt_put(ncnew,"transverse_mercator", "grid_mapping_name" ,"transverse_mercator")
    ncatt_put(ncnew,"transverse_mercator", "semi_major_axis", 6377563.396,prec="double")
    ncatt_put(ncnew,"transverse_mercator", "semi_minor_axis" ,6356256.910,prec="double")
    ncatt_put(ncnew,"transverse_mercator", "inverse_flattening" ,299.3249646,prec="double")
    ncatt_put(ncnew,"transverse_mercator", "latitude_of_projection_origin" ,49.0,prec="double")
    ncatt_put(ncnew,"transverse_mercator", "longitude_of_projection_origin" ,-2.0,prec="double")
    ncatt_put(ncnew,"transverse_mercator", "false_easting" ,400000.0,prec="double")
    ncatt_put(ncnew,"transverse_mercator", "false_northing" ,-100000.0,prec="double")
    ncatt_put(ncnew,"transverse_mercator", "scale_factor_at_projection_origin",0.9996012717,prec="double")

    ncatt_put(ncnew, 0, "title", paste("A map of ",model_variable,sep=""))
    ncatt_put(ncnew, 0, "institution", "Centre for Ecology & Hydrology (CEH) Lancaster")
    ncatt_put(ncnew, 0, "source", "Centre for Ecology & Hydrology (CEH) Lancaster")
    ncatt_put(ncnew, 0, "reference", "EcoMAPS v1.01")
    ncatt_put(ncnew, 0, "description", paste("Predicted map of ",model_variable," using EcoMAPS v1.01",sep=""))
    ncatt_put(ncnew, 0, "grid_mapping", "transverse_mercator")
    ncatt_put(ncnew, 0, "history", "history")
    ncatt_put(ncnew, 0, "summary", paste("Predicted map of ",model_variable,sep=""))
    ncatt_put(ncnew, 0, "keywords", "Mapping, LOI, Broad Habitat, Northing")
    ncatt_put(ncnew, 0, "date_created", as.character(Sys.Date()), prec="text")
    ncatt_put(ncnew, 0, "date_modified", as.character(Sys.Date()), prec="text")
    ncatt_put(ncnew, 0, "date_issued", as.character(Sys.Date()), prec="text")

    ncatt_put(ncnew, 0, "creator_name", user_name)
    ncatt_put(ncnew, 0, "creator_url", "http://www.ceh.ac.uk//")
    ncatt_put(ncnew, 0, "creator_email", email_address)

    ncatt_put(ncnew, 0, "geospatial_lon_min", ncatt_get(cov_dat, 0, "geospatial_lon_min")$value, prec="double")
    ncatt_put(ncnew, 0, "geospatial_lat_min", ncatt_get(cov_dat, 0, "geospatial_lat_min")$value, prec="double")
    ncatt_put(ncnew, 0, "geospatial_lon_max", ncatt_get(cov_dat, 0, "geospatial_lon_max")$value, prec="double")
    ncatt_put(ncnew, 0, "geospatial_lat_max", ncatt_get(cov_dat, 0, "geospatial_lat_max")$value, prec="double")
    ncatt_put(ncnew, 0, "licence", ncatt_get(cov_dat,0,"licence")$value)
    ncatt_put(ncnew, 0, "publisher_name", "Centre for Ecology & Hydrology")
    ncatt_put(ncnew, 0, "publisher_url", "http://www.ceh.ac.uk")
    ncatt_put(ncnew, 0, "publisher_email", "enquiries@ceh.ac.uk")
    ncatt_put(ncnew, 0, "Conventions", ncatt_get(cov_dat, 0, "Conventions")$value)
    ncatt_put(ncnew, 0, "comment", "comment")
    ncatt_put(ncnew, 0, "model_formula", mod_formula)
    ncatt_put(ncnew, 0, "root_mean_square_error", rmse)
    ncatt_put(ncnew, 0, "r_squared", r2)
    ncatt_put(ncnew, 0, "AIC", aic_val)
    ncatt_put(ncnew, 0, "Model_Terms", paste(c(row.names(mod_sum$pTerms.table),row.names(mod_sum$s.table)),collapse=","))
    ncatt_put(ncnew, 0, "Model_pVals", paste(round(c((mod_sum$pTerms.table[,3]),(mod_sum$s.table[,4])),4),collapse=","))
    nc_close(ncnew)
}
#########################
#########################

#do_work()
tryCatch(do_work(), error=function(e) { progress_fn(geterrmessage()); return(NA)})
