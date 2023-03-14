#!/etc/bin/env bash

# create 10 files
for i in {1..10}
do
    cp ../data/listings_summary.csv ./client-staging-input-directory/tenant1-listings_summary_$i.csv
done

for i in {1..10}
do
    cp ../data/listings_summary.csv ./client-staging-input-directory/tenant2-listings_summary_$i.csv
done
