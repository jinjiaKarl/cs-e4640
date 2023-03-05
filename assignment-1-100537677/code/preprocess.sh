#!/etc/bin/env bash
# add city column to a csv file

if [ $# != 2 ]; then
    echo "Usage: $0 csv_file_path city"
    exit 1
fi
file=$1
city=$2
sed -i.bak "1s/^/city,/; 2,$ s/^/${city},/" ${file}