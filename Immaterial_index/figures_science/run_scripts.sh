#!/bin/bash

# Assuming the scripts are in the same directory as this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Disable immediate exit on error
set +e

# Run all scripts starting with 'region_'
for script in $SCRIPT_DIR/region*.R; do
    echo "Running $script"
    Rscript "$script"

    # Check the exit status of the last command
    if [ $? -ne 0 ]; then
        echo "Error running $script. Continuing to the next script."
    fi
done

# Enable immediate exit on error
set -e
