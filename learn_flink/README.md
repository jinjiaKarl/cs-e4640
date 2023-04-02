
# Concepts

# Deployment

## Standalone

* Flink Client
* JobManager
    * Application mode
    * Per-job mode
    * Session mode
* TaskManager


# Run
```
docker build -t jinjia/pyflink .
docker compose up 

curl http://localhost:8081


flink run  -py /opt/flink/examples/python/datastream/basic_operations.py # submit to flink cluster, why does not output stardard output?
python3 /opt/flink/examples/python/datastream/basic_operations.py # not submit to flink cluster, output stardard output

# output目录是存放在taskmanager下
flink run  -py /opt/flink/examples/python/datastream/word_count.py  --output /opt/flink/examples/python/datastream/output
``` 