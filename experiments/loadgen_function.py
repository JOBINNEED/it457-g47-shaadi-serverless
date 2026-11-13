"""shaadi-loadgen: experiment harness that runs inside AWS (ap-south-1).

Invoked from the Lambda console with a JSON test event:
  {"mode": "coldwarm", "targets": ["ping", "interest"], "memories": [128, 256, 512, 1024], "burst": 8, "warm": 50}
  {"mode": "concurrency", "target": "ping", "memory": 512, "levels": [1, 9, 50], "seconds": 60}
  {"mode": "logs", "minutes": 120}

coldwarm    - for each target and memory size: change the memory and an environment variable (this forces
              Lambda to start new execution environments), fire `burst` requests at the same instant (cold
              starts), then `warm` requests one after another (warm).
concurrency - keeps N virtual users calling the API for `seconds`, for each N in `levels` (replaces k6).
logs        - CloudWatch Logs Insights: every REPORT line of the three functions (init, duration, billed).
Every mode writes CSV files to s3://$BUCKET/results/ and returns a short summary.
"""
import csv
import io
import json
import os
import statistics
import threading
import time
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor

import boto3

API = os.environ["API_URL"].rstrip("/")
BUCKET = os.environ["BUCKET"]
LAMBDA = boto3.client("lambda")
LOGS = boto3.client("logs")
S3 = boto3.client("s3")

TARGETS = {
    "ping": {"function": "shaadi-ping", "method": "GET", "path": "/baseline"},
    "interest": {"function": "shaadi-interest-api", "method": "POST", "path": "/interest"},
    "moderate": {"function": "shaadi-moderate", "method": "POST", "path": "/moderate"},
}


def body_for(target, i):
    if target == "interest":
        return {"from": "loadgen", "to": f"user_{i}", "message": "experiment"}
    if target == "moderate":
        return {"imageKey": f"photos/photo_{i % 30 + 1:02d}.jpg"}
    return None


