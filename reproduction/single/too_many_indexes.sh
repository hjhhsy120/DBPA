#!/bin/bash/

# Too many indexes. The performance of the insert, delete, and
# update queries may slow down.
bash start_dool_big.sh
for ncolumns in 50 60 70 80; do
    for colsize in 10 20; do
        for nrows in 200000 400000; do
            python createt.py --ncolumns $ncolumns --nrows $nrows --colsize $colsize
            for bench in tpcc tatp smallbank voter; do
                echo -e "benchmark ${bench} start"
                $OLTPBENCH_HOME/oltpbenchmark -b $bench -c ./config/pg${bench}_config.xml --execute=true -s 15 -o outputfile &
                sleep 10
                for nindex10 in 0 6 8; do
                    nindex=$(expr $ncolumns \* $nindex10 / 10)
                    python add_index.py -c $nindex
                    python id_index.py -c 1
                    for nclient in 5 10; do
                        for expid in 1 2 3; do
                            sleep 5
                            echo -e "fault_manyindex_${nindex10}_begin\t$(date +%Y-%m-%d\ %H:%M:%S)"
                            python update_sql.py -c $nclient --ncolumns $ncolumns --nrows $nrows --colsize $colsize
                            echo -e "fault_manyindex_${nindex10}_end\t$(date +%Y-%m-%d\ %H:%M:%S)"
                        done
                    done
                    python add_index.py -c 0
                done
                ps -ef | grep oltpbench | awk '$0 !~ /grep/ {print $2}' | xargs kill -9
                sleep 3
                rm -r -f results
                echo -e "benchmark ${bench} end"
            done
        done
    done
done
sleep 900
bash stop_dool_big.sh
