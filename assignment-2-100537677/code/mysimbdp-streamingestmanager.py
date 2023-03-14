import argparse, json
from confluent_kafka import Consumer
from confluent_kafka.admin import AdminClient, NewTopic
from threading import Thread
import subprocess
import signal

kafka_host = "localhost:9092,localhost:9093,localhost:9094"

def set_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mq', type=str, help='mq name', default='kafka')
    parser.add_argument('--tenant_name', type=str, help='tenant name, separate by comma', default='tenant1,tenant2')
    parser.add_argument('--topic_name', type=str, help='topic name', default='test')
    parser.add_argument('--pre_defined_time', type=int, help='pre defined time',default=10)
  #  parser.add_argument('--threshold', type=int, help='threshold for average ingestion time', default=10)
    args = parser.parse_args()
    return args


class ConsumerAlert(Thread):
    def __init__(self,tenant_name, topic_name, pre_defined_time, apps):
        super().__init__()
        self.attributes = {
            "tenant_name": tenant_name,
            "topic_name": topic_name,
            "pre_defined_time": pre_defined_time,
            "apps": apps
        }
    def run(self):
        # earliest: pull all messages from the offset set by last commit
        consuemer_group = "streamingestmanager"
        c = Consumer({
                'bootstrap.servers': kafka_host,
                'group.id': consuemer_group,
                'auto.offset.reset': 'earliest'
            })
        sub_topics = []
        for name in self.attributes["tenant_name"].split(","):
            topic_name = name + "_" + self.attributes["topic_name"] + "_alert"
            sub_topics.append(topic_name)
        c.subscribe(sub_topics)
        print("Kafka {} Consumer has been initiated...".format(consuemer_group))
        while True:
            msg = c.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                print("Consumer {} error: {}".format(consuemer_group, msg.error()))
                continue
            data = msg.value().decode("utf-8")
            print("Consumer {} consume data: {} from topic {}".format(consuemer_group,data, msg.topic()))
            data = json.loads(data)
            if data["alert_type"] == "delete_consumer":
                if len(self.attributes["apps"][data["tenant_name"]]["app"]) > 1:
                    self.attributes["apps"][data["tenant_name"]]["app"].pop().kill()
            elif data["alert_type"] == "add_consumer":
                args = {"topic_name": self.attributes["topic_name"], "kafka_host": kafka_host, "pre_defined_time": self.attributes["pre_defined_time"]}
                # start a subprocess to run clientstreamingestapp
                app = subprocess.Popen(["python3", "clientstreamingestapp-" + data["tenant_name"] + ".py", json.dumps(args)])
                self.attributes["apps"][data["tenant_name"]]["app"].append(app)

class StreamIngest:
    def __init__(self, tenant_name, topic_name,pre_defined_time) -> None:
        self.attributes = {
            "tenant_name": tenant_name,
            "topic_name": topic_name,
            "pre_defined_time": pre_defined_time,
            "apps": {}
        }

    def initial_kafka(self):
        # create topics for each tenant
        a = AdminClient({"bootstrap.servers": kafka_host})
        new_topics = []
        for name in self.attributes["tenant_name"].split(","):
            topic_name = name + "_" + self.attributes["topic_name"]
            topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
            new_topics.append(topic)
            topic_name = name + "_" + self.attributes["topic_name"] + "_report"
            topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
            new_topics.append(topic)
            topic_name = name + "_" + self.attributes["topic_name"] + "_alert"
            topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
            new_topics.append(topic)
            self.attributes["apps"][name] = {"app": []}

        fs = a.create_topics(new_topics)
        for topic, f in fs.items():
            try:
                f.result()
                print("Topic {} created".format(topic))
            except Exception as e:
                print("Failed to create topic {}: {}".format(topic, e))

    def start_streaming_app(self):
        for name in self.attributes["tenant_name"].split(","):
            args = {"topic_name": self.attributes["topic_name"], "kafka_host": kafka_host, "pre_defined_time": self.attributes["pre_defined_time"]}
            # start a subprocess to run clientstreamingestapp
            app = subprocess.Popen(["python3", "clientstreamingestapp-" + name + ".py", json.dumps(args)])
            self.attributes["apps"][name]["app"].append(app)
        print("{} apps have been started".format(self.attributes["apps"]))
        for name in self.attributes["tenant_name"].split(","):
            for app in self.attributes["apps"][name]["app"]:
                app.wait()

    def get_apps(self):
        return self.attributes["apps"]
            
def exit_handler(signum, frame):
    print("Exit")
    for name in args.tenant_name.split(","):
        for app in apps[name]["app"]:
            app.kill()
   
    exit()
    
if __name__ == "__main__":
    args = set_args()
    if args.mq != 'kafka':
        print("Only support Kafka for now")
        exit()
    
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    si = StreamIngest(args.tenant_name, args.topic_name, args.pre_defined_time)
    apps = si.get_apps()

    ca = ConsumerAlert(args.tenant_name, args.topic_name, args.pre_defined_time, apps)
    ca.start()

    si.initial_kafka()
    si.start_streaming_app()

    