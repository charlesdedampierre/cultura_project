# Loop to continuously capture and update the log file
while true; do
    # Save tmux log and append to server_log.txt
    tmux capture-pane -t unseen_model -p >> server_log.txt
    # Wait for some time before capturing again (adjust sleep duration as needed)
    sleep 1
done