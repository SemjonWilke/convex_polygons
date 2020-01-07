#!/bin/bash
for f in instances/*/*.instance.json ; do
    echo -en "\r\b\b$f\033[0K"
    python3 presentation.py $f -o -a abbas;
done;
