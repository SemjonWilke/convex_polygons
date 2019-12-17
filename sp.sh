#!/bin/bash

for f in instances/*/*.instance.json ; do
    echo -en "\r\b\b$f\033[0K"
    python3 topo_start.py $f -s 50;
done;

for f in instances/*/*.instance.json ; do
    echo -en "\r\b\b$f\033[0K"
    python3 topo_start.py $f -s 75;
done;

for f in instances/*/*.instance.json ; do
    echo -en "\r\b\b$f\033[0K"
    python3 topo_start.py $f -s 100;
done;

for f in instances/*/*.instance.json ; do
    echo -en "\r\b\b$f\033[0K"
    python3 topo_start.py $f -s 200;
done;
