"""Shaadi.com PoC: 'send interest' API (API Gateway HTTP API -> Lambda -> DynamoDB)."""
import json
import os
import time
import uuid

import boto3

TABLE = boto3.resource("dynamodb").Table(os.environ.get("TABLE_NAME", "Interests"))
COLD_START = True  # module code runs once per execution environment


def respond(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body, default=str),
    }


def lambda_handler(event, context):
    global COLD_START
    cold, COLD_START = COLD_START, False
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")

    if method == "POST":
        data = json.loads(event.get("body") or "{}")
        item = {
            "interestId": str(uuid.uuid4()),
            "fromUser": str(data.get("from", "anonymous")),
            "toUser": str(data.get("to", "anonymous")),
            "message": str(data.get("message", ""))[:200],
            "createdAt": int(time.time() * 1000),
        }
        TABLE.put_item(Item=item)
        print(json.dumps({"op": "put", "coldStart": cold}))
        return respond(201, {"saved": item, "coldStart": cold})

    interest_id = (event.get("pathParameters") or {}).get("id")
    if interest_id:
        found = TABLE.get_item(Key={"interestId": interest_id}).get("Item")
        print(json.dumps({"op": "get", "coldStart": cold}))
        return respond(200 if found else 404, {"item": found, "coldStart": cold})

    return respond(200, {"status": "ok", "service": "shaadi-interest-api", "coldStart": cold})
