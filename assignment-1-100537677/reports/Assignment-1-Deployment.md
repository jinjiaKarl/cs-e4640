# This is a deployment/installation guide

## Deployment

```bash
cd code
pip3 install -r requirements.txt

# start kafka and sharded mongo cluster
docker compose up

# initialize the cluster
bash mongo_init.sh

# check sharding
docker-compose exec router01 mongosh --port 27017
[direct: mongos] airbnb> db.listing.getShardDistribution() 
[direct: mongos] airbnb> sh.status()


# stop
docker compose down

# clear all volumes
docker volume rm `docker volume ls | grep code | awk '{print $2}'`
docker volume prune # remove all unused volumes
```

## Run

```bash
# install dependencies
pip3 install -r requirements.txt
```

### data preprocessing

```bash
# add new field "city" to the data
bash preprocess.sh "../data/listings_summary.csv" "Los Angeles"
```

### data ingestion

I provide two methods of data ingestion.

- The first one is to read the external `csv` file and insert the data to the database.
```bash
python3 mysimbdp-dataingest.py --database airbnb --collection listing --filepath ../data/data.csv
```
- The second one is to receive the data from specific topic in kafka and insert the data to the database.
```bash
# comsume data from kafka and insert to mongodb
python3 mysimbdp-dataingest.py --database airbnb --collection listing --stream True --topic listing
# produce data to kafka
python3 client_dataingest.py --topic listing --filepath ../data/data.csv
```

### daas

I provide a simple web interface for data ingestion and query. It is a flask app. The following API endpoints are provided:

- `/ingestion`: insert multiple records to the database
```bash
# start daas
python3 mysimbdp-daas.py --database airbnb --collection listing

# client
python3 client_daas.py --ingest_file_path ../data/data.csv
```

- `/query?name=xxx`: query records by a given condition using the `name` argument
```
curl --location --request GET 'http://127.0.0.1:8000/query?name=Zen'

{
"_id": {
"$oid": "63eb82d00c9fb2edadff9628"
},
"city": "Los Angeles",
"id": 2732,
"name": "Zen Life at the Beach",
"host_id": 3041,
"host_name": "Yoga Priestess",
"neighbourhood_group": "Other Cities",
"neighbourhood": "Santa Monica",
"latitude": 34.0044,
"longitude": -118.48095,
"room_type": "Private room",
"price": 179,
"minimum_nights": 7,
"number_of_reviews": 24,
"last_review": "2022-08-21",
"reviews_per_month": 0.17,
"calculated_host_listings_count": 2,
"availability_365": 365,
"number_of_reviews_ltm": 3,
"license": null
}
```
- `/query/<id>`: query a record by id
```
curl --location --request GET 'http://127.0.0.1:8000/query/2732'

{
"_id": {
"$oid": "63eb82d00c9fb2edadff9628"
},
"city": "Los Angeles",
"id": 2732,
"name": "Zen Life at the Beach",
"host_id": 3041,
"host_name": "Yoga Priestess",
"neighbourhood_group": "Other Cities",
"neighbourhood": "Santa Monica",
"latitude": 34.0044,
"longitude": -118.48095,
"room_type": "Private room",
"price": 179,
"minimum_nights": 7,
"number_of_reviews": 24,
"last_review": "2022-08-21",
"reviews_per_month": 0.17,
"calculated_host_listings_count": 2,
"availability_365": 365,
"number_of_reviews_ltm": 3,
"license": null
}
```
- `/insert`: insert a record to the database
```
curl --location --request POST 'http://127.0.0.1:8000/insert' \
--header 'Content-Type: application/json' \
--data-raw '{
"city": "Los Angeles",
"id": 2732,
"name": "Zen Life at the Beach",
"host_id": 3041,
"host_name": "Yoga Priestess",
"neighbourhood_group": "Other Cities",
"neighbourhood": "Santa Monica",
"latitude": 34.0044,
"longitude": -118.48095,
"room_type": "Private room",
"price": 179,
"minimum_nights": 7,
"number_of_reviews": 24,
"last_review": "2022-08-21",
"reviews_per_month": 0.17,
"calculated_host_listings_count": 2,
"availability_365": 365,
"number_of_reviews_ltm": 3,
"license": null
}'

{
    "inserted_id": "63eb8ed65b7af67f46aeec32"
}
```


```bash
# start daas
python3 mysimbdp-daas.py --database airbnb --collection listing

# client
python3 client_daas.py --ingest_file_path ../data/data.csv
```

### performance test
## using bash script
```
bash performance_test.sh
```

## using official tools

* [mongodb free monitoring tool](https://www.mongodb.com/docs/manual/administration/free-monitoring/): we will be provided a unique URL where we can access your monitored data.
* mongotop: `mongotop --uri="mongodb://localhost:27122"`
* mongostat: `mongostat --uri="mongodb://localhost:27122"`
