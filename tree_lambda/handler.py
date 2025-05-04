import boto3
import json
import os
import redis
import uuid

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Get DynamoDB table instance
def get_table():
    return dynamodb.Table(os.environ['TABLE_NAME'])

# Connect to Redis (ElastiCache)
def get_redis_client():
    return redis.Redis(
        host=os.environ['REDIS_HOST'],
        port=6379,
        decode_responses=True
    )

# Lambda entry point
def lambda_handler(event, context):
    table = get_table()
    redis_client = get_redis_client()

    method = event.get("requestContext", {}).get("http", {}).get("method")

    # ========== GET /api/tree ==========
    if method == "GET":
        # Return cached result if available
        cached = redis_client.get("tree")
        if cached:
            return {"statusCode": 200, "body": cached}

        # Fetch all nodes from DynamoDB
        response = table.scan()
        nodes = response.get('Items', [])

        # Build tree structure and cache it
        tree = json.dumps(build_tree(nodes))
        redis_client.set("tree", tree, ex=300)  # Cache for 5 minutes

        return {
            "statusCode": 200,
            "body": tree
        }

    # ========== POST /api/tree ==========
    elif method == "POST":
        body = json.loads(event['body'])

        # Create new node with UUID
        item = {
            "id": str(uuid.uuid4()),
            "label": body['label'],
            "parentId": body['parentId']
        }

        # Save to DynamoDB and clear cache
        table.put_item(Item=item)
        redis_client.delete("tree")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Node created", "item": item})
        }

    # ========== Unsupported Method ==========
    return {
        "statusCode": 404,
        "body": json.dumps({"message": "Not Found"})
    }

# Build tree from flat list of nodes
def build_tree(nodes):
    # Map nodes by ID and prepare 'children' list
    node_map = {
        n['id']: {
            "id": n['id'],
            "label": n['label'],
            "children": []
        } for n in nodes
    }

    roots = []
    for n in nodes:
        pid = n.get('parentId')
        if pid and pid in node_map:
            node_map[pid]["children"].append(node_map[n['id']])
        else:
            roots.append(node_map[n['id']])  # Root node
    return roots
