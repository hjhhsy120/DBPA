#!/bin/bash

while (( i++ < 15))
do
    echo -e "fault_IO_begin_1\t$(date +%Y-%m-%d\ %H:%M:%S)"
    sleep 30
    echo -e "fault_IO_begin_2\t$(date +%Y-%m-%d\ %H:%M:%S)"
    stress-ng -i 4 -t 60s
    echo -e "fault_IO_end_1\t$(date +%Y-%m-%d\ %H:%M:%S)"
    sleep 30
    echo -e "fault_IO_end_2\t$(date +%Y-%m-%d\ %H:%M:%S)"
done
