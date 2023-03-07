import json, time, os
import pandas as pd
import pymongo
def ingestion(file_path, extension, name):
    print("Ingesting file: " + file_path, "with name: " + name)
    client = pymongo.MongoClient("mongodb://localhost:27117/")
    db = client["airbnb"]
    collection = db["listing"]

    # metrics
    start = time.time()
    end = 0
    data_size = os.path.getsize(file_path) # in bytes
    sucessful_rows = 0
    failed_rows = 0
    if(extension == "csv"):
        data = pd.read_csv(file_path)
        data_json = json.loads(data.to_json(orient='records'))
        # TODO: insert data to database
        result = collection.insert_many(data_json)
        end = time.time()
        sucessful_rows = len(result.inserted_ids)
        failed_rows = len(data_json) - sucessful_rows
    else:
        print("{} file type {} not supported!".format(name, extension))
        return False, {}
    
    metrics = {
        "ingestion_time": end - start, # float in seconds
        "ingestion_type": "batch",
        "file_name": file_path.split("/")[-1],
        "ingestion_rate": data_size / (time.time() - start),
        "data_size": data_size, # in bytes
        "sucessful_rows": sucessful_rows,
        "failed_rows": failed_rows,
        "tanent_name": name
    }
    return True, metrics