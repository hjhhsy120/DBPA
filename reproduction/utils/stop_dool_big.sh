#!/bin/bash
ssh user@localhost 'bash -s' << 'ENDSSH'
cd /home/user && bash stop_dool2.sh
echo -e "server_dool_end\t$(date +%Y-%m-%d\ %H:%M:%S)"
cd /home/user && mv metricsx.csv metricsx_$(date +%Y-%m-%d-%H-%M-%S).csv
cd /home/user && mv metricsy.csv metricsy_$(date +%Y-%m-%d-%H-%M-%S).csv
ENDSSH
echo -e "client_dool_end\t$(date +%Y-%m-%d\ %H:%M:%S)"
