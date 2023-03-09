from confluent_kafka import Producer
import pandas as pd
from threading import Thread


class Tenant1(Thread):
    def __init__(self, topic, file_path):
        Thread.__init__(self)
        self.topic = topic
        self.file_path = file_path

    def run(self):
        produce_event(self.topic, self.file_path, "tenant1")

class Tenant2(Thread):
    def __init__(self, topic, file_path):
        Thread.__init__(self)
        self.topic = topic
        self.file_path = file_path

    def run(self):
        produce_event(self.topic, self.file_path, "tenant2")
    
def produce_event(topic, file_path, producer_name):
    p = Producer({'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094'})
    print("Kafka {} Producer has been initiated...".format(producer_name))
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
        p.produce(topic, m, callback=cb)
        p.flush()

if __name__ == '__main__':
    topic = "tenant1_test"
    #file_path = "../data/data.csv"
    file_path = "../data/listings_summary.csv"
    t1 = Tenant1(topic, file_path)
    t1.start()
    topic = "tenant2_test"
    t2 = Tenant2(topic, file_path)
    t2.start()
    t1.join()
    t2.join()