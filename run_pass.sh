#!/bin/bash
LL=5000
LU=10000
P=0
while [ $P -le 30 ]; do
    for f in instances/*/*.instance.json; do
        echo -en "$f"
        L=$(grep -o "\"i\"" $f | wc -l)
        if [ $L -gt $LL ]; then
            if [ $L -le $LU ]; then
                timeout 180 python3 presentation.py $f -a pass -o -e $P -v;
            fi;
        fi;
    done;
    P=$(( $P+5 ))
done
