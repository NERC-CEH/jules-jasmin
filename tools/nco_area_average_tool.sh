#!/bin/bash

if [ $# -ne 6 ]
then
        echo "Usage: nco area averaging tool <variable name> <start data filename> <end data filename> <region variable> <region filename> <output directory>"
        echo "        Create a file containing the area average for a region using nco." 
	echo "           <variable name> is the name of the variable to average"
	echo "           <start data filename> and <end data filename> are the first and last data file to process, all files between these files will be summarised too"
        echo "           <region variable> is the name of the mask variable in the file <region filename> to use to perform the averaging"
        echo "           <output directory> is the directory where the files will be written to"
        exit
fi

variable=$1
start_data_path=$2
end_data_path=$3
region_var=$4
region_path=$5
output_dir=$6

# find list of input files

find_common_prefix='N;s/^?*\(.*\).*\n\1.*$/\1/'

postfix=`{ echo $start_data_path; echo $end_data_path;} | rev | sed -e $find_common_prefix | rev`
prefix=`{ echo $start_data_path; echo $end_data_path;} | sed -e $find_common_prefix`

if [ "$prefix" == "$start_data_path" ]
then
  input_files=$prefix
else
  start_year=`echo "$start_data_path" | sed -e "s:^$prefix\(.*\)$postfix$:\1:"`
  end_year=`echo "$end_data_path" | sed -e "s:^$prefix\(.*\)$postfix$:\1:"`
  input_files=""
  for yr in $(seq $start_year $end_year)
  do  
   input_files="$input_files ${prefix}${yr}${postfix}"
  done
fi

#process input files
mkdir -p $output_dir || { echo "Error making directory $output_dir" ; exit 2 ; }
for in_file in $input_files
do
        outfilename=`basename "${in_file}"`
        outf="$output_dir/regional_average_${region_var}_$outfilename"
        tmpf=/tmp/temp.nc

        # Put info from data file and region file into one, so we don't
        # end up editing the source by mistake
        echo ncks
        ncks ${in_file} $tmpf || { echo Error ncks ; exit 2 ; }
        ncks -A $region_path $tmpf  || { echo Error ncks2 ; exit 2 ; }

        echo ncap2 -O -h -s "${variable}_$region_var=$variable*$region_var" $tmpf $tmpf
        ncap2 -O -h -s "${variable}_$region_var=$variable*$region_var" $tmpf $tmpf || { echo Error ncap2 ; exit 2 ; }

        # Average over the whole domain, once for each region
        echo AVERAGING
        echo ncwa -O -h -a y,x $tmpf $tmpf
        ncwa -O -h -a y,x $tmpf $tmpf || { echo Error ncwa ; exit 2 ; }

        echo CREATE OUTPUT
        varlist=time
        varlist="$varlist,${variable}_$region_var"
        ncks -O -h -v $varlist $tmpf $outf || { echo Error ncks ; exit 2 ; }
        rm $tmpf
done

