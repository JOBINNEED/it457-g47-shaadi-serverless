"""Lambda A (baseline): GET /baseline (API Gateway reserves /ping for its own health check). No AWS SDK, no network calls - measures Lambda + API Gateway alone."""
import json

COLD_START = True  # module code runs once per execution environment


def lambda_handler(event, context):
    global COLD_START
    cold, COLD_START = COLD_START, False
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"pong": True, "coldStart": cold}),
    }
