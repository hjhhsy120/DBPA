#!bin/bash

# Heavy workload. Simply increasing the workload amount can
# lead to heavy resource consumption and degrades performance.
bash start_dool_big.sh
propcnt=(7 4 1 6)
cnt=0
for bench in tpcc tatp voter smallbank; do
    echo -e "benchmark ${bench} start"
    $OLTPBENCH_HOME/oltpbenchmark -b ${bench} -c ./config/pg${bench}_config.xml --execute=true -s 15 -o outputfile &
    for nclient in 64 128; do
        prop=0
        while ((prop < ${propcnt[$cnt]})); do
            python setconfig.py expconfig/pg${bench}_config.xml expconfig/pg${bench}_config_exp.xml $nclient $bench $prop
            for expid in 1 2 3 4 5; do
                python main.py --client_3 $nclient --bench $bench --benchconfig ./expconfig/pg${bench}_config_exp.xml
            done
            let prop++
        done
    done
    ps -ef | grep oltpbench | awk '$0 !~ /grep/ {print $2}' | xargs kill -9
    sleep 3
    rm -r -f results
    echo -e "benchmark ${bench} end"
    let cnt++
done
sleep 900
bash stop_dool_big.sh

