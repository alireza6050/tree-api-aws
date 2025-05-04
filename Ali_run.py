import requests
import time
import json
import random

API_URL = "https://pg5vtzqdf6.execute-api.us-east-1.amazonaws.com/api/tree?mode=bulk"

def generate_nodes(count):
    nodes = []
    nodes.append({"label": "root", "parentId": None})
    for i in range(1, count):
        parent_index = random.randint(0, i - 1)
        nodes.append({
            "label": f"node{i}",
            "parentId": "root" if parent_index == 0 else f"node{parent_index}"
        })
    return nodes

if __name__ == "__main__":
    print("Generating data...")
    data = generate_nodes(1)

    print("Sending bulk insert...")
    start = time.time()
    res = requests.post(API_URL, json=data)
    end = time.time()

    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.json()}")
    print(f"Time taken: {end - start:.2f} seconds")
