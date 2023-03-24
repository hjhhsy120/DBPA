# DBPA: A Benchmark for Transactional Database Performance Anomalies

Please refer to the `README.md` files in each folder for the details of the reproduction procedures and the evaluation scripts.

The datasets are available at: 

https://github.com/hjhhsy120/DBPA_dataset

## Anomaly Types with Reproduction Scripts

The datasets are provided in another repository.

### Single Anomalies

- Concurrent Inserts
- Missing Indexes
- Heavy Workloads
- Vacuum
- Concurrent Commits
- Lock Waits
- Too Many Indexes
- Small Shared Buffer
- I/O Saturation

### Compound Anomalies

- Missing Indexes + Concurrent Commits
- Missing Indexes + Lock Waits
- Missing Indexes + Too Many Indexes
- Heavy Workloads + I/O Saturation
- Vacuum + Too Many Indexes
- Too Many Indexes + Heavy Workloads

## Reproduction

The reproduction procedures of single anomalies are listed as follows.

### Small Shared Buffer

- Script: `small_shared_buffer.sh` 


- Correctness: 
  - Set `ini_knob_values` as 25~40% of available memory as the normal. 
  - Set anomalous values for `shared_buffers` : modify the `knob_values` 
  - Check whether the throughput of OLTPBench is 10% lower than normal.
- Reproduction command: `bash small_shared_buffer.sh >> small_shared_buffer.txt` 

### I/O Saturation Due to Other Processes

- Script: `io_saturation.sh`
- Correctness
  - Set the number of workers for stress-ng: adjust the `-i` in  `io_saturation_server.sh` 
  - Check whether the throughput of OLTPBench is 10% lower than normal.


- Reproduction command: `bash io_saturation.sh >> io_saturation.txt` 

### Highly Concurrent Inserts

- Script: `concurrent_inserts.sh` 


- Correctness: Check whether the latency of injected queries are >1.5 times longer than single-thread inserts
- Reproduction: `bash concurrent_inserts.sh >> concurrent_inserts.txt` 

### Highly Concurrent Commits

- Script: `concurrent_commits.sh` 


- Correctness: check whether the result set is not empty: `select * from pg_stat_activity where wait_event = ‘WALWriteLock’ and state <> ‘idle’;` 
- Reproduction: `bash concurrent_commits.sh >> concurrent_commits.txt` 

### Heavy Workload

- Script: `heavy_workload.sh` 


- Correctness: check whether the average latency of OLTPBench is >1.5 times longer than normal.
- Reproduction: `bash heavy_workload.sh >> heavy_workload.txt` 

### Missing Indexes and Vacuum

- Script: `missing_indexes_and_vacuum.sh` 


- Correctness: 
  - For Missing Indexes, check whether the average latency of injected queries is >20 times longer than indexed scans.
  - For Vacuum, check whether the average latency of injected queries is >1.5 times longer than the same table size without vacuum.
- Reproduction: `bash missing_indexes_and_vacuum.sh >> missing_indexes_and_vacuum.txt` 

### Too Many Indexes

- Script: `too_many_indexes.sh` 
- Correctness: check whether the average latency of injected queries is >1.5 times longer than without the indexes.
- Reproduction: `bash too_many_indexes.sh >> too_many_indexes.txt` 

### Lock Waits

- Script: `lock_waits.sh` 


- Correctness: check whether there are lock wait events.
- Reproduction: `bash lock_waits.sh >> lock_waits.txt` 

## Generation of Compound Anomalies

- Script: `reproduction/compound/generation/generation.py`
- Use the `gen_data` function, where the parameter `data` is a list of samples. Each sample contains two vectors for the anomalies and one vector for the normal background. The vector consists of the monitoring metrics of one timestamp. The parameter `same_type` indicates whether the anomalies are rooted in the same factor, i.e., the environment, the workload amount, and the queries.

## Evaluation

- Dataset preparation: `dataset.py`
- Normalization: `norm.py`
- Anomaly detection: `python detect.py --data_file data_use_[4/6/8]_norm --model_name_list IsolationForest,OneClassSVM,LocalOutlierFactor,SVDD`
- Anomaly diagnosis (ML):  `python diagnosis.py --train_file data_use_[4/6/8]_norm --model_name_list Linear,MLP,DecisionTree,RandomForest,XGBoost,LightGBM` 
- Anomaly diagnosis (AutoMonitor and KNN): `python automonitor_weighted.py --test_size [0.2/0.4/0.6]`

## Citation

```
Shiyue Huang, Ziwei Wang, Xinyi Zhang, Yaofeng Tu, zhongliang Li, and Bin Cui:
"DBPA: A Benchmark for Transactional Database Performance Anomalies"
SIGMOD 2023
```