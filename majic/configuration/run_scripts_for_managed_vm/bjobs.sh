#!/bin/bash
command=`modulecmd bash load /utils/Modules/default/modulefiles/lsfmodules/9.1`

eval "$command"

bjobs -u jules-bd-robot

