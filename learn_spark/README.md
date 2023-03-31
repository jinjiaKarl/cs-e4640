# Spark Concepts

* SparkSession: Act as a program driver to manage the execution of tasks
    * SparkContext: Main entry point for Spark functionality. A SparkContext represents the connection to a Spark cluster, and can be used to create RDD and broadcast variables on that cluster.
* RDD：是弹性分布式数据集（Resilient Distributed Dataset）的简称，是分布式内存的一个抽象概念，提供了一种高度受限的共享内存模型。
* DAG：是Directed Acyclic Graph（有向无环图）的简称，反映RDD之间的依赖关系。
* Driver Program：控制程序，负责为Application构建DAG图。
* Cluster Manager：集群资源管理中心，负责分配计算资源。例如：YARN、Mesos、Standalone。
* Worker Node：工作节点，负责完成具体计算。
* Executor：是运行在工作节点（Worker Node）上的一个进程，负责运行Task，并为应用程序存储数据。每一个APP都会有一个专属的Executor进程，以多线程的方式运行多个Task。
* Application: 用户编写的Spark应用程序，一个Application包含多个Job。
* Job：一个Job包含多个RDD及作用于相应RDD上的各种操作。
* Stage：是Job的基本调度单位，一个job会分为多组task，每组task被称为“stage”。
* Task：运行在Executor上的工作单元，是Executor中的一个线程。One task works on a partition at a time.
* 总结：Application由多个Job组成，Job由多个Stage组成，Stage由多个Task组成。Stage是作业调度的基本单位。
* Partition: Input data is distributed in different nodes for processing
    * Support partitions for data processing: a node keeps one or n partitions, a partition resides only in a node => for computing
* Transformations: Instructions about how to transform a data in a form to another form, and it will not change the original data(immutability)
* Action: Compute the results for a set of transformations, such as, count or average



