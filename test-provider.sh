#!/bin/bash

provider=$1
signed=$2
regpath=$3
showcols=$4
anoncolcheck=$5

if [ -z "$provider" ]; then
    echo "provider (arg 1) must be set"
    exit 1
fi

if [ -z "$signed" ]; then
    echo "signed (arg 2) must be set (true/false))"
    exit 1
else
    SIGNED=$signed
fi

echo "testing provider: $provider"

if [ -z "$regpath" ]; then
    regpath=$(pwd)
fi

echo "registry path: $regpath"

# Create and activate virtual environment

python3 -m venv venv
source venv/bin/activate

# install packages

pip install pandas
pip install psycopg[binary]

# download and unzip stackql binary

if [ ! -f stackql ]
then
    wget -q https://releases.stackql.io/stackql/latest/stackql_linux_amd64.zip
    unzip stackql_linux_amd64.zip
fi

chmod +x stackql

# show version
./stackql --version

# do checks

# set registry path
if [ "$SIGNED" = "true" ]; then
    REG='{"url": "file://'${regpath}'", "localDocRoot": "'${regpath}'", "verifyConfig": {"nopVerify": false}}'
else
    REG='{"url": "file://'${regpath}'", "localDocRoot": "'${regpath}'", "verifyConfig": {"nopVerify": true}}'
fi

# start the server if not running
echo "checking if server is running"
if ! pgrep -f "stackql --registry=" > /dev/null; then
    echo "starting server with registry: $REG"
    nohup ./stackql --registry="${REG}" --pgsrv.port=5444 srv &> stackql.log &
    STACKQL_PID=$!  # Capture the server process ID
    echo "stackql server started with PID: $STACKQL_PID"
    sleep 5
else
    echo "server is already running"
    STACKQL_PID=$(pgrep -f "stackql --registry=")
    echo "existing stackql server PID: $STACKQL_PID"
fi

if [ -z "$showcols" ]; then
    python3 test-provider.py $provider
else
    python3 test-provider.py $provider $showcols
    # TODO implement anoncolcheck for server tests    
fi

# Deactivate virtual environment
# deactivate

echo "stopping server with PID: $STACKQL_PID"
kill -9 $STACKQL_PID
echo "stackql server stopped"