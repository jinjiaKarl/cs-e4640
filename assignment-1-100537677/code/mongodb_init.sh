#!/etc/bin/env bash

# Initialize the replica sets
docker-compose exec configsvr01 sh -c "mongosh < /scripts/init-configserver.js"
docker-compose exec shard01-a sh -c "mongosh < /scripts/init-shard01.js"
docker-compose exec shard02-a sh -c "mongosh < /scripts/init-shard02.js"
docker-compose exec shard03-a sh -c "mongosh < /scripts/init-shard03.js"

sleep 10

# Initialize the mongos
docker-compose exec router01 sh -c "mongosh < /scripts/init-router.js"
