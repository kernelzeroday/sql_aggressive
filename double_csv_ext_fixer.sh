#!/bin/bash

find . -type f -name '*.csv.csv' | while read file; do
    # Remove the redundant .csv extension
    new_name=$(echo "$file" | sed 's/\.csv\.csv$/.csv/')
    mv -v "$file" "$new_name"
done

