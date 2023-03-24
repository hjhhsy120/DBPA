# Evaluation

## Anomaly Detection

- Split training and test datasets
  - `python dataset.py --test_ratio 0.2 --folder_list data/32_128/single,data/32_256/single,data/64_128/single,data/64_256/single --result_name data_use_8`
  - `python dataset.py --test_ratio 0.4 --folder_list data/32_128/single,data/32_256/single,data/64_128/single,data/64_256/single --result_name data_use_6`
  - `python dataset.py --test_ratio 0.6 --folder_list data/32_128/single,data/32_256/single,data/64_128/single,data/64_256/single --result_name data_use_4`
- Normalization
  - `python norm.py --data_name data_use_8`
  - `python norm.py --data_name data_use_6`
  - `python norm.py --data_name data_use_4`
- Training and evaluation on detection
  - `python detect.py --data_file data_use_[4/6/8]_norm --model_name_list IsolationForest,OneClassSVM,LocalOutlierFactor,SVDD`

## Diagnosis

### Machine Learning Models

- Split training and test datasets
  - `python dataset.py --test_ratio 0.2 --folder_list data/32_128/single,data/32_256/single,data/64_128/single,data/64_256/single --result_name data_use_8`
  - `python dataset.py --test_ratio 0.4 --folder_list data/32_128/single,data/32_256/single,data/64_128/single,data/64_256/single --result_name data_use_6`
  - `python dataset.py --test_ratio 0.6 --folder_list data/32_128/single,data/32_256/single,data/64_128/single,data/64_256/single --result_name data_use_4`
- Normalization
  - `python norm.py --data_name data_use_8`
  - `python norm.py --data_name data_use_6`
  - `python norm.py --data_name data_use_4`
- Training and evaluation on diagnosis
  - `python diagnosis.py --train_file data_use_[4/6/8]_norm --model_name_list Linear,MLP,DecisionTree,RandomForest,XGBoost,LightGBM` 

### AutoMonitor and KNN

- Data preprocessing:`python dataset_automonitor.py`
- Evaluation:`python automonitor_weighted.py --test_size [0.2/0.4/0.6]`