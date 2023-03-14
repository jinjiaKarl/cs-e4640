# This is a deployment/installation guide

The deployment docker-compose.yml file is reused from the previous assignment. I have added opentelemetry-collector and prometheus to the docker-compose file.

## Deployment
```
cd code
python3 -m venv .
source ./bin/activate

pip3 install -r requirements.txt

# start kafka and sharded mongo cluster
docker compose up -d

# initialize the cluster
bash mongodb_init.sh

# check sharding
docker-compose exec router01 mongosh --port 27017
[direct: mongos] test> use airbnb
[direct: mongos] airbnb> db.listing.getShardDistribution() 
[direct: mongos] airbnb> sh.status()


# stop
docker compose down

# clear all volumes
docker volume rm `docker volume ls | grep code | awk '{print $2}'`
docker volume prune # remove all unused volumes

#
deactivate
```

## Run batch
```
# terminal 1
python3 mysimbdp-batchingestmanager.py


# terminal 2
cp ../data/data.csv ./client-staging-input-directory/tenant1-data.csv

# terminal 3 to run performance test
bash performance_batch.sh
```

## Run stream
```
# terminal 1
python3 mysimbdp-streamingestmanager.py

# terminal 2
python3 mysimbdp-streamingestmonitor.py

# terminal 3 to run performance test
python3 performance_stream.py
```
```