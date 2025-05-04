import boto3
import json
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method")
    if method == "GET":
        response = table.scan()
        nodes = response.get('Items', [])
        return {
            "statusCode": 200,
            "body": json.dumps(build_tree(nodes))
        }

    elif method == 'POST':
        body = json.loads(event['body'])
        item = {
            "id": str(hash(body['label'] + str(body['parentId']))),
            "label": body['label'],
            "parentId": str(body['parentId']),
        }
        table.put_item(Item=item)
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
