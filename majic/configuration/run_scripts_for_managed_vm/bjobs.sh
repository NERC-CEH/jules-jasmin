#!/bin/sh
command=`modulecmd bash load /utils/Modules/default/modulefiles/lsfmodules/8.0`

eval "$command"

bjobs
