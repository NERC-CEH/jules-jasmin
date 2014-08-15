#!/bin/bash

ps -u$LOGNAME | sed 's/TTY/STAT/g' | sed 's/^\(\s*[0-9][0-9]*\).*/\1 RUN/g'

