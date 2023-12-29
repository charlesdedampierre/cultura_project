#!/bin/bash

# Find all R scripts in the current directory
for file in *.R; do
    # Update the paths in each file
    sed -i.bak 's|file = "../../results/df_individuals_score.csv"|file = "../../results/df_individuals_score_science.csv"|g' "$file"
    sed -i.bak 's|file = "../../results/df_region_score.csv"|file = "../../results/df_region_score_science.csv"|g' "$file"
    
    echo "Updated paths in $file"
done
