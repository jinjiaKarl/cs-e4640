def ingestion(file_path, name):
    print("Ingesting file: " + file_path, "with name: " + name)
    return True, {"file_count": 1, "file_size": 1000}