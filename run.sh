#!/bin/bash

COUNTER = 0;
while [ 1 ] ; do
    COUNTER=$[COUNTER +1]
    echo $COUNTER
    for f in instances/*/*.instance.json ; do
        python3 presentation.py -r $COUNTER -o $f;
        echo -en "\r\b\b$f"
    done;
done;
