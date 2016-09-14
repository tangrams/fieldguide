#!/usr/bin/env bash
OS=$(uname)
DIST="UNKNOWN"

# what linux distribution is?
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DIST=$NAME
fi

case "$1" in
    install)

        # INSTALL DEPENDECIES
        if [ $OS == "Linux" ]; then
            echo "Install dependeces for Linux - $DIST"

            if [ "$DIST" == "Amazon Linux AMI" ]; then

                # Amazon Linux
                sudo yum update
                sudo yum upgrade
                sudo yum groupinstall "Development Tools"

            elif [ "$DIST" == "Ubuntu" ]; then

                sudo apt-get update
                sudo apt-get upgrade
                sudo apt-get install build-essential python-setuptools python-dev python-pip

            fi
        fi

        
        if [ ! -d .tmp ]; then
            mkdir tmp
        fi

        pip install fpdf tornado
        ;;

    start)
        sudo python src/server.py $2
        ;;

    stop)
        sudo kill -9 `pgrep -f src/server.py`
        ;;

    *)
        if [ ! -e /usr/local/bin/paparazzi_worker ]; then
            echo "Usage: $0 install"
        else
            echo "Usage: $0 start"
        fi
        exit 1
        ;;
esac