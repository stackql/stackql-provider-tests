provider=$1
signed=$2
regpath=$3
anoncolcheck=$4

# check for another stackql server running
if [ -n "$(lsof -i :5444)" ]; then
    echo "another server is running on port 5444, please stop it"
    exit 1
fi

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

# install packages

pip install -q -r requirements.txt

# download and unzip stackql binary

if [ ! -f stackql ]
then
    wget -q https://releases.stackql.io/stackql/latest/stackql_linux_amd64.zip
    unzip stackql_linux_amd64.zip
fi

 chmod +x stackql

# do checks

# set registry path
if [ "$SIGNED" = "true" ]; then
    REG='{"url": "file://'${regpath}'", "localDocRoot": "'${regpath}'", "verifyConfig": {"nopVerify": false}}'
else
    REG='{"url": "file://'${regpath}'", "localDocRoot": "'${regpath}'", "verifyConfig": {"nopVerify": true}}'
fi

# start server if not running
echo "checking if server is running"
ps
ps -ef | grep stackql
ps -ef | grep stackql | grep -v grep

if [ -z "$(ps -ef | grep stackql | grep -v grep)" ]; then
    echo "starting server with registry: $REG"
    nohup ./stackql --registry="${REG}" --pgsrv.port=5444 srv &
    sleep 5
else
    echo "server is already running"
fi

if [ -z "$anoncolcheck" ]; then
    python3 test-provider.py $provider
else
    # TODO implement anoncolcheck for server tests
    python3 test-provider.py $provider $anoncolcheck
fi