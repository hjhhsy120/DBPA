#!/bin/bash/
bash start_dool_big.sh
echo -e "normal_begin\t$(date +%Y-%m-%d\ %H:%M:%S)"
for bench in tpcc tatp voter smallbank; do
    echo -e "benchmark ${bench} start"
    $OLTPBENCH_HOME/oltpbenchmark -b $bench -c ./config/pg${bench}_config.xml --execute=true -s 15 -o outputfile
    rm -r -f results
    echo -e "benchmark ${bench} end"
done
echo -e "normal_end\t$(date +%Y-%m-%d\ %H:%M:%S)"
sleep 900
bash stop_dool_big.sh
