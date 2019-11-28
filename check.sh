#!/bin/bash

for f in instances/*/*.instance.json ; do
    echo -en "\r\b\b$f\033[0K"
    python checker.py $f;
done;
