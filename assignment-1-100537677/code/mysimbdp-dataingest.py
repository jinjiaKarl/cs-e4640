import pandas as pd
import json
import argparse
import pymongo
from confluent_kafka import Consumer
import logging
from confluent_kafka.admin import AdminClient, NewTopic

# python3 mysimbdp-dataingest.py --database airbnb --collection listing --filepath ../data/data.csv
# python3 mysimbdp-dataingest.py --database airbnb --collection listing --stream True --topic listing
def set_logger():
    logging.basicConfig(
        format="%(asctime)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="../logs/consumer.log",
        filemode="a",
    )
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    return logger


def connect_to_mongo(uri, database, collection):
    client = pymongo.MongoClient(uri)
    db = client[database]
    table = db[collection]
    return table


def set_args():
    parser = argparse.ArgumentParser(description="Data ingestion.")
    parser.add_argument(
        "--database_uri",
        type=str,
        help="database uri",
        default="localhost:27117",
    )
    parser.add_argument("--database", type=str, help="database name", required=True)
    parser.add_argument("--collection", type=str, help="collection name", required=True)
    parser.add_argument("--filepath", type=str, help="csv file path")
    parser.add_argument("--stream", type=bool, help="stream data")
    parser.add_argument("--topic", type=str, help="kafka topic")
    args = parser.parse_args()
    return args


class FileIngest:
    def __init__(self, db):
        self.db = db
        pass

    def read_csv_to_json(self, file_path):
        try:
            data = pd.read_csv(file_path)
            #d = data.to_json(orient="records")
            #print(type(d))  # str
            data_json = json.loads(data.to_json(orient="records"))
            # print(type(data_json)) // list
            # batch
            result = self.db.insert_many(data_json)
            print("ingested {} documents".format(len(result.inserted_ids)))
        except Exception as e:
            print(e)


class StreamIngest:
    def __init__(self):
        # earliest: pull all messages from the offset set by last commit
        self.consumer = Consumer(
            {
                "bootstrap.servers": "localhost:9092",
                "group.id": "python-consumer",
                "auto.offset.reset": "earliest",
            }
        )
        print("Kafka Consumer has been initiated...")

    def create_topic(self, topic):
        a = AdminClient({"bootstrap.servers": "localhost:9092"})
        fs = a.create_topics([NewTopic(topic, num_partitions=3, replication_factor=2)])
        for topic, f in fs.items():
            try:    
                f.result()
                print("Topic {} created".format(topic))
                logger.info("Topic {} created".format(topic))
            except Exception as e:
                print("Failed to create topic {}: {}".format(topic, e))
                logger.error("Failed to create topic {}: {}".format(topic, e))


    def consume(self, topic):
        print("Available topics to consume: ", self.consumer.list_topics().topics)
        self.consumer.subscribe([topic])
        while True:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue
            data = msg.value().decode("utf-8")
            #print(data)
            logger.info("consume data: %s from topic %s", data, topic)
            # write to mongodb
            db.insert_one(json.loads(data))


if __name__ == "__main__":
    try:
        args = set_args()
        db = connect_to_mongo(args.database_uri, args.database, args.collection)
        if args.stream:
            logger = set_logger()
            stream_processor = StreamIngest()
            stream_processor.create_topic(args.topic)
            stream_processor.consume(args.topic)
        else:
            file_processor = FileIngest(db)
            file_processor.read_csv_to_json(args.filepath)
    except Exception as e:
        print(e)
