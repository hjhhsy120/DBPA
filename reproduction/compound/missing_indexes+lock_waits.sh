#!bin/bash

bench_list=(tpcc tatp smallbank)
table_list=(customer subscriber checking)
column_list=(c_payment_cnt bit_1 bal)

bash start_dool_big.sh
for ncolumns in 5 20; do
    for colsize in 50; do
        for nrows in 4000000; do
            python createt.py --ncolumns $ncolumns --nrows $nrows --colsize $colsize
            for nclient in 5 10; do
                for expid in 1 2; do
                    echo -e "fault_2_begin\t$(date +%Y-%m-%d\ %H:%M:%S)"
                    python main.py --client_2 $nclient --tabsize $nrows --duration 7200 &
                    sleep 60
                    for i in 0 1 2; do
                        echo -e "benchmark ${bench_list[$i]} start"
                        for expid in 1 2; do
                            python lock_wait.py --duration 60 --database_name ${bench_list[$i]} --table_name ${table_list[$i]} --column_name ${column_list[$i]}
                            ps -ef | grep oltpbench | awk '$0 !~ /grep/ {print $2}' | xargs kill -9
                            sleep 3
                            rm -r -f results
                        done
                        echo -e "benchmark ${bench_list[$i]} end"
                    done
                    ps -ef | grep main.py | awk '$0 !~ /grep/ {print $2}' | xargs kill -9
                    sleep 3
                    echo -e "fault_2_end\t$(date +%Y-%m-%d\ %H:%M:%S)"
                done
            done
        done
    done
done
sleep 900
bash stop_dool_big.sh
