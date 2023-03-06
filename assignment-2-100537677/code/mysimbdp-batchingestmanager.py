import time, json, os, importlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


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
            if (constraints.get("file_count") == None):
                self.tenants[tenant_name]["file_count"] = 0
            else:
                self.tenants[tenant_name]["file_count"] += 1
        # check
        if extension  not in constraints.get("file_types").split(","):
            print("{} file {} type not allowed!".format(tenant_name, filename))
            return False
        if (constraints.get("number_of_files_limit") != None and self.tenants[tenant_name]["file_count"] > constraints.get("number_of_files_limit")):
            print("{} file {} count exceeded!".format(tenant_name, filename))
            return False
        file_size = os.path.getsize(src_path)
        if (constraints.get("file_size_limit") != None and file_size > constraints.get("file_size_limit")):
            print("{} file {} size exceeded!".format(tenant_name, filename))
            return False
        return True
    
    def call_client_batchingestapp(self, event):
        src_path, _, _, tenant_name = self.parse_src_path(event)
        app = importlib.import_module("clientbatchingestapp-{}".format(tenant_name) )
        is_success, metrics = app.ingestion(src_path, tenant_name)
        print("Ingestion result: {}".format(is_success))
        print("Ingestion metrics: {}".format(metrics))
        return is_success
    
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


if __name__=="__main__":
    folder_name = "./client-staging-input-directory"
    w = Watcher(folder_name, MyHandler())
    w.run()
