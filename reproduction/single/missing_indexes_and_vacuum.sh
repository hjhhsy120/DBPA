#!bin/bash

bash start_dool_big.sh
for ncolumns in 5 10 20; do
    for colsize in 50 100; do
        for nrows in 2000000 4000000; do
            python createt.py --ncolumns $ncolumns --nrows $nrows --colsize $colsize
            # Missing indexes. The select queries on large tables may slow down.
            for bench in tpcc tatp voter smallbank; do
                echo -e "benchmark ${bench} start"
                $OLTPBENCH_HOME/oltpbenchmark -b $bench -c ./config/pg${bench}_config.xml --execute=true -s 15 -o outputfile &
                sleep 10
                for nclient in 5 10; do
                    for expid in 1 2 3; do
                        python main.py --client_2 $nclient --tabsize $nrows
                    done
                done
                ps -ef | grep oltpbench | awk '$0 !~ /grep/ {print $2}' | xargs kill -9
                sleep 3
                rm -r -f results
                echo -e "benchmark ${bench} end"
            done
            # Vacuum. The vacuums of the deleted data in the data blocks
            # lead to unnecessary I/O consumption. This anomaly occurs in PostgreSQL
            # but not in MySQL, because PostgreSQL appends new data to the end
            # of the tables, but MySQL inserts new data into the vacuums.
            for droprate in 0.5 0.8; do
                python deletet.py --nrows $nrows --droprate $droprate
                for bench in tpcc tatp voter smallbank; do
                    echo -e "benchmark ${bench} start"
                    $OLTPBENCH_HOME/oltpbenchmark -b $bench -c ./config/pg${bench}_config.xml --execute=true -s 15 -o outputfile &
                    sleep 10
                    for nclient in 5 10; do
                        for expid in 1 2 3; do
                            python main.py --client_4 $nclient --tabsize $nrows
                        done
                    done
                    ps -ef | grep oltpbench | awk '$0 !~ /grep/ {print $2}' | xargs kill -9
                    sleep 3
                    rm -r -f results
                    echo -e "benchmark ${bench} end"
                done
            done
        done
    done
done
sleep 900
bash stop_dool_big.sh
