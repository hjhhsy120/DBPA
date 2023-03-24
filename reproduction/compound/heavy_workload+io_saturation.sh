#!bin/bash

bash start_dool_big.sh
propcnt=(1 1 1 1)
cnt=0
for bench in tpcc tatp voter smallbank; do
    echo -e "benchmark ${bench} start"
    $OLTPBENCH_HOME/oltpbenchmark -b ${bench} -c ./config/pg${bench}_config.xml --execute=true -s 15 -o outputfile &
    sleep 10
    for nclient in 64 128; do
        prop=0
        while ((prop < ${propcnt[$cnt]})); do
            python setconfig.py expconfig/pg${bench}_config.xml expconfig/pg${bench}_config_exp.xml $nclient $bench $prop 7200
            for expid in 1 2 3 4; do
                echo -e "thefault3_begin\t$(date +%Y-%m-%d\ %H:%M:%S)"
                $OLTPBENCH_HOME/oltpbenchmark -b ${bench} -c ./expconfig/pg${bench}_config_exp.xml --execute=true &
                sleep 10
                ssh user@localhost 'bash -s' <<'ENDSSH'
cd /home/user && bash io_saturation_server.sh
ENDSSH
                ps -ef | grep ./expconfig | awk '$0 !~ /grep/ {print $2}' | xargs kill -9
                sleep 3
                echo -e "thefault3_end\t$(date +%Y-%m-%d\ %H:%M:%S)"
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
