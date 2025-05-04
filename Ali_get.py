import requests, time, json

tree_url = "https://pg5vtzqdf6.execute-api.us-east-1.amazonaws.com/api/tree"

def print_tree(nodes, level=0):
    for node in nodes:
        indent = "  " * level
        print(f"{indent}- {node['label']}")
        print_tree(node.get("children", []), level + 1)

# First: cold start (no Redis)
t0 = time.time()
res1 = requests.get(tree_url)
print("Cold (no cache):", time.time() - t0)

# Second: hot cache
t0 = time.time()
res2 = requests.get(tree_url)
print("Warm (Redis cached):", time.time() - t0)
print(len(res2.json()))

