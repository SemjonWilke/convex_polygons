#!/bin/bash
COUNTER=1;
while [ 1 ] ; do
    echo -e "\n$COUNTER"
    for f in instances/*/*.instance.json ; do
        echo -en "\r\b\b$f\033[0K"
        python3 presentation.py $f -r $COUNTER -o;
        python3 checker.py $f;
        if [ $? -eq 3 ]
            then exit 1
        fi
    done;
    let COUNTER++
done;
