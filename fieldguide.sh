#!/usr/bin/env bash

case "$1" in
    install)
        if [ ! -d .tmp ]; then
            mkdir tmp
        fi

        pip install fpdf tornado
        ;;
    start)
        python src/server.py 
        ;;
esac