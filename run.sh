#!/bin/bash

COUNTER = 0;
while [ 1 ] ; do
    let COUNTER++
    echo $COUNTER
    for f in instances/*/*.instance.json ; do
        python3 presentation.py $f -r $COUNTER -o;
        if [ $? -eq 3 ]
            then exit 1
        fi
        echo -en "\r\b\b$f"
    done;
done;
