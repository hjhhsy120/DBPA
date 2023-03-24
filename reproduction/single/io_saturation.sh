#!/bin/bash

# I/O saturation due to other processes. It is a representative of
# resource bottleneck and differs from the anomaly caused by the workload.
bash start_dool_big.sh
for bench in tpcc tatp voter smallbank; do
    echo -e "benchmark ${bench} start"
    $OLTPBENCH_HOME/oltpbenchmark -b $bench -c ./config/pg${bench}_config.xml --execute=true -s 15 -o outputfile &
    ssh user@localhost 'bash -s' <<'ENDSSH'
cd /home/user && bash io_saturation_server.sh
ENDSSH
    ps -ef | grep oltpbench | awk '$0 !~ /grep/ {print $2}' | xargs kill -9
    sleep 3
    rm -r -f results
    echo -e "benchmark ${bench} end"
done
sleep 900
bash stop_dool_big.sh

