#!/bin/bash/
for bench in tpcc tatp smallbank voter; do
    echo -e "benchmark ${bench} start"
    $OLTPBENCH_HOME/oltpbenchmark -b $bench -c ./config/pg${bench}_config.xml --create=true --load=true -s 15 -o outputfile
    ps -ef | grep oltpbench | awk '$0 !~ /grep/ {print $2}' | xargs kill -9
    sleep 3
    rm -r -f results
    echo -e "benchmark ${bench} end"
done