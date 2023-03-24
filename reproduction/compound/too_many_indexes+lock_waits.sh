#!/bin/bash/

bench_list=(tpcc tatp smallbank)
table_list=(customer subscriber checking)
column_list=(c_payment_cnt bit_1 bal)

bash start_dool_big.sh
for ncolumns in 50 80; do
    for colsize in 20; do
        for nrows in 400000; do
            python createt.py --ncolumns $ncolumns --nrows $nrows --colsize $colsize
            for nindex10 in 6 8; do
                nindex=$(expr $ncolumns \* $nindex10 / 10)
                python add_index.py -c $nindex
                python id_index.py -c 1
                for nclient in 5 10; do
                    for expid in 1; do
                        sleep 5
                        echo -e "fault_manyindex_${nindex10}_begin\t$(date +%Y-%m-%d\ %H:%M:%S)"
                        python update_sql.py -c $nclient --ncolumns $ncolumns --nrows $nrows --colsize $colsize --duration 7200 &
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
                        ps -ef | grep update_sql | awk '$0 !~ /grep/ {print $2}' | xargs kill -9
                        sleep 3
                        echo -e "fault_manyindex_${nindex10}_end\t$(date +%Y-%m-%d\ %H:%M:%S)"
                    done
                done
                python add_index.py -c 0
            done
        done
    done
done
sleep 900
bash stop_dool_big.sh