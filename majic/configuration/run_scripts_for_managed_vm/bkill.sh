#!/bin/bash
command=`modulecmd bash load /utils/Modules/default/modulefiles/lsfmodules/8.0`

eval "$command"

if [ -z "$1" ]
then
  echo "must include job number: bkill <job number>"
else
 bkill -u jules-bd-robot $1
fi

