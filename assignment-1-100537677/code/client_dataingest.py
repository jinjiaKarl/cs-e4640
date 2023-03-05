import argparse
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
import logging
import pandas as pd

# python3 client_dataingest.py --topic listing --filepath ../data/data.csv
def set_logger():
    logging.basicConfig(
        format="%(asctime)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="../logs/producer.log",
        filemode="a",
    )
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    return logger


def set_args():
    parser = argparse.ArgumentParser(description="Data ingestion.")
    parser.add_argument("--topic", type=str, help="database name", required=True)
    parser.add_argument("--filepath", type=str, help="csv file path", required=True)
    args = parser.parse_args()
    return args


def create_topic(topic):
    a = AdminClient({"bootstrap.servers": "localhost:9092"})
    fs = a.create_topics([NewTopic(topic, num_partitions=1, replication_factor=1)])
    for topic, f in fs.items():
        try:
            f.result()
            print("Topic {} created".format(topic))
            logger.info("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))
            logger.error("Failed to create topic {}: {}".format(topic, e))


def produce_event(topic, filepath):
    p = Producer({"bootstrap.servers": "localhost:9092"})
    print("Kafka Producer has been initiated...")

    def cb(err, msg):
        if err is not None:
            logger.error("Error: %s" % err)
        else:
            message = "Produced message on topic {} with value of {}".format(
                msg.topic(), msg.value().decode("utf-8")
            )
            logger.info(message)

    data = pd.read_csv(filepath)
    # one by one
    for i in data.index:
        data_json = data.loc[i].to_json()
        m = data_json.encode("utf-8")
        print(m)
        p.produce(topic, m, callback=cb)
        p.flush()


if __name__ == "__main__":
    try:
        logger = set_logger()
        args = set_args()
        create_topic(args.topic)
        produce_event(args.topic, args.filepath)
    except Exception as e:
        print(e)
