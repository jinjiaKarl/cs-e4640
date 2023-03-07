# This is a deployment/installation guide

The deployment docker-compose.yml file is reused from the previous assignment. I have added opentelemetry-collector and prometheus to the docker-compose file.

## Deployment
```
# 
pip3 install opentelemetry-exporter-otlp
pip3 install opentelemetry-sdk

cd code
pip3 install -r requirements.txt

# start kafka and sharded mongo cluster
docker compose up

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
```

## Run batch
```

```

## Run stream
```
```