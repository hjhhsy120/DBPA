#!/bin/bash
sess1=monitoring1
tmux has-session -t $sess1 2>/dev/null
if [ $? == 0 ]; then
    tmux send-keys -t $sess1 C-c
    sleep 5
    tmux kill-session -t $sess1 && echo $sess1" killed"
fi
sess2=monitoring2
tmux has-session -t $sess2 2>/dev/null
if [ $? == 0 ]; then
    tmux send-keys -t $sess2 C-c
    sleep 5
    tmux kill-session -t $sess2 && echo $sess2" killed"
fi