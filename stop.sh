#!/bin/bash

if ! pgrep -f "stackql --registry=" > /dev/null; then
    echo "stackql server is not running"
else
    STACKQL_PID=$(pgrep -f "stackql --registry=")
    echo "stopping stackql server"
    kill -9 $STACKQL_PID
fi