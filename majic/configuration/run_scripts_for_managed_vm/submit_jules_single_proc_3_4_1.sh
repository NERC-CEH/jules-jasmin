#!/bin/bash
command=`modulecmd bash load /utils/Modules/default/modulefiles/lsfmodules/8.0`

eval "$command"


sed "s/procs_template/1/g" jules_run_script.sh | bsub
