#!/bin/bash
for f in instances/*/*.instance.json ; do
    echo -en "\r\b\b$f\033[0K"
    python3 presentation.py $f -o -a abbas;
    python3 presentation.py $f -o -a ben_v3;
done;

:' this is a multiline comment
COUNTER=620;
while [ 1 ] ; do
    echo -e "\n$COUNTER"
    for f in instances/*/*.instance.json ; do
        echo -en "\r\b\b$f\033[0K"
        python3 presentation.py $f -r $COUNTER -o -a ben_v1 2> /dev/null;
        if [ $? -eq 3 ]
            then exit 1
        fi
    done;
    let COUNTER++
done;
'
