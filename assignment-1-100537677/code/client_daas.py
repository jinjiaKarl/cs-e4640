import pandas as pd
import requests, argparse
import json

# python3 client_daas.py --ingest_file_path ../data/data.csv
def set_args():
    parser = argparse.ArgumentParser(description="API ingestion.")
    parser.add_argument("--ingest_file_path", type=str, help="file path")
    parser.add_argument(
        "--addr", type=str, help="server addr", default="http://localhost:8000"
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    try:
        args = set_args()
        ingest_file_path = args.ingest_file_path
        data = pd.read_csv(ingest_file_path)
        data_json = data.to_json(orient="records")
        # loads: str -> dict
        data_json = json.loads(data_json)
        r = requests.post(args.addr + "/ingestion", json=data_json)
        print(r.json())
    except Exception as e:
        print(e)
