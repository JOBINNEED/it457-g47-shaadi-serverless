# IT-457 Group 47: Shaadi.com on AWS, serverless proof of concept

IT-457 Cloud Computing case study project, Theme 4: Serverless and Startups.

| Member | Student ID | Main contribution |
|---|---|---|
| Sri Sai Madhava Teja Yanduri | 202301138 | Case analysis, reports, results write-up |
| Kavya Chauhan | 202301116 | AWS build: functions, IAM, API, SAM template, harness |
| Venkata L Subramanyam | 202301280 | Measurements, Logs Insights, data, charts, workbook |

**Live presentation page:** https://ypq1jax2t5.execute-api.ap-south-1.amazonaws.com/demo
(only while the stack is running; it is paused between sessions)

## What this project is

1. **Case analysis.** How Shaadi.com moved from a hosted private cloud to AWS, the four problems it solved
   (delivery speed, DB3 IOPS, messaging scale, manual photo review), the architecture, and the cost per 1,000 requests.
2. **Serverless proof of concept** in `ap-south-1` (Mumbai), rebuilding Shaadi.com's serverless photo moderation:

```
Client -> API Gateway (HTTP API) -> Lambda (Python 3.15)
            GET  /baseline   -> shaadi-ping           (no AWS calls: pure overhead)
            POST /interest   -> shaadi-interest-api   -> DynamoDB Interests
            POST /moderate   -> shaadi-moderate       -> Rekognition (reads photo from S3) -> DynamoDB verdicts
            GET  /demo       -> shaadi-demo           (one-page presentation with live calls)
          shaadi-loadgen (console-invoked harness): cold starts, load, Logs Insights -> CSV in S3
```

3. **Experiments:** E1 cold vs warm, E2 memory 128/256/512/1,024 MB, E3 concurrency 1/9/50 users, E4 cost per 1,000 requests.

## Key results (12-13 Nov 2026)

| | Baseline | Interest API | Moderation |
|---|---|---|---|
| Warm latency (client p50) | 18 ms | 24-32 ms | 173-202 ms |
| Cold latency, 128 -> 1,024 MB | 493 -> 310 ms | 1,950 -> 699 ms | 2,071 -> 1,608 ms |
| Cost per 1,000 requests | $0.0012 | $0.0019 | $1.0038 (99.6% Rekognition) |

- Cold-start Billed Duration = Init + handler time (INIT is billed).
- Served throughput capped at ~100 req/s = 10 x the account's concurrency quota of 10; 59-63% HTTP 503 above it.
- API Gateway reserves `/ping`, so the baseline route is `/baseline`.

## Repository layout

| Path | Contents |
|---|---|
| `docs/` | Week 1, Week 2 and final reports; complete project guide; presentation guide |
| `src/lambdas/` | `ping_function.py`, `interest_function.py`, `moderate_function.py` |
| `src/demo/` | Presentation page (`page.html`) and the function that serves it |
| `infra/` | `template.yaml` (AWS SAM, whole stack) and `iam/` least-privilege policies |
| `experiments/` | `loadgen_function.py` harness, Logs Insights queries, browser scripts |
| `data/` | Run 1 pilot and run 2 datasets (CSV) and the results workbook |
| `analysis/` | Scripts that build the charts, workbook, reports and guides |
| `figures/`, `screenshots/` | Charts and AWS console evidence |

## Deploy from scratch

```bash
cd infra
sam build && sam deploy --guided --region ap-south-1     # creates everything, prints the demo URL
sam delete                                              # removes everything
```
Upload test images to `photos/` in the bucket (see `experiments/generate_test_images.js`).

## Run the experiments

Invoke `shaadi-loadgen` from the Lambda console with:
```json
{"mode": "coldwarm", "targets": ["ping", "interest", "moderate"], "memories": [128, 256, 512, 1024], "burst": 8, "warm": 50}
{"mode": "concurrency", "target": "ping", "memory": 512, "levels": [1, 9, 50], "seconds": 60}
{"mode": "logs", "minutes": 90}
```
