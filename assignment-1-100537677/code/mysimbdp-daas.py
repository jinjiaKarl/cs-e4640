from flask import Flask
from flask import request, jsonify

# from flask_restx import Api, Resource, fields
import pymongo
from bson import json_util
import json
import argparse
import logging

# python3 mysimbdp-daas.py --database airbnb --collection listing
logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    filename="../logs/daas.log",
    filemode="w",
    level=logging.DEBUG,
)


def connect_to_mongo(uri, database, collection):
    client = pymongo.MongoClient(uri)
    db = client[database]
    table = db[collection]
    return table


def set_args():
    parser = argparse.ArgumentParser(description="Data ingestion.")
    parser.add_argument(
        "--database_uri",
        type=str,
        help="database uri",
        default="localhost:27117",
    )
    parser.add_argument("--database", type=str, help="database name", required=True)
    parser.add_argument("--collection", type=str, help="collection name", required=True)
    args = parser.parse_args()
    return args


app = Flask(__name__)

""" insert multiple record """
@app.post("/ingestion")
def ingestion():
    try:
        data = request.get_json() 
        # print(type(data)) # list
        app.logger.info("data: %s", data)
        # insert data to mongodb
        result = db.insert_many(data)
        return jsonify({"inserted_len": len(result.inserted_ids)}), 201
    except Exception as e:
        app.logger.error("error: %s", e)
        return jsonify({"error": str(e)}), 400


@app.get("/query")
def query():
    try:
        name = request.args.get("name")
        if name:
            result = list(db.find({"name": {"$regex": "^.*" + name + ".*$"}}))
            return json.dumps(result, indent=4, default=json_util.default), 200
        result = list(db.find())
        app.logger.info("result: %s", result)
        return json.dumps(result, indent=4, default=json_util.default), 200
    except Exception as e:
        app.logger.error("error: %s", e)
        return jsonify({"error": str(e)}), 400


@app.get("/query/<id>")
def query_id(id):
    try:
        result = db.find_one({"id": int(id)})
        return json.dumps(result, indent=4, default=json_util.default), 200
    except Exception as e:
        app.logger.error("error: %s", e)
        return jsonify({"error": str(e)}), 400


""" insert one record """
@app.post("/insert")
def insert():
    try:
        data = request.get_json() 
        #print(type(data))  # dict
        result = db.insert_one(data)
        # print(type(result.inserted_id)) # <class 'bson.objectid.ObjectId'>
        return jsonify({"inserted_id": str(result.inserted_id)}), 201
    except Exception as e:
        app.logger.error("error: %s", e)
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    try:
        args = set_args()
        db = connect_to_mongo(args.database_uri, args.database, args.collection)
        app.run(debug=True, host="0.0.0.0", port=8000)
    except Exception as e:
        app.logger.error("error: %s", e)
