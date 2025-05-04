import requests, time, json

tree_url = "https://upm5h5b3p9.execute-api.us-east-1.amazonaws.com/api/tree"

# First: cold start (no Redis)
t0 = time.time()
res1 = requests.get(tree_url)
print("Cold (no cache):", time.time() - t0)

# Second: hot cache
t0 = time.time()
res2 = requests.get(tree_url)
print("Warm (Redis cached):", time.time() - t0)
print(res2.json())