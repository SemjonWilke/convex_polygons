for f in $(git diff --name-only); do
    fp="instances/$(echo $f | cut -d "/" -f2,3 | cut -d "." -f1).instance.json";
    echo $fp;
    python3 bin/HCHECK.py $fp;
    cat $f | grep -e True -e False;
done;
