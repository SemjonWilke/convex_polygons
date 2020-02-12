#!/bin/bash
COUNTER=10;
while [ 1 ] ; do
    echo -e "\n$(( $COUNTER )) $(( $COUNTER*10-1 ))"
    for f in instances/*/*.instance.json; do
        echo -en "\r\b\b$f\033[0K"
        python3 presentation.py -l $(( $COUNTER )) $(( $COUNTER*10-1 )) $f -a ben_v3 -o -e 33 -v;
    done;

    COUNTER=$(( $COUNTER*10 ));
done
