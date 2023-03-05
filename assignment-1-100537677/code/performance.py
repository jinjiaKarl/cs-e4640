import time, threading
import argparse
import pandas as pd
import json
import pymongo
import numpy as np

# python3 performance.py --database_uri localhost:27117 --database airbnb --collection listing --filepath ../data/data.csv --num_users 1 --num_requests 1
def set_args():
    parser = argparse.ArgumentParser(description="Database performance test.")
    parser.add_argument(
        "--database_uri",
        type=str,
        help="database uri",
        default="localhost:27117",
    )
    parser.add_argument(
        "--database", type=str, help="database name", default="airbnb", required=True
    )
    parser.add_argument(
        "--collection",
        type=str,
        help="collection name",
        default="listing",
        required=True,
    )
    parser.add_argument(
        "--w",
        type=int,
        help="used with replication, 0: no wait, 1: wait for primary, 2: wait for 2 servers, -1: wait for majority servers",
        default="-1",
    )
    parser.add_argument(
        "--j",
        type=bool,
        help="used with replication, wait for journaling",
        default="true",
    )
    parser.add_argument(
        "--filepath",
        type=str,
        help="csv file path",
        default="../data/data.csv",
        required=True,
    )
    parser.add_argument(
        "--num_users", type=int, help="concurrent users", default=1, required=True
    )
    parser.add_argument(
        "--num_requests",
        type=int,
        help="num_requests per user",
        default=1,
        required=True,
    )
    args = parser.parse_args()
    return args


def connect_to_mongo(uri, database, collection, w, j):
    client = pymongo.MongoClient(uri)
    db = client[database]
    table = db[collection]
    if w == 0:
        table = table.with_options(
            write_concern=pymongo.write_concern.WriteConcern(w=0)
        )
    elif w == 1:
        table = table.with_options(
            write_concern=pymongo.write_concern.WriteConcern(w=1)
        )
    elif w == 2:
        table = table.with_options(
            write_concern=pymongo.write_concern.WriteConcern(w=2)
        )
    elif w == -1:
        table = table.with_options(
            write_concern=pymongo.write_concern.WriteConcern(w="majority")
        )
    if j:
        table = table.with_options(
            write_concern=pymongo.write_concern.WriteConcern(j=True)
        )
    else:
        table = table.with_options(
            write_concern=pymongo.write_concern.WriteConcern(j=False)
        )
    return table


class TestDMS(threading.Thread):
    def __init__(self, db, filepath, name, num_requests):
        super().__init__()
        self.name = name
        self.db = db
        self.filepath = filepath
        self.num_requests = num_requests
        self.result = None

    def run(self) -> None:
        data = pd.read_csv(self.filepath)
        data_json = json.loads(data.to_json(orient="records"))
        times = []
        data_lines_actual = 0
        data_lines_expected = len(data_json) * self.num_requests
        for i in range(self.num_requests):
            try:
                start = time.time()
                # deep copy as pymongo will modify the data
                # https://pymongo.readthedocs.io/en/stable/faq.html#writes-and-ids
                data_json_copy = json.loads(json.dumps(data_json))
                result = self.db.insert_many(data_json_copy)
                data_lines_actual += len(result.inserted_ids)
                times.append(time.time() - start)
                print(
                    "{} ingested {} documents\n".format(
                        self.name, len(result.inserted_ids)
                    )
                )
            except pymongo.errors.BulkWriteError as e:
                print(e)
            except Exception as e:
                print(e)

        self.result = {
            "times": times,
            "data_lines_actual": data_lines_actual,
            "data_lines_expected": data_lines_expected,
        }

    def get_result(self):
        return self.result


if __name__ == "__main__":
    args = set_args()
    db = connect_to_mongo(
        args.database_uri, args.database, args.collection, args.w, args.j
    )
    threads = []
    for i in range(args.num_users):
        threads.append(
            TestDMS(db, args.filepath, "user_{}".format(i), args.num_requests)
        )
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    times = []
    data_lines = 0
    data_expected = 0
    for t in threads:
        if t.get_result() is None:
            continue
        times.extend(t.get_result().get("times"))
        data_lines += t.get_result().get("data_lines_actual")
        data_expected += t.get_result().get("data_lines_expected")
    times.sort()
    arr = np.array(times)

    print(
        "{} users requests: {} data_lines: {}  fails: {} throughputs: {} avg: {} std: {} min: {}  90%: {} 99%: {} max: {}\n".format(
            args.num_users,
            args.num_requests,
            data_lines,
            data_expected - data_lines,
            data_lines / np.sum(arr),
            np.mean(arr),
            np.std(arr),
            np.min(arr),
            np.percentile(arr, 90),
            np.percentile(arr, 99),
            np.max(arr),
        )
    )
