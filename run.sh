#!/bin/bash
COUNTER=1;
while [ 1 ] ; do
    echo -e "\n$COUNTER"
    for f in instances/*_*/*.instance.json ; do
        echo -en "\r\b\b$f\033[0K"
        python3 presentation.py $f -r $COUNTER -o -a ben_v1;
        if [ $? -eq 0 ]
            then python3 checker.py $f;
        fi
        if [ $? -eq 3 ]
            then exit 1
        fi
    done;
    let COUNTER++
done;
