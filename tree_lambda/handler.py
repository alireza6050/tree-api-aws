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
            "body": json.dumps(tree)
        }

    elif method == 'POST':
        body = json.loads(event['body'])
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
