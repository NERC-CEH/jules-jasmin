#!/bin/bash
command=`modulecmd bash load /utils/Modules/default/modulefiles/lsfmodules/8.0`

eval "$command"

bjobs -u jules-bd-robot

