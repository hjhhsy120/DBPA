#!/bin/bash/

# Lock waits. The queries with writes require the locks, 
# which can increase the latency.
bench_list=(tpcc tatp smallbank)
table_list=(customer subscriber checking)
column_list=(c_payment_cnt bit_1 bal)
bash start_dool_big.sh
for i in 0 1 2; do
    echo -e "benchmark ${bench_list[$i]} start"
    for expid in 1 2 3 4 5 6 7 8 9 10; do
        python lock_wait.py --duration 60 --database_name ${bench_list[$i]} --table_name ${table_list[$i]} --column_name ${column_list[$i]}
        ps -ef | grep oltpbench | awk '$0 !~ /grep/ {print $2}' | xargs kill -9
        sleep 3
        rm -r -f results
    done
    echo -e "benchmark ${bench_list[$i]} end"
done
sleep 900
bash stop_dool_big.sh