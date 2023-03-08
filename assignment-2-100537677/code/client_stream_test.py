from confluent_kafka import Producer
import pandas as pd

def produce_event(topic, file_path):
    p = Producer({'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094'})
    print("Kafka Producer has been initiated...")
    def cb(err, msg):
        if err is not None:
            print("Error: %s" % err)
        else:
            message = "Produced message on topic {} with value of {}".format(
                msg.topic(), msg.value().decode("utf-8")
            )
            print(message)
    data = pd.read_csv(file_path)
    # one by one
    for i in data.index:
        data_json = data.loc[i].to_json()
        m = data_json.encode("utf-8")
        print(m)
        p.produce(topic, m, callback=cb)
        p.flush()

if __name__ == '__main__':
    topic = "tenant1_test"
    file_path = "../data/data.csv"
    produce_event(topic, file_path)