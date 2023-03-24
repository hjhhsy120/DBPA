# Configuration Files for OLTPBench

Please set the terminals tag with the following steps (TPC-C as an example)

1. Server: monitor I/O `iostat -x 5` 
2. Client: start TPC-C benchmark `$OLTPBENCH_HOME/oltpbenchmark -b tpcc -c ./config/pgtpcc_config.xml --execute=true -s 5 -o outputfile` 
3. Watch the %util metric on Server after 5 seconds. if %util > 60%, then modify the terminals tag to be smaller. If %util <= 60%, then finish.