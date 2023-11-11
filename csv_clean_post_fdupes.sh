#!/bin/bash

find . -type f -name '*csv*' | while read file; do
    base_name=$(echo "$file" | sed 's/\(.*\)\..*/\1/')
    csv_version="${base_name}.csv"

    if [ -f "$csv_version" ]; then
        size_file=$(stat -f%z "$file")
        size_csv_version=$(stat -f%z "$csv_version")

        if [ $size_file -gt $size_csv_version ]; then
            mv -v "$file" "$csv_version"
        elif [ $size_file -lt $size_csv_version ]; then
            rm -v "$file"
        fi
    else
        mv -v "$file" "$csv_version"
    fi
done

