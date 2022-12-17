method=$1
provider=$2
regpath=$3
anoncolcheck=$4

if [ "$method" = "server" ]; then 
    echo "running tests in server mode"
elif [ "$method" = "exec" ]; then
    echo "running tests in exec mode"
else
    echo "method (arg 1) must be either 'server' or 'exec'"
    exit 1
fi

if [ -z "$provider" ]; then
    echo "provider (arg 2) must be set"
    exit 1
fi

echo "testing provider: $provider"

if [ -z "$regpath" ]; then
    regpath=$(pwd)
fi

echo "registry path: $regpath"

if [ "$method" = "exec" ]; then
    if [ ! -d "pystackql" ]; then
        git clone https://github.com/stackql/pystackql.git
    fi
fi

# install packages

pip install -r requirements.txt

# download and unzip stackql binary

if [ ! -f stackql ]
then
    wget https://releases.stackql.io/stackql/latest/stackql_linux_amd64.zip
    unzip stackql_linux_amd64.zip
fi

 chmod +x stackql

# do checks

if [ "$method" = "exec" ]; then
    if [ -z "$anoncolcheck" ]; then
        python3 test-provider-exec.py $provider $regpath
    else
        python3 test-provider-exec.py $provider $regpath $anoncolcheck
    fi
elif [ "$method" = "server" ]; then
    # set registry path
    REG='{"url": "file://'${regpath}'", "localDocRoot": "'${regpath}'", "verifyConfig": {"nopVerify": true}}'

    # start server
    echo "starting server with registry: $REG"
    nohup ./stackql --registry="${REG}" --pgsrv.port=5444 srv &
    sleep 5

    if [ -z "$anoncolcheck" ]; then
        python3 test-provider-server.py $provider
    else
        # TODO implement anoncolcheck for server tests
        python3 test-provider-server.py $provider $anoncolcheck
    fi
fi

