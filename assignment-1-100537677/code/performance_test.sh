#!/etc/bin/env bash

for i in $(seq 0 5 10)
do
   users=$i
   if [ $users -eq 0 ]; then
       users=1
   fi
   requests=2
   file="../data/listings_summary.csv"
   echo "==========================================="
   echo "Running $users users and $requests requests"
   result=`python3 performance.py --database_uri localhost:27117 --database airbnb --collection listing --w 1 --j false --filepath ${file} --num_users ${users} --num_requests ${requests}`
   # note: "" is needed to preserve the newlines
   echo "$result"
done