#!/usr/bin/env bash

case "$1" in
    install)
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