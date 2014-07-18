#!/bin/bash
module load /utils/Modules/default/modulefiles/lsfmodules/8.0


sed "s/procs_template/1/g" jules_run_script.sh | bsub
