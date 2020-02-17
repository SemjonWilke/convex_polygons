#!/bin/bash
COUNTER=1000;
LIMIT=1000;
while [ 1 ] ; do
    echo -e "\n$(( $COUNTER+1 )) $(( $COUNTER+$LIMIT ))"
    for f in instances/*/*.instance.json; do
        echo -en "\r\b\b$f\033[0K"
        python3 presentation.py -l $(( $COUNTER+1 )) $(( $COUNTER+$LIMIT )) $f -a nested -o -v;
    done;

    COUNTER=$(( $COUNTER+$LIMIT ));
    CHECK=$(( $LIMIT*10 ));
    if [ $COUNTER -eq $CHECK ];
    then
        LIMIT=$CHECK;
        sleep 1
    fi;
done
