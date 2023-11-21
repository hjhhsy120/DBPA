# Reproduction

## Preparation

### Folders

+ single: reproduction of single anomalies
+ compound: reproduction of selected compound anomalies
+ utils: scripts that support the reproduction procedures
+ config: OLTPBench configuration files for background workload
+ expconfig: OLTPBench configuration files for injected workload
+ propconfig: OLTPBench transaction ratios for injected workload
+ server_files: scripts to place on the server
+ codegen: generator of reproduction scripts

### Software Requirements
+ On the database server, PostgreSQL and stress-ng should be installed.
  + Currently the reproduction scripts are applicable for PostgreSQL, but you can easily modify them for MySQL.
+ On the client, the OLTPBench should be installed.

### Dool Preparation

- Install dool (from Github) on the database server.
- Add the following lines to `~/.bashrc` on the database server.

```sh
export DSTAT_PG_USER=postgres
export DSTAT_PG_PWD=YOUR_PASSWORD
export DSTAT_PG_HOST=YOUR_IP
export DSTAT_PG_PORT=YOUR_PORT
```

### OLTPBench Preparation
+ Set the IP, port, user, and password for the database by modifying the following files
    + create_database.py
    + Configuration files in the folder 'config'
+ Refer to `config/README.md` to set the terminals tags.
+ Create the databases: `python create_database.py` 
+ Create the tables and insert the data: `bash load_OLTP.sh` 

### Reproduction Scripts Preparation

- Set the IP, port, user, and password for the database by modifying the following files
  - add_index.py
  - database.py
  - id_index.py
  - lock_wait.py
  - set_knob.py
  - update_sql.py
  - Configuration files in the folder 'expconfig'
- Set the IP and port for the Server by modifying the following files
  - io_saturation.sh
  - small_shared_buffer.sh
  - heavy_workload+io_saturation.sh
  - small_shared_buffer+concurrent_inserts.sh
  - too_many_indexes+io_saturation.sh
  - start_dool_big.sh
  - stop_dool_big.sh

## Anomaly Reproduction

### Small Shared Buffer

- Script: `small_shared_buffer.sh` 

+ Correctness: 
  + Set `ini_knob_values` as 25~40% of available memory as the normal. 
  + Set anomalous values for `shared_buffers` : modify the `knob_values` 
  + Check whether the throughput of OLTPBench is 10% lower than normal.
+ Reproduction command: `bash small_shared_buffer.sh >> small_shared_buffer.txt` 

### I/O Saturation Due to Other Processes

- Script: `io_saturation.sh`
- Correctness
  - Set the number of workers for stress-ng: adjust the `-i` in  `io_saturation_server.sh` 
  - Check whether the throughput of OLTPBench is 10% lower than normal.

+ Reproduction command: `bash io_saturation.sh >> io_saturation.txt` 

### Highly Concurrent Inserts

- Script: `concurrent_inserts.sh` 

+ Correctness: Check whether the latency of injected queries are >1.5 times longer than single-thread inserts
+ Reproduction: `bash concurrent_inserts.sh >> concurrent_inserts.txt` 

### Highly Concurrent Commits

- Script: `concurrent_commits.sh` 

+ Correctness: check whether the result set is not empty: `select * from pg_stat_activity where wait_event = ‘WALWriteLock’ and state <> ‘idle’;` 
+ Reproduction: `bash concurrent_commits.sh >> concurrent_commits.txt` 

### Heavy Workload

- Script: `heavy_workload.sh` 

+ Correctness: check whether the average latency of OLTPBench is >1.5 times longer than normal.
+ Reproduction: `bash heavy_workload.sh >> heavy_workload.txt` 

### Missing Indexes and Vacuum

- Script: `missing_indexes_and_vacuum.sh` 

+ Correctness: 
  + For Missing Indexes, check whether the average latency of injected queries is >20 times longer than indexed scans.
  + For Vacuum, check whether the average latency of injected queries is >1.5 times longer than the same table size without vacuum.
+ Reproduction: `bash missing_indexes_and_vacuum.sh >> missing_indexes_and_vacuum.txt` 

### Too Many Indexes
+ Script: `too_many_indexes.sh` 
+ Correctness: check whether the average latency of injected queries is >1.5 times longer than without the indexes.
+ Reproduction: `bash too_many_indexes.sh >> too_many_indexes.txt` 

### Lock Waits

- Script: `lock_waits.sh` 

+ Correctness: check whether there are lock wait events.
+ Reproduction: `bash lock_waits.sh >> lock_waits.txt` 

### Compound Anomalies

#### Missing Indexes + Lock Waits

+ `bash missing_indexes+lock_waits.sh >> missing_indexes+lock_waits.txt`

#### Missing Indexes + Too Many Indexes

+ `bash missing_indexes+too_many_indexes.sh >> missing_indexes+too_many_indexes.txt`

#### Too Many Indexes + Lock Waits(too_many_indexes+lock_waits.sh)

+ `bash too_many_indexes+lock_waits.sh >> too_many_indexes+lock_waits.txt`

#### Too Many Indexes + Heavy Workload(too_many_indexes+heavy_workload.sh)

+ `bash too_many_indexes+heavy_workload.sh >> too_many_indexes+heavy_workload.txt`

#### Too Many Indexes + I/O Saturation Due to Other Processes(too_many_indexes+io_saturation.sh)

+ `bash too_many_indexes+io_saturation.sh >> too_many_indexes+io_saturation.txt`

#### Heavy Workload + I/O Saturation Due to Other Processes(heavy_workload+io_saturation.sh)

+ `bash heavy_workload+io_saturation.sh >> heavy_workload+io_saturation.txt`

#### Missing Indexes + Highly Concurrent Commits(missing_indexes+concurrent_commits.sh)

+ `bash missing_indexes+concurrent_commits.sh >> missing_indexes+concurrent_commits.txt`

#### Too Many Indexes + Vacuum(vacuum+too_many_indexes.sh)

+ `bash vacuum+too_many_indexes.sh >> vacuum+too_many_indexes.txt`

#### Small Shared Buffer + Highly Concurrent Inserts(small_shared_buffer+concurrent_inserts.sh)

+ `bash small_shared_buffer+concurrent_inserts.sh >> small_shared_buffer+concurrent_inserts.txt`

### Data Processing

+ Monitoring metrics on the server: `metricsx.csv` and `metricsy.csv` 
+ Execute `python merge_csv.py metricsx.csv metricsy.csv` for `merge.csv`
+ Log files on the client: `*.txt` . Refer to the timestamps in the log files to slice the anomalous data from `merge.csv` 

## Generation of Compound Anomalies

- Script: `compound/generation/generation.py`
- Use the `gen_data` function, where the parameter `data` is a list of samples. Each sample contains two vectors for the anomalies and one vector for the normal background. The vector consists of the monitoring metrics of one timestamp. The parameter `same_type` indicates whether the anomalies are rooted in the same factor, i.e., the environment, the workload amount, and the queries.

## Codegen

- Reproduction scripts can be generated from `XML` files with the `codegen` tool.
- Usage example: `python codegen.py --config template.xml --output temp`
- It generates the `Shell` script from `template.xml` into the `temp` folder. Example `XML` files are provided in the `codegen` folder.
