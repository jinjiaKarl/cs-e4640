import sys, json, time, datetime
from confluent_kafka import Consumer, Producer
import pymongo
from threading import Thread, Lock

tenant_name = "tenant2"
args = json.loads(sys.argv[1])
topic = tenant_name + "_" + args['topic_name']
report_topic = "tenant2" + "_" + args['topic_name'] + "_report"
kafka_host = args['kafka_host']
predefined_time = args['pre_defined_time']

metrics = {}
update = False
metrics_lock = Lock()

def connect_to_mongo(uri, database, collection):
    client = pymongo.MongoClient(uri)
    db = client[database]
    table = db[collection]
    return table

def start():
    db = connect_to_mongo("mongodb://localhost:27117", "airbnb", "listing_tenant2")
    consumer_group = "clientstreamingestapp-tenant2"
    c = Consumer({
        'bootstrap.servers': kafka_host,
        'group.id': consumer_group,
        'auto.offset.reset': 'earliest'
    })
    c.subscribe([topic])
    print("Kafka Consumer {} has been initiated...".format(consumer_group))
    msg_count = 0
    time_consumed = 0
    total_msg_size = 0
    while True:
        msg = c.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer {} error: {}".format(consumer_group, msg.error()))
            continue

        data = msg.value().decode("utf-8")
        print("Consumer {} consume data: {} from topic {}".format(consumer_group, data, msg.topic()))
        msg_count += 1
        start = time.time()
        data = json.loads(data)
        data["tenant_name"] = tenant_name
        # write to mongodb
        db.insert_one(data)
        end = time.time()
        time_consumed += end - start
        # produce report
        msg_size = sys.getsizeof(data) # in bytes
        total_msg_size += msg_size
        metrics_lock.acquire()
        try:
            global metrics, update
            metrics = {
                "total_messages": msg_count,
                "ingestion_time": end - start, # float in seconds
                "avg_ingestion_time": time_consumed / msg_count,
                "ingestion_type": "streaming",
                "ingestion_rate": msg_size /  (end - start),
                "data_size": msg_size, # in bytes
                "total_data_size": total_msg_size,
                "qps": total_msg_size / time_consumed,
                "tenant_name": tenant_name,
                "timestamp": str(datetime.datetime.now()),
                "predefined_time": predefined_time
            }
            print("Tenant {} Producing metrics: {}".format(tenant_name,metrics))
            update = True
        finally:
            metrics_lock.release()

# report in a separate thread
class ProduceMetric(Thread):
    def __init__(self, p):
        super().__init__()
        self.p = p
    def run(self):
        def cb(err, msg):
            if err is not None:
                print("Error: %s" % err)
            else:
                message = "Produced message on topic {} with value of {}".format(
                    msg.topic(), msg.value().decode("utf-8")
                )
                print(message)
        while True:
            time.sleep(predefined_time)
            metrics_lock.acquire()
            try:
                global metrics, update
                if metrics != {} and update:
                    self.p.produce(report_topic,  json.dumps(metrics).encode("utf-8"), callback=cb)
                    update = False
            finally:
                metrics_lock.release()
            self.p.flush()

p = ProduceMetric(Producer({'bootstrap.servers': kafka_host}))
p.start()
start()
