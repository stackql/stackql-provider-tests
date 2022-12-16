provider=$1
regpath=$2
anoncolcheck=$3

if [ -z "$provider" ]; then
    echo "provider must be set"
    exit 1
fi

echo "testing provider: $provider"

if [ -z "$regpath" ]; then
    regpath=$(pwd)
fi

echo "registry path: $regpath"

# clone pystackql if not present

if [ ! -d "pystackql" ]; then
    git clone https://github.com/stackql/pystackql.git
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

if [ -z "$anoncolcheck" ]; then
    python3 test-provider.py $provider $regpath
else
    python3 test-provider.py $provider $regpath $anoncolcheck
fi