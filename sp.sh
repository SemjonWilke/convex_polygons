#!/bin/bash

for f in instances/rand_ortho/*.instance.json ; do
    echo -en "\r\b\b$f\033[0K"
    python3 topo_start.py $f;
done;
