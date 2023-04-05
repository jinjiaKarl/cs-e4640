
# Concepts


Batch process(bounded data)



Streaming process(unbounded data) 
* Source operator
* Transformation operator, map(), keyBy(), filter()
* Sink operator


[Architecture](https://nightlies.apache.org/flink/flink-docs-master/zh/docs/concepts/flink-architecture/)
* Flink Client  `flink run`
* JobManager
* TaskManager


[API](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/concepts/overview/)
* [DataStream](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/datastream/overview/) API(bounded/unbounded streams)
* DataSet API(bounded streams)
* Table API: Declarative DSL, follows relational model
* SQL


Stateful stream processing
* 无状态的计算观察每个独立事件，并根据最后一个事件输出结果。有状态的计算则会基于多个事件输出结果。
    * 例如若在一分钟内收到两个相差20度以上的温度读数，则发出警告，这是有状态的计算。
* [delivery guarantee](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/connectors/datastream/guarantees/)
    * At least once: 最少一次，如果产生故障，可能有重复数据。
    * At most once: 最多一次，如果产生故障，可能丢失数据。
    * Exactly once: 精确一次，如果产生故障，数据会被正确的处理一次。
    * [end-to-end exactly-once](https://blog.csdn.net/m0_49834705/article/details/114598055): 从source到transformation到sink的整个数据流处理过程中，都能保证exactly-once的语义。
* [Checkpoint](https://zhuanlan.zhihu.com/p/263833210):


Timely stream processing
* time types
    * Event Time: time when event occurs
    * Ingestion Time: time when event is received by the system
    * Process Time: time when event is processed by a specific operator in the pipeline
* [Watermark](https://cloud.tencent.com/developer/article/1803318)：如果要使用Event Time，那么需要设置Watermark，Watermark是Flink插入到数据流中的一种特殊的数据结构，它包含一个时间戳，并假设后续不会有小于该时间戳的数据，如果后续数据存在小于该时间戳的数据则视为延迟数据，需另外处理。
* [Window](https://www.zhihu.com/tardis/zm/art/102325190)
    * Window Assigner: 指定窗口的分配策略，Flink提供了多种窗口分配器，如滚动窗口、滑动窗口、会话窗口等。
        * Batch/Tumbling Windows: 滚动窗口下窗口之间之间不重叠，且窗口长度是固定的。
        * Sliding Windows：滑动窗口以一个步长（Slide）不断向前滑动，窗口的长度固定。使用时，我们要设置Slide和Size；不同窗口之间会有重叠。
        * Count Windows: 分组依据是元素的数量
        * [Session Windows](https://www.jianshu.com/p/520c14d669d6)：是指一段持续活跃的期间，由活跃间隙分隔开，一个session没有固定的时长和步长，需要自己定义处理机制。
    * Window Function
        * 增量计算：窗口保存一份中间数据，每流入一个新元素，新元素与中间数据两两合一，生成新的中间数据，再保存到窗口中。
        * 全量计算：窗口先缓存该窗口所有元素，等到触发条件后对窗口内的全量元素执行计算。
    * Window Trigger: 决定了何时启动Window Function来处理窗口中的数据以及何时将窗口内的数据清理。
    * Window Evictor: actions after the trigger fires and before and/or after the windows function is called.
    * Keyed Window or Non-keyed Window: 
        * Keyed Window: 按照key分组，每个key都有自己的窗口，不同key之间的窗口是独立的。
        * Non-keyed Window: 没有key，所有的数据都在一个窗口中，所有的数据都是共享的。
        * 从计算上看，Keyed Window编程结构会将输入的stream转换成Keyed stream，逻辑上会对应多个Keyed stream，每个Keyed stream会独立进行计算，这就使得多个Task可以对Windowing操作进行并行处理，具有相同Key的数据元素会被发到同一个Task中进行处理。而对于Non-Keyed Window编程结构，Non-Keyed stream逻辑上将不能split成多个stream，所有的Windowing操作逻辑只能在一个Task中进行处理，也就是说计算并行度为1。

# Deployment

## Standalone

* Flink Client
* [JobManager](https://zhuanlan.zhihu.com/p/96105903)
    * Application mode: creates a session cluster per application and executes the application’s main() method on the cluster; Flink Job 集群可以看做是 Flink Application 集群”客户端运行“的替代方案。
    * Per-job mod(deprecated)e: once the job finishes, the JobManager shuts down; the resources are not shared across jobs. 
    * Session mode (default): the cluster lifecycle is independent of that of any job running on the cluster and the resources are shared across all jobs.
* TaskManager


# Run-
```
docker build -t jinjia/pyflink -f Dockerfile_simple .
docker compose -f docker-compose_simple.yaml up 

curl http://localhost:8081


flink run  -py /opt/flink/examples/python/datastream/basic_operations.py # submit to flink cluster, why does not output stardard output?
python3 /opt/flink/examples/python/datastream/basic_operations.py # not submit to flink cluster, output stardard output

# output目录是存放在taskmanager下
flink run  -py /opt/flink/examples/python/datastream/word_count.py  --output /opt/flink/examples/python/datastream/output
``` 


# Run
https://github.com/apache/flink-playgrounds/tree/master/pyflink-walkthrough
```
docker build --tag pyflink/pyflink:1.16.0-scala_2.12 . 

docker compose up

flink run -py /opt/pyflink-walkthrough/payment_msg_proccessing.py
```