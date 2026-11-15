"""shaadi-demo: serves the one-page presentation (GET /demo) and its helpers.

GET  /demo                    -> the HTML page (same origin as the API, so its buttons call /baseline, /interest, /moderate)
GET  /demo/photo?key=photos/x -> the test photo as JPEG (bucket stays private; read with this role)
GET  /demo/items?table=verdicts|interests -> latest items from DynamoDB
POST /demo/cold {"fn": "ping"|"interest"|"moderate"} -> sets a new RUN_NONCE env var so the next call is a cold start
"""
import base64
import json
import os
import time
import uuid
from decimal import Decimal

import boto3
from boto3.dynamodb.types import TypeDeserializer

BUCKET = os.environ["BUCKET"]
S3 = boto3.client("s3")
DDB = boto3.client("dynamodb")
LAMBDA = boto3.client("lambda")
DES = TypeDeserializer()
FUNCS = {"ping": "shaadi-ping", "interest": "shaadi-interest-api", "moderate": "shaadi-moderate"}
TABLES = {"verdicts": "verdicts", "interests": "Interests"}
HTML = __HTML__


def resp(code, body, ctype="application/json", b64=False):
    if not isinstance(body, str):
        body = json.dumps(body, default=lambda o: float(o) if isinstance(o, Decimal) else str(o))
    return {"statusCode": code, "headers": {"Content-Type": ctype, "Cache-Control": "no-store"},
            "body": body, "isBase64Encoded": b64}


def lambda_handler(event, context):
    path = event.get("rawPath", "/demo")
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    qs = event.get("queryStringParameters") or {}

    if path in ("/demo", "/demo/"):
        return resp(200, HTML, "text/html; charset=utf-8")

    if path == "/demo/photo":
        key = qs.get("key", "photos/photo_01.jpg")
        if not key.startswith("photos/") or ".." in key:
            return resp(400, {"error": "key must be under photos/"})
        data = S3.get_object(Bucket=BUCKET, Key=key)["Body"].read()
        return resp(200, base64.b64encode(data).decode(), "image/jpeg", True)

    if path == "/demo/items":
        table = TABLES.get(qs.get("table", "verdicts"))
        if not table:
            return resp(400, {"error": "unknown table"})
        items, kw = [], {"TableName": table}
        while True:
            page = DDB.scan(**kw)
            items += [{k: DES.deserialize(v) for k, v in it.items()} for it in page["Items"]]
            if "LastEvaluatedKey" not in page:
                break
            kw["ExclusiveStartKey"] = page["LastEvaluatedKey"]
        items.sort(key=lambda i: i.get("createdAt", 0), reverse=True)
        return resp(200, {"count": len(items), "items": items[:20]})

    if path == "/demo/cold" and method == "POST":
        fn = FUNCS.get(json.loads(event.get("body") or "{}").get("fn", "ping"))
        if not fn:
            return resp(400, {"error": "unknown function"})
        t0 = time.time()
        env = LAMBDA.get_function_configuration(FunctionName=fn).get("Environment", {}).get("Variables", {})
        env["RUN_NONCE"] = uuid.uuid4().hex[:8]
        LAMBDA.update_function_configuration(FunctionName=fn, Environment={"Variables": env})
        LAMBDA.get_waiter("function_updated").wait(FunctionName=fn, WaiterConfig={"Delay": 1, "MaxAttempts": 25})
        time.sleep(2)
        return resp(200, {"function": fn, "nonce": env["RUN_NONCE"], "seconds": round(time.time() - t0, 1)})

    return resp(404, {"error": "not found", "path": path})
