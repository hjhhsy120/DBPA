#!/bin/bash
ssh user@localhost 'bash -s' << 'ENDSSH'
cd /home/user && bash start_dool2.sh
echo -e "server_dool_begin\t$(date +%Y-%m-%d\ %H:%M:%S)"
ENDSSH
echo -e "client_dool_begin\t$(date +%Y-%m-%d\ %H:%M:%S)"
