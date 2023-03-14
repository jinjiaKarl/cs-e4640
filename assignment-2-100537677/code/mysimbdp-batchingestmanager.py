import time, json, os, importlib, logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import View


def set_logger():
    logging.basicConfig(
        format="%(asctime)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="../logs/batchmanager.log",
        filemode="a",
    )
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    return logger


# reference: https://philipkiely.com/code/python_watchdog.html
class Watcher:

    def __init__(self, directory=".", handler=FileSystemEventHandler()):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory

    def run(self):
        self.observer.schedule(
            self.handler, self.directory, recursive=True)
        self.observer.start()
        print("\nWatcher Running in {}/\n".format(self.directory))
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()
        print("\nWatcher Terminated\n")


class MyHandler(FileSystemEventHandler):
    def __init__(self):
        # to be more realistic, we should store this in a database
        self.tenants = {}
        # create counter Instrument to report measurements
        self.successful_rows_counter = meter.create_counter("successful_rows")
        self.failed_rows_counter = meter.create_counter("failed_rows")
        self.data_size_counter = meter.create_counter("data_size")
        self.ingestion_time_counter = meter.create_counter("ingestion_time")
        def cb(options):
            # tranverse self.tenants
            for tenant_name, tenant in self.tenants.items():
                print("collecting metrics for tenant: {}, {}".format(tenant_name, tenant))
                yield metrics.Observation(tenant["qps"], {"tenant": tenant_name})
        meter.create_observable_gauge("batch_qps", callbacks=[cb], description="batch_qps")

    def parse_src_path(self, event):
        src_path = event.src_path
        filename = src_path.split("/")[-1]
        extension = filename.split(".")[-1]
        tenant_name = filename.split("-")[0]
        return src_path, filename, extension, tenant_name
    
    def check_constraints(self, event):
        src_path, filename, extension, tenant_name = self.parse_src_path(event)
        constraints = {}
        with open("constraints_{}.json".format(tenant_name), 'r') as file:
            constraints = json.load(file)
        print("Constraints: {}".format(constraints))
        if(self.tenants.get(tenant_name) == None):
            self.tenants[tenant_name] = {}
        if (self.tenants[tenant_name].get("file_count") == None):
            self.tenants[tenant_name]["file_count"] = 1
        else:
            self.tenants[tenant_name]["file_count"] += 1
        
        # check
        if extension  not in constraints.get("file_types").split(","):
            print("{} file {} type not allowed!".format(tenant_name, filename))
            return False
        if (constraints.get("number_of_files_limit") != None and self.tenants[tenant_name]["file_count"] > constraints.get("number_of_files_limit")):
            print("{} file {} count {} exceeded!".format(tenant_name, filename, self.tenants[tenant_name]["file_count"]))
            return False
        print("{} file size: {}".format(src_path, os.path.getsize(src_path)))
        if (constraints.get("file_size_limit") != None and os.path.getsize(src_path) > constraints.get("file_size_limit")):
            print("{} file {} size exceeded!".format(tenant_name, filename))
            return False
        return True
    
    def call_client_batchingestapp(self, event):
        src_path, _, extension, tenant_name = self.parse_src_path(event)
        app = importlib.import_module("clientbatchingestapp-{}".format(tenant_name) )
        is_success, metrics = app.ingestion(src_path, extension, tenant_name)
        print("Ingestion result: {} metrics: {} ".format(is_success, metrics))
        logger.info("Ingestion result: {} metrics: {}".format(is_success, metrics))
        self.successful_rows_counter.add(metrics.get("successful_rows", 0), {"tenant": tenant_name})
        self.failed_rows_counter.add(metrics.get("failed_rows", 0), {"tenant": tenant_name})
        self.data_size_counter.add(metrics.get("data_size", 0), {"tenant": tenant_name})
        self.ingestion_time_counter.add(metrics.get("ingestion_time", 0), {"tenant": tenant_name})
        if (self.tenants.get(tenant_name) != None and is_success):
            self.tenants[tenant_name]["data_size"] = self.tenants[tenant_name].get("data_size", 0) + metrics.get("data_size", 0)
            self.tenants[tenant_name]["ingestion_time"] = self.tenants[tenant_name].get("ingestion_time", 0) + metrics.get("ingestion_time", 0)
            self.tenants[tenant_name]["successful_rows"] = self.tenants[tenant_name].get("successful_rows", 0) + metrics.get("successful_rows", 0)
            self.tenants[tenant_name]["failed_rows"] = self.tenants[tenant_name].get("failed_rows", 0) + metrics.get("failed_rows", 0)
            self.tenants[tenant_name]["qps"] = self.tenants[tenant_name]["data_size"] / self.tenants[tenant_name]["ingestion_time"]
            self.performance_metrics(tenant_name)
        return is_success
    
    def performance_metrics(self, tenant_name):
        success_rows = self.tenants[tenant_name]["successful_rows"]
        failed_rows = self.tenants[tenant_name]["failed_rows"]
        print("Tenant: {} QPS: {} Time {} Successful Rows: {} Failed Rows: {}".format(tenant_name, self.tenants[tenant_name]["qps"], self.tenants[tenant_name]["ingestion_time"], success_rows, failed_rows))
        logger.info("Tenant: {} QPS: {} Time {} Successful Rows: {} Failed Rows: {}".format(tenant_name, self.tenants[tenant_name]["qps"], self.tenants[tenant_name]["ingestion_time"], success_rows, failed_rows))

    def on_created(self, event):
        print("Created: {} file".format(event.src_path))
        if(event.event_type == "created" and event.is_directory == False):
            if not self.check_constraints(event):
                # move to invalid directory
                invalid_directory = os.getcwd() + "/client-staging-invalid-directory"
                if not os.path.exists(invalid_directory):
                    os.makedirs(invalid_directory)
                new_file = os.getcwd() + "/client-staging-invalid-directory/" + event.src_path.split("/")[-1]
                os.rename(event.src_path, new_file)
                print("Move file to: {}".format(new_file))
                return
            # call clinetbatchingestapp
            if  self.call_client_batchingestapp(event):
                os.remove(event.src_path)
                print("Deleted: {} file".format(event.src_path))
            else:
                # move to failed directory
                failed_directory = os.getcwd() + "/client-staging-failed-directory"
                if not os.path.exists(failed_directory):
                    os.makedirs(failed_directory)
                new_file = os.getcwd() + "/client-staging-failed-directory/" + event.src_path.split("/")[-1]
                os.rename(event.src_path, new_file)
                print("Move file to: {}".format(new_file))

