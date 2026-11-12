"""Lambda B (photo moderation): POST /moderate {"imageKey": "photos/photo_01.jpg"}.

Mirrors Shaadi.com's serverless photo screening: Amazon Rekognition reads the photo straight from S3,
the function turns the labels into a verdict and stores it in DynamoDB.
"""
import json
import os
import time
import uuid

import boto3

BUCKET = os.environ["BUCKET"]
TABLE = boto3.resource("dynamodb").Table(os.environ.get("TABLE_NAME", "verdicts"))
REKOGNITION = boto3.client("rekognition")
MIN_CONFIDENCE = 60   # labels below this are ignored
REJECT_AT = 80        # a label at or above this rejects the photo; 60-80 goes to human review
COLD_START = True


def respond(status, body):
    return {"statusCode": status, "headers": {"Content-Type": "application/json"},
            "body": json.dumps(body, default=str)}


def lambda_handler(event, context):
    global COLD_START
    cold, COLD_START = COLD_START, False
    data = json.loads(event.get("body") or "{}")
    key = data.get("imageKey")
    if not key:
        return respond(400, {"error": "imageKey is required", "coldStart": cold})

    t0 = time.perf_counter()
    result = REKOGNITION.detect_moderation_labels(
        Image={"S3Object": {"Bucket": BUCKET, "Name": key}}, MinConfidence=MIN_CONFIDENCE)
    rekognition_ms = round((time.perf_counter() - t0) * 1000, 1)

    labels = [{"name": l["Name"], "confidence": round(l["Confidence"], 1)} for l in result["ModerationLabels"]]
    top = max((l["confidence"] for l in labels), default=0)
    verdict = "rejected" if top >= REJECT_AT else "review" if labels else "approved"

    TABLE.put_item(Item={
        "verdictId": str(uuid.uuid4()), "imageKey": key, "verdict": verdict,
        "labels": json.dumps(labels), "rekognitionMs": str(rekognition_ms),
        "coldStart": cold, "createdAt": int(time.time() * 1000)})
    print(json.dumps({"op": "moderate", "coldStart": cold, "rekognitionMs": rekognition_ms}))
    return respond(200, {"imageKey": key, "verdict": verdict, "labels": labels,
                         "rekognitionMs": rekognition_ms, "coldStart": cold})