def call(target, i):
    t = TARGETS[target]
    data = body_for(target, i)
    req = urllib.request.Request(API + t["path"], method=t["method"],
                                 data=json.dumps(data).encode() if data else None,
                                 headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    status, cold, extra = 0, None, ""
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status = r.status
            payload = json.loads(r.read())
            cold = payload.get("coldStart")
            extra = payload.get("rekognitionMs", "")
    except urllib.error.HTTPError as e:
        status = e.code
    except Exception as e:  # network error / timeout
        status = -1
        extra = type(e).__name__
    return {"status": status, "cold": cold, "ms": round((time.perf_counter() - t0) * 1000, 2), "extra": extra}


def force_cold(function, memory):
    cfg = LAMBDA.get_function_configuration(FunctionName=function)
    env = cfg.get("Environment", {}).get("Variables", {})
    env["RUN_NONCE"] = uuid.uuid4().hex[:8]
    LAMBDA.update_function_configuration(FunctionName=function, MemorySize=memory, Environment={"Variables": env})
    LAMBDA.get_waiter("function_updated").wait(FunctionName=function)
    time.sleep(3)


def put_csv(key, rows, fields):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
    S3.put_object(Bucket=BUCKET, Key=key, Body=buf.getvalue().encode(), ContentType="text/plain; charset=utf-8")


def pct(values, p):
    values = sorted(values)
    return values[min(len(values) - 1, int(round(p / 100 * (len(values) - 1))))] if values else None


def coldwarm(ev, run):
    rows, summary = [], []
    for target in ev.get("targets", ["ping", "interest"]):
        for mem in ev.get("memories", [128, 256, 512, 1024]):
            force_cold(TARGETS[target]["function"], mem)
            n = ev.get("burst", 8)
            gate = threading.Barrier(n)

            def burst_call(i):
                gate.wait()
                return call(target, i)

            with ThreadPoolExecutor(max_workers=n) as pool:
                burst = list(pool.map(burst_call, range(n)))
            warm = [call(target, 100 + i) for i in range(ev.get("warm", 50))]
            for phase, results in (("cold_burst", burst), ("warm_sequential", warm)):
                for i, r in enumerate(results, 1):
                    rows.append({"target": target, "memory_mb": mem, "phase": phase, "request_no": i, **r})
            cold_ms = [r["ms"] for r in burst if r["cold"]]
            warm_ms = [r["ms"] for r in warm if r["status"] == 200 or r["status"] == 201]
            summary.append({"target": target, "memory_mb": mem, "cold_starts": len(cold_ms),
                            "cold_p50_ms": pct(cold_ms, 50), "warm_p50_ms": pct(warm_ms, 50),
                            "warm_p95_ms": pct(warm_ms, 95),
                            "errors": sum(1 for r in burst + warm if r["status"] not in (200, 201))})
    put_csv(f"results/{run}_coldwarm_raw.csv", rows,
            ["target", "memory_mb", "phase", "request_no", "status", "cold", "ms", "extra"])
    put_csv(f"results/{run}_coldwarm_summary.csv", summary, list(summary[0].keys()))
    return summary


def concurrency(ev, run):
    target = ev.get("target", "ping")
    if ev.get("memory"):
        force_cold(TARGETS[target]["function"], ev["memory"])
    rows, summary = [], []
    for level in ev.get("levels", [1, 9, 50]):
        deadline = time.time() + ev.get("seconds", 60)
        start = time.time()
        lock = threading.Lock()

        def user(u):
            i = 0
            while time.time() < deadline:
                r = call(target, u * 100000 + i)
                r.update({"level": level, "user": u, "t_s": round(time.time() - start, 3)})
                with lock:
                    rows.append(r)
                i += 1

        with ThreadPoolExecutor(max_workers=level) as pool:
            list(pool.map(user, range(level)))
        mine = [r for r in rows if r["level"] == level]
        ok = [r["ms"] for r in mine if r["status"] == 200]
        summary.append({"target": target, "virtual_users": level, "requests": len(mine), "ok": len(ok),
                        "throttled_or_error": len(mine) - len(ok),
                        "rps": round(len(mine) / ev.get("seconds", 60), 1),
                        "p50_ms": pct(ok, 50), "p95_ms": pct(ok, 95), "p99_ms": pct(ok, 99),
                        "max_ms": max(ok) if ok else None,
                        "cold_starts": sum(1 for r in mine if r["cold"])})
        time.sleep(5)
    put_csv(f"results/{run}_concurrency_raw.csv", rows,
            ["level", "user", "t_s", "status", "cold", "ms", "extra"])
    put_csv(f"results/{run}_concurrency_summary.csv", summary, list(summary[0].keys()))
    return summary


def logs(ev, run):
    end = int(time.time())
    start = end - 60 * ev.get("minutes", 120)
    rows = []
    for target, t in TARGETS.items():
        q = LOGS.start_query(
            logGroupName=f"/aws/lambda/{t['function']}", startTime=start, endTime=end, limit=10000,
            queryString='filter @type = "REPORT" | fields @timestamp, @memorySize, @initDuration, '
                        '@duration, @billedDuration, @maxMemoryUsed | sort @timestamp asc')
        while True:
            res = LOGS.get_query_results(queryId=q["queryId"])
            if res["status"] in ("Complete", "Failed", "Cancelled", "Timeout"):
                break
            time.sleep(1)
        for rec in res.get("results", []):
            f = {c["field"]: c["value"] for c in rec}
            rows.append({"function": t["function"], "timestamp": f.get("@timestamp"),
                         "memory_mb": int(float(f.get("@memorySize", 0)) / 1e6),
                         "init_ms": f.get("@initDuration", ""), "duration_ms": f.get("@duration"),
                         "billed_ms": f.get("@billedDuration"),
                         "max_memory_mb": int(float(f.get("@maxMemoryUsed", 0)) / 1e6)})
    put_csv(f"results/{run}_cloudwatch_report_lines.csv", rows,
            ["function", "timestamp", "memory_mb", "init_ms", "duration_ms", "billed_ms", "max_memory_mb"])
    return {"report_lines": len(rows), "by_function": {
        f: sum(1 for r in rows if r["function"] == f) for f in {r["function"] for r in rows}}}


def lambda_handler(event, context):
    run = time.strftime("%Y%m%dT%H%M%S")
    mode = event.get("mode")
    out = {"coldwarm": coldwarm, "concurrency": concurrency, "logs": logs}[mode](event, run)
    return {"run": run, "mode": mode, "summary": out}
