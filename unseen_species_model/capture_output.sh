#!/bin/bash

while true; do
    tmux capture-pane -t unseen_model:0 -p >> output.log
    sleep 5  # Adjust the sleep duration as needed
done