#!/bin/bash
COUNTER=0;
LIMIT=10;
while [ 1 ] ; do
    echo -e "\n$(( $COUNTER+1 )) $(( $COUNTER+$LIMIT ))"
    for f in instances/*/*.instance.json; do
        echo -en "\r\b\b$f\033[0K"
        python3 presentation.py -l $(( $COUNTER+1 )) $(( $COUNTER+$LIMIT )) $f -a ben_v3 -o -e 33;
    done;

    COUNTER=$(( $COUNTER+$LIMIT ));
    CHECK=$(( $LIMIT*10 ));
    if [ $COUNTER -eq $CHECK ];
    then
        LIMIT=$CHECK;
    fi;
done
