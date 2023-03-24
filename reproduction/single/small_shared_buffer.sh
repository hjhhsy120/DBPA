#!/bin/bash

# Small shared buffer. It is representative of bad database configurations. 
# The shared buffer works as the cache of the disk, which can
# significantly influence the database performance. A small shared
# buffer is a common anomaly caused by mistaken adjustments.
ini_knob_names=(shared_buffers)
ini_knob_values=(16GB)
knob_names=(shared_buffers shared_buffers shared_buffers shared_buffers shared_buffers)
knob_values=(16GB 512MB 128MB 32MB 8MB)
for ((i = 0; i < 5; i++)); do
    #-----------------------set knob
    python set_knob.py -kn ${ini_knob_names[0]} -kv ${ini_knob_values[0]}
    python set_knob.py -kn ${knob_names[i]} -kv ${knob_values[i]}
    #----------------------restart database
    ssh user@localhost 'bash -s' <<'ENDSSH'
sleep 120
pg_ctlcluster 12 main restart -m i
sleep 1200
ENDSSH
    bash start_dool_big.sh
    #----------------------OLTPBENCH
    for bench in tpcc tatp voter smallbank; do
        echo -e "benchmark ${bench} start"
        echo -e "fault_knob_${knob_names[i]}_${knob_values[i]}_begin\t$(date +%Y-%m-%d\ %H:%M:%S)"
        $OLTPBENCH_HOME/oltpbenchmark -b $bench -c ./expconfig/pg${bench}_config_setknob.xml --execute=true -s 15 -o outputfile
        echo -e "fault_knob_${knob_names[i]}_${knob_values[i]}_end\t$(date +%Y-%m-%d\ %H:%M:%S)"
        sleep 15
        rm -r -f results
        echo -e "benchmark ${bench} end"
    done
    sleep 900
    bash stop_dool_big.sh
done

python set_knob.py -kn ${ini_knob_names[0]} -kv ${ini_knob_values[0]}

ssh user@localhost 'bash -s' <<'ENDSSH'
pg_ctlcluster 12 main restart -m i
sleep 900
ENDSSH
