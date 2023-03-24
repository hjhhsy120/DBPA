#!/bin/bash/

bash start_dool_big.sh
for ncolumns1 in 5 20; do
    for colsize1 in 50; do
        for nrows1 in 4000000; do
            python createt.py --ncolumns $ncolumns1 --nrows $nrows1 --colsize $colsize1 --table_name aa
            for ncolumns2 in 5 10; do
                for colsize2 in 20; do
                    python createt.py --ncolumns $ncolumns2 --nrows 100 --colsize $colsize2 --table_name bb
                    for bench in tpcc tatp smallbank voter; do
                        echo -e "benchmark ${bench} start"
                        $OLTPBENCH_HOME/oltpbenchmark -b $bench -c ./config/pg${bench}_config.xml --execute=true -s 15 -o outputfile &
                        sleep 10
                        for nclient1 in 5 10; do
                            for expid1 in 1; do
                                echo -e "fault_2_begin\t$(date +%Y-%m-%d\ %H:%M:%S)"
                                python main.py --client_2 $nclient1 --tabsize $nrows1 --table_name aa --duration 7200 &
                                sleep 60
                                for nclient2 in 50 100 150; do
                                    for expid2 in 1 2; do
                                        python main.py --client_5 $nclient2 --ncolumns $ncolumns2 --nrows 1 --colsize $colsize2 --table_name bb
                                    done
                                done
                                ps -ef | grep main.py | awk '$0 !~ /grep/ {print $2}' | xargs kill -9
                                sleep 3
                                echo -e "fault_2_end\t$(date +%Y-%m-%d\ %H:%M:%S)"
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
done
sleep 900
bash stop_dool_big.sh
