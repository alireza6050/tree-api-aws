import boto3
import json
import os
import redis

dynamodb = boto3.resource('dynamodb')

def get_table():
    return dynamodb.Table(os.environ['TABLE_NAME'])

def get_redis_client():
    return redis.Redis(
        host=os.environ['REDIS_HOST'],
        port=6379,
        decode_responses=True
    )

def lambda_handler(event, context):
    table = get_table()
    redis_client = get_redis_client()

    method = event.get("requestContext", {}).get("http", {}).get("method")
    path = event.get("rawPath") or event.get("requestContext", {}).get("http", {}).get("path", "")
    query = event.get("rawQueryString", "")

    # =================== GET /api/tree ===================
    if method == "GET":
        cached = redis_client.get("tree")
        if cached:
            return {"statusCode": 200, "body": cached}

        response = table.scan()
        nodes = response.get('Items', [])
        tree = json.dumps(build_tree(nodes))
        redis_client.set("tree", tree, ex=300)

        return {
            "statusCode": 200,
            "body": tree
        }

    # =================== POST /api/tree ===================
    elif method == "POST":
        body = json.loads(event['body'])

        # Handle bulk insert if query string or path includes "bulk"
        if "bulk" in path or "mode=bulk" in query:
            items = []
            for node in body:
                item = {
                    "id": str(hash(node['label'] + str(node['parentId']))),
                    "label": node['label'],
                    "parentId": str(node['parentId']),
                }
                items.append({"PutRequest": {"Item": item}})
            
            for i in range(0, len(items), 25):
                batch = items[i:i + 25]
                table.meta.client.batch_write_item(RequestItems={table.name: batch})

            redis_client.delete("tree")

            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Bulk insert complete", "count": len(items)})
            }

        # Handle single node insert
        item = {
            "id": str(hash(body['label'] + str(body['parentId']))),
            "label": body['label'],
            "parentId": str(body['parentId']),
        }
        table.put_item(Item=item)
        redis_client.delete("tree")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Node created", "item": item})
        }

    # =================== Unsupported ===================
    return {
        "statusCode": 404,
        "body": json.dumps({"message": "Not Found"})
    }

def build_tree(nodes):
    node_map = {n['id']: {**n, "children": []} for n in nodes}
    roots = []
    for n in nodes:
        pid = n.get('parentId')
        if pid and pid in node_map:
            node_map[pid]["children"].append(node_map[n['id']])
        else:
            roots.append(node_map[n['id']])
    return roots