[RDD](https://www.zhihu.com/question/59810584), DATAFRAME, DATASET的区别
> https://www.zhihu.com/question/48684460
* RDD API:
* DataFrame API: distributed data organized into named columns
* Dataset API: 


Spark ecosystem 
> https://blog.51cto.com/u_15294985/5437527
* Spark Core: 实现了 Spark 的基本功能，包含 RDD、任务调度、内存管理、错误恢复、与存储系统交互等模块。
* Spark SQL: Spark 用来操作结构化数据的程序包。通过 Spark SQL，我们可以使用 SQL 操作数据。
    * DataFrame: 是 Spark SQL 中最基本的数据抽象，是一个分布式的数据集合，是一个二维表格。
    * Dataset: 是对 DataFrame 的进一步封装，包含了其他的信息，例如数据类型。
    * [Structured Streaming](https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html): 用于对流式实时数据的处理。可以将结果输出到外部存储系统，例如 Kafka 等。
    * Spark MLlib: 提供常见的机器学习(ML)功能的程序库。包括分类、回归、聚类、协同过滤等，还提供了模型评估、数据导入等额外的支持功能。
* Spark Streaming: Spark 提供的对流式准实时数据(near-realtime)进行流式计算的组件。基本原理是把输入数据以某一时间间隔批量的处理，当批处理间隔缩短到秒级时，便可以用于处理实时数据流。
    * DStream: 代表持续性的数据流和经过各种 Spark 算子操作后的结果数据流。

* Spark GraphX: Spark 提供的图计算组件。GraphX 是 Spark 的一个图计算库，它提供了图的并行计算和图的并行操作。



# Spark Cluster with Docker & docker-compose(2021 ver.)

https://github.com/mvillarrealb/docker-spark-cluster

# General

A simple spark standalone cluster for your testing environment purposses. A *docker-compose up* away from you solution for your spark development environment.

The Docker compose will create the following containers:

container|Exposed ports
---|---
spark-master|9090 7077
spark-master|4040 4040
spark-worker-1|9091
spark-worker-2|9092
demo-database|5432


The following UIs are available:
> https://stackoverflow.com/questions/56397738/
* Spark UI: Every SparkContext launches a Web UI, by default on port 4040, that displays useful information about the application. 
* Master UI
* Worker UI
# Installation

The following steps will make you run your spark cluster's containers.

## Pre requisites

* Docker installed

* Docker compose  installed

## Build the image


```sh
docker build -t cluster-apache-spark:3.0.2 .
```

## Run the docker-compose

The final step to create your test cluster will be to run the compose file:

```sh
docker-compose up -d
```

## Validate your cluster

Just validate your cluster accesing the spark UI on each worker & master URL.

### Spark Master

http://localhost:9090/

![alt text](docs/spark-master.png "Spark master UI")

### Spark Worker 1

http://localhost:9091/

![alt text](docs/spark-worker-1.png "Spark worker 1 UI")

### Spark Worker 2

http://localhost:9092/

![alt text](docs/spark-worker-2.png "Spark worker 2 UI")


# Resource Allocation 

This cluster is shipped with three workers and one spark master, each of these has a particular set of resource allocation(basically RAM & cpu cores allocation).

* The default CPU cores allocation for each spark worker is 1 core.

* The default RAM for each spark-worker is 1024 MB.

* The default RAM allocation for spark executors is 256mb.

* The default RAM allocation for spark driver is 128mb

* If you wish to modify this allocations just edit the env/spark-worker.sh file.

# Binded Volumes

To make app running easier I've shipped two volume mounts described in the following chart:

Host Mount|Container Mount|Purposse
---|---|---
apps|/opt/spark-apps|Used to make available your app's jars on all workers & master
data|/opt/spark-data| Used to make available your app's data on all workers & master

This is basically a dummy DFS created from docker Volumes...(maybe not...)

# Run Sample applications


## NY Bus Stops Data [Pyspark]

This programs just loads archived data from [MTA Bus Time](http://web.mta.info/developers/MTA-Bus-Time-historical-data.html) and apply basic filters using spark sql, the result are persisted into a postgresql table.

The loaded table will contain the following structure:

latitude|longitude|time_received|vehicle_id|distance_along_trip|inferred_direction_id|inferred_phase|inferred_route_id|inferred_trip_id|next_scheduled_stop_distance|next_scheduled_stop_id|report_hour|report_date
---|---|---|---|---|---|---|---|---|---|---|---|---
40.668602|-73.986697|2014-08-01 04:00:01|469|4135.34710710144|1|IN_PROGRESS|MTA NYCT_B63|MTA NYCT_JG_C4-Weekday-141500_B63_123|2.63183804205619|MTA_305423|2014-08-01 04:00:00|2014-08-01

To submit the app connect to one of the workers or the master and execute:

```sh
/opt/spark/bin/spark-submit --master spark://spark-master:7077 \
--jars /opt/spark-apps/postgresql-42.2.22.jar \
--driver-memory 1G \
--executor-memory 1G \
/opt/spark-apps/main.py
```

![alt text](./articles/images/pyspark-demo.png "Spark UI with pyspark program running")

## MTA Bus Analytics[Scala]

This program takes the archived data from [MTA Bus Time](http://web.mta.info/developers/MTA-Bus-Time-historical-data.html) and make some aggregations on it, the calculated results are persisted on postgresql tables.

Each persisted table correspond to a particullar aggregation:

Table|Aggregation
---|---
day_summary|A summary of vehicles reporting, stops visited, average speed and distance traveled(all vehicles)
speed_excesses|Speed excesses calculated in a 5 minute window
average_speed|Average speed by vehicle
distance_traveled|Total Distance traveled by vehicle


To submit the app connect to one of the workers or the master and execute:

```sh
/opt/spark/bin/spark-submit --deploy-mode cluster \
--master spark://spark-master:7077 \
--total-executor-cores 1 \
--class mta.processing.MTAStatisticsApp \
--driver-memory 1G \
--executor-memory 1G \
--jars /opt/spark-apps/postgresql-42.2.22.jar \
--conf spark.driver.extraJavaOptions='-Dconfig-path=/opt/spark-apps/mta.conf' \
--conf spark.executor.extraJavaOptions='-Dconfig-path=/opt/spark-apps/mta.conf' \
/opt/spark-apps/mta-processing.jar
```

You will notice on the spark-ui a driver program and executor program running(In scala we can use deploy-mode cluster)

![alt text](./articles/images/stats-app.png "Spark UI with scala program running")


# Summary

* We compiled the necessary docker image to run spark master and worker containers.

* We created a spark standalone cluster using 2 worker nodes and 1 master node using docker && docker-compose.

* Copied the resources necessary to run demo applications.

* We ran a distributed application at home(just need enough cpu cores and RAM to do so).

# Why a standalone cluster?

* This is intended to be used for test purposes, basically a way of running distributed spark apps on your laptop or desktop.

* This will be useful to use CI/CD pipelines for your spark apps(A really difficult and hot topic)

# Steps to connect and use a pyspark shell interactively

* Follow the steps to run the docker-compose file. You can scale this down if needed to 1 worker. 

```sh
docker-compose up --scale spark-worker=1
docker exec -it docker-spark-cluster_spark-worker_1 bash
apt update
apt install python3-pip
pip3 install pyspark
pyspark
```

# What's left to do?

* Right now to run applications in deploy-mode cluster is necessary to specify arbitrary driver port.

* The spark submit entry in the start-spark.sh is unimplemented, the submit used in the demos can be triggered from any worker
