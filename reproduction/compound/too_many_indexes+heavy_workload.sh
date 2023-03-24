#!/bin/bash/

propcnt=(1 1 1 1)
cnt=0
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
                        cnt=0
                        for bench in tpcc tatp voter smallbank; do
                            echo -e "benchmark ${bench} start"
                            $OLTPBENCH_HOME/oltpbenchmark -b ${bench} -c ./config/pg${bench}_config.xml --execute=true -s 15 -o outputfile &
                            for nclient in 64 128; do
                                prop=0
                                while ((prop < ${propcnt[$cnt]})); do
                                    python setconfig.py expconfig/pg${bench}_config.xml expconfig/pg${bench}_config_exp.xml $nclient $bench $prop
                                    for expid in 1 2; do
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