def set_opentelemetry():
    view_with_attributes_limit_successful_rows = View(
        instrument_type=metrics.Counter,
        instrument_name="successful_rows",
        attribute_keys={"tenant"},
    )
    view_with_attributes_limit_failed_rows = View(
        instrument_type=metrics.Counter,
        instrument_name="failed_rows",
        attribute_keys={"tenant"},
    )
    view_with_attributes_limit_data_size = View(
        instrument_type=metrics.Counter,
        instrument_name="data_size",
        attribute_keys={"tenant"},
    )
    view_with_attributes_limit_ingestion_time = View(
        instrument_type=metrics.Counter,
        instrument_name="ingestion_time",
        attribute_keys={"tenant"},
    )
    exporter = OTLPMetricExporter(insecure=True)
    # MetricReader: collect metrics and export to OTLP, default interval is 60000 milliseconds
    # https://opentelemetry.io/docs/reference/specification/metrics/sdk/#periodic-exporting-metricreader
    reader = PeriodicExportingMetricReader(exporter)
    # MteterProvider: It provides access to Meters.
    provider = MeterProvider(
        metric_readers=[reader],
        views=[view_with_attributes_limit_successful_rows, view_with_attributes_limit_failed_rows, view_with_attributes_limit_data_size, view_with_attributes_limit_ingestion_time]
    )

    # set global MeterProvider
    metrics.set_meter_provider(provider)
    # Meter: responsible for creating Instruments
    meter = metrics.get_meter_provider().get_meter("batch", "0.1.0")
    return meter

if __name__=="__main__":
    logger = set_logger()
    meter = set_opentelemetry()
    folder_name = "./client-staging-input-directory"
    w = Watcher(folder_name, MyHandler())
    w.run()
