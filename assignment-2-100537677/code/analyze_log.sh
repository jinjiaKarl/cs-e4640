#!/bin/bash

log_path="../logs/batchmanager.log"
if [ ! -f $log_path ]; then
    echo "Log file not found"
    exit 1
fi

if [ "$1" == "all" ]; then
    # Use grep to filter the logs for the specified tenant and extract the successful rows
    successful_rows=$(grep "sucessful_rows': " $log_path | awk -F"sucessful_rows': " '{total += $2} END {print total}')

    echo "Total successful rows: $successful_rows"
    exit 0
fi

# Get the tenant name from user input
echo "Enter the tenant name:"
read tenant_name

# Use grep to filter the logs for the specified tenant and extract the successful rows
successful_rows=$(grep "tanent_name': '$tenant_name'" $log_path | awk -F"sucessful_rows': " '{total += $2} END {print total}')

echo "Total successful rows for $tenant_name: $successful_rows"