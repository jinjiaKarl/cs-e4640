# Concepts

Components
* API: Defines data types and operations for generating and correlating tracing, metrics, and logging data.
* SDK: Provides a language-specific implementation of the API. 
* Instrumenting: code from the system’s components must emit traces, metrics, and logs.
    * automatic instrumentation: Without being required to modify the source code you can collect telemetry from an application 
    * manual instrumentation: 
        * develop a library
        * develop a service: configure the OpenTelemetry SDK, create Telemetry Data and export data by two ways: 
            * directly to a backend
            * via a collector
    * synchronous instruments: are used inline with application/business processing logic, like when handling a request or calling another service. 
    * asynchronous instruments: register callback functions, which are invoked on demand to make measurements. This is useful to periodically measure a value that cannot be instrumented directly. Callback functions will be called only when the Meter is being observed. 
* collector: It supports receiving telemetry data in multiple formats (e.g., OTLP, Jaeger, Prometheus, as well as many commercial/proprietary tools) and sending data to one or more backends. 
    * two versions of Collector: 
        * `Collector core` packages provide the basic functionality to receive, process, and export telemetry data.
        * `Collector contrib` packages bring support for more data formats and vendor backends. Offers support for popular open source projects including Jaeger, Prometheus.
    * components: 
        * receivers: receive data from different sources, such as OTLP, Jaeger, Zipkin, Prometheus, etc.
        * processors: process data, such as filtering, batching, etc.
        * exporters: send data to different backends, such as Jaeger, Zipkin, OTLP, Prometheus, etc.
* exporter: 将数据直接发送到不同的后端，有不同的exporter，例如ConsoleExporter, JaegerExporter, ZipkinExporter, OTLPExporter, PrometheusExporter, etc.

将数据发送到后端有两种方式：
* 通过exporter直接发送
* 先发送到collector，再由collector发送到后端




# Run

## automatic instrumentation
https://opentelemetry.io/docs/instrumentation/python/automatic/

`pip install opentelemetry-distro ` installs the API, SDK, and the opentelemetry-bootstrap and opentelemetry-instrument tools.

Automatic instrumentation with Python uses a `Python agent` that can be attached to any Python application. It dynamically injects bytecode to capture telemetry from many popular libraries and frameworks.

``` 
pip3 install -r requirements.txt
python3 -m venv .
source ./bin/activate


# installs the corresponding instrumentation libraries
opentelemetry-bootstrap -a install 

opentelemetry-instrument \
    --traces_exporter console \
    --metrics_exporter console \
    flask run

# link up manual instrumentation with automatic instrumentation.

# By default, opentelemetry-instrument exports traces and metrics over OTLP/gRPC 
# and will send them to localhost:4317, which is what the collector is listening on.
pip install opentelemetry-exporter-otlp
opentelemetry-instrument flask run

```
