#!/bin/bash

ini_knob_names=(shared_buffers)
ini_knob_values=(16GB)
knob_names=(shared_buffers shared_buffers shared_buffers shared_buffers)
knob_values=(512MB 128MB 32MB 8MB)
propcnt=(1 1 1 1)
for ((i = 0; i < 4; i++)); do
    #-----------------------set knobs
    python set_knob.py -kn ${ini_knob_names[0]} -kv ${ini_knob_values[0]}
    python set_knob.py -kn ${knob_names[i]} -kv ${knob_values[i]}
    #----------------------restart database
    ssh user@localhost 'bash -s' <<'ENDSSH'
sleep 120
pg_ctlcluster 12 main restart -m i
sleep 1200
ENDSSH
    echo -e "fault_knob_${knob_names[i]}_${knob_values[i]}_begin\t$(date +%Y-%m-%d\ %H:%M:%S)"
    bash start_dool_big.sh
    for ncolumns in 5 40; do
        for colsize in 50 100; do
            python createt.py --ncolumns $ncolumns --nrows 100 --colsize $colsize
            for bench in tpcc tatp voter smallbank; do
                echo -e "benchmark ${bench} start"
                $OLTPBENCH_HOME/oltpbenchmark -b $bench -c ./config/pg${bench}_config.xml --execute=true -s 15 -o outputfile &
                for nclient in 100 150; do
                    for expid in 1; do
                        python main.py --client_1 $nclient --ncolumns $ncolumns --nrows 1 --colsize $colsize
                    done
                done
                # sleep 1080
                ps -ef | grep oltpbench | awk '$0 !~ /grep/ {print $2}' | xargs kill -9
                sleep 3
                rm -r -f results
                echo -e "benchmark ${bench} end"
            done
        done
    done
    echo -e "fault_knob_${knob_names[i]}_${knob_values[i]}_end\t$(date +%Y-%m-%d\ %H:%M:%S)"
    sleep 900
    bash stop_dool_big.sh
done

python set_knob.py -kn ${ini_knob_names[0]} -kv ${ini_knob_values[0]}

ssh user@localhost 'bash -s' <<'ENDSSH'
pg_ctlcluster 12 main restart -m i
sleep 900
ENDSSH
