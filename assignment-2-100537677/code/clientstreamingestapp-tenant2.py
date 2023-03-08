import sys, json, time, subprocess
args = json.loads(sys.argv[1])
topic = "teant2" + "_" + args['topic_name']
kafka_host = args['kafka_host']
predefined_time = args['pre_defined_time']

def consume():
    print("Starting to consume messages {} {} {}".format(topic, kafka_host, predefined_time))
    time.sleep(10)
    return

consume()