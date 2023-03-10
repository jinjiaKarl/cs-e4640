import argparse, json, signal
from confluent_kafka import Consumer, Producer,TopicPartition
import logging
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader


kafka_host = "localhost:9092,localhost:9093,localhost:9094"
running = True


def set_logger():
    logging.basicConfig(
        format="%(asctime)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="../logs/streamingmonitor.log",
        filemode="a",
    )
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    return logger



def set_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mq', type=str, help='mq name', default='kafka')
    parser.add_argument('--tenant_name', type=str, help='tenant name, separate by comma', default='tenant1,tenant2')
    parser.add_argument('--topic_name', type=str, help='topic name', default='test')
    parser.add_argument('--threshold', type=int, help='threshold for average ingestion time', default=1)
    args = parser.parse_args()
    return args

def consume():
    def commit_completed(err, partitions):
        if err:
            print(str(err))
        else:
            print("Committed partition offsets: " + str(partitions))
    consumer_group = "streamingestmonitor"
    c = Consumer({
            'bootstrap.servers': kafka_host,
            'group.id': consumer_group,
            'auto.offset.reset': 'earliest',
            'on_commit': commit_completed,
            'enable.auto.commit': True # default is True
        })

    p = Producer({'bootstrap.servers': kafka_host})
    sub_topics = []
    for name in args.tenant_name.split(","):
        topic_name = name + "_" + args.topic_name + "_report"
        sub_topics.append(topic_name)
        # get the highest offset
        low, high = c.get_watermark_offsets(TopicPartition(topic_name, partition=0))
        print("topic: {}, partition: {}, low: {}, high: {}".format(topic_name, 0, low, high))
    
    try:
        c.subscribe(sub_topics)
        print("Kafka {} Consumer has been initiated...".format(consumer_group))
        json_data = {}
        def cb(options):
            if json_data != {}:
                tenant_name = json_data["tenant_name"]
                stream_qps = json_data["qps"]
                yield metrics.Observation(stream_qps, {"tenant": tenant_name})
        meter.create_observable_gauge("stream_qps", callbacks=[cb], description="stream_qps")

        while running:
            msg = c.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                print("Consumer {} error: {}".format(consumer_group, msg.error()))
                raise Exception("Consumer {} error: {}".format(consumer_group, msg.error()))
            data = msg.value().decode("utf-8")
            print("Consumer {} consume data: {} from topic {}".format(consumer_group, data, msg.topic()))
            json_data = json.loads(data)
            logger.info("Consumer {} consume data: {} from topic {}".format(consumer_group, data, msg.topic()))
            if json_data != {} and json_data["avg_ingestion_time"] < args.threshold:
                json_data["alert_type"] = "delete_consumer"
                json_data["alert_msg"] = "Average ingestion time is less than threshold, delete a {} consumer".format(json_data["tenant_name"])
                produce_alert(p, json_data)
            elif json_data != {} and json_data["avg_ingestion_time"] >= args.threshold:
                json_data["alert_type"] = "add_consumer"
                json_data["alert_msg"] = "Average ingestion time is greater than threshold, add a {} consumer".format(json_data["tenant_name"])
                produce_alert(p, json_data)
    finally:
        c.close()

def shutdown():
    global running
    running = False

def produce_alert(p, data):
    def cb(err, msg):
        if err is not None:
            print("Error: %s" % err)
        else:
            message = "Produced message on topic {} with value of {}".format(
                msg.topic(), msg.value().decode("utf-8")
            )
            print(message)
    for name in args.tenant_name.split(","):
        topic_name = name + "_" + args.topic_name + "_alert"
        p.produce(topic_name, json.dumps(data), callback=cb)
        p.flush()


def exit_handler(signum, frame):
    print("Exit")
    exit()

def set_opentelemetry():
    exporter = OTLPMetricExporter(insecure=True)
    # MetricReader: collect metrics and export to OTLP, default interval is 60000 milliseconds
    # https://opentelemetry.io/docs/reference/specification/metrics/sdk/#periodic-exporting-metricreader
    reader = PeriodicExportingMetricReader(exporter)
    # MteterProvider: It provides access to Meters.
    provider = MeterProvider(
        metric_readers=[reader],
    )
    # set global MeterProvider
    metrics.set_meter_provider(provider)
    # Meter: responsible for creating Instruments
    meter = metrics.get_meter_provider().get_meter("batch", "0.1.0")
    return meter

if __name__ == "__main__":
    logger = set_logger()
    args = set_args()
    meter = set_opentelemetry()
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    consume()
