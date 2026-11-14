"""IT-457 Group 47 final report (Shaadi.com) in the Week 2 ReportLab style."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle, CondPageBreak)
from PIL import Image as PILImage

LIB = "/usr/share/fonts/truetype/liberation/"
pdfmetrics.registerFont(TTFont("Sans", LIB + "LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Sans-B", LIB + "LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Sans-I", LIB + "LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Sans-BI", LIB + "LiberationSans-BoldItalic.ttf"))
pdfmetrics.registerFont(TTFont("Serif", LIB + "LiberationSerif-Regular.ttf"))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-B", italic="Sans-I", boldItalic="Sans-BI")

OUT = "/home/claude/final/202301138_IT457_Group47_Final_Report.pdf"
W2IMG = "/home/claude/wk2/img/"
FIG = "/home/claude/final/fig/"
SHOT = "/home/claude/poc/screenshots/"
HDR_R = "Final Report: Analysis, Implementation and Results"

body = ParagraphStyle("b", fontName="Sans", fontSize=9.6, leading=13.2, spaceAfter=5)
small = ParagraphStyle("s", parent=body, fontSize=8.3, leading=10.6, spaceAfter=0)
smallb = ParagraphStyle("sb", parent=small, fontName="Sans-B")
h1 = ParagraphStyle("h1", fontName="Sans-B", fontSize=15, leading=19, spaceBefore=10, spaceAfter=6)
h2 = ParagraphStyle("h2", fontName="Sans-B", fontSize=11.5, leading=15, spaceBefore=8, spaceAfter=4)
cap = ParagraphStyle("c", fontName="Sans-I", fontSize=8, leading=10, textColor=colors.HexColor("#555555"),
                     alignment=TA_CENTER, spaceBefore=3, spaceAfter=9)
bul = ParagraphStyle("bu", parent=body, leftIndent=14, bulletIndent=3, spaceAfter=3)
boxst = ParagraphStyle("box", parent=body, fontSize=9.3, leading=12.6)

story = []
counters = {"t": 0, "f": 0}


def P(t, s=body):
    if s in (h1, h2):
        story.append(CondPageBreak(1.3*inch))
    story.append(Paragraph(t, s))


def B(items):
    for t in items:
        story.append(Paragraph(t, bul, bulletText="•"))


def caption(kind, text):
    counters[kind] += 1
    label = "Table" if kind == "t" else "Figure"
    return Paragraph(f"{label} {counters[kind]}: {text}", cap)


def table(rows, widths, text, header=True, fs=8.3, keep=True):
    data = [[Paragraph(str(c), smallb if (header and i == 0) else ParagraphStyle("x", parent=small, fontSize=fs, leading=fs + 2.3))
             for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * inch for w in widths], repeatRows=1 if header else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
          ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#888888")), ("TOPPADDING", (0, 0), (-1, -1), 3),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("LEFTPADDING", (0, 0), (-1, -1), 4)]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDEDED")), ("LINEBELOW", (0, 0), (-1, 0), 0.9, colors.black)]
    t.setStyle(TableStyle(st))
    items = [t, caption("t", text)]
    story.append(KeepTogether(items) if keep else t)
    if not keep:
        story.append(items[1])


def fig(path, text, width=6.9, maxh=None):
    w, h = PILImage.open(path).size
    ww = width * inch
    hh = ww * h / w
    if maxh and hh > maxh * inch:
        hh = maxh * inch
        ww = hh * w / h
    story.append(KeepTogether([Image(path, width=ww, height=hh), caption("f", text)]))


def page(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setFont("Sans", 7.5)
        canvas.setFillColor(colors.HexColor("#555555"))
        canvas.drawString(0.75 * inch, 10.62 * inch, "IT-457  |  Group 47  |  Shaadi.com")
        canvas.drawRightString(7.75 * inch, 10.62 * inch, HDR_R)
        canvas.setStrokeColor(colors.HexColor("#BBBBBB"))
        canvas.line(0.75 * inch, 10.56 * inch, 7.75 * inch, 10.56 * inch)
    canvas.setFont("Sans", 8)
    canvas.drawCentredString(4.25 * inch, 0.5 * inch, str(doc.page))
    canvas.restoreState()


doc = BaseDocTemplate(OUT, pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch, topMargin=0.75 * inch,
                      bottomMargin=0.75 * inch, title="IT-457 Case Study Project - Final Report (Shaadi.com, Group 47)",
                      author="Group 47: Sri Sai Madhava Teja Yanduri, Kavya Chauhan, Venkata L Subramanyam",
                      subject="Shaadi.com on AWS: case analysis, serverless PoC implementation and measured results")
doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(0.75 * inch, 0.75 * inch, 7 * inch, 9.7 * inch, id="f")], onPage=page)])

# ================================================================== COVER
story.append(Spacer(1, 1.35 * inch))
story.append(Paragraph("Cloud Computing Case Study Project", ParagraphStyle("t", fontName="Sans-B", fontSize=24, leading=30, alignment=TA_CENTER)))
story.append(Paragraph("IT-457 | Final Report: Case Analysis, Serverless Implementation and Results",
                       ParagraphStyle("t2", fontName="Serif", fontSize=14, leading=19, alignment=TA_CENTER, textColor=colors.HexColor("#7a5c3a"), spaceBefore=6)))
story.append(Paragraph("Case Study: Shaadi.com - AI/ML on AWS to analyze 67 billion event records",
                       ParagraphStyle("t3", fontName="Sans", fontSize=11, leading=15, alignment=TA_CENTER, spaceBefore=8)))
story.append(Paragraph("Theme 4: Serverless and Startups  |  Group 47", ParagraphStyle("t4", fontName="Sans-B", fontSize=11.5, leading=15, alignment=TA_CENTER, spaceBefore=4)))
story.append(Spacer(1, 0.25 * inch))
story.append(Image("/home/claude/wk1/img/p1-000.png", width=1.25 * inch, height=1.25 * inch * 426 / 744))
story.append(Spacer(1, 0.4 * inch))
cov = [["Name", "Student ID", "Role in this phase"],
       ["Sri Sai Madhava Teja Yanduri", "202301138", "Case analysis lead, results write-up, report editor"],
       ["Kavya Chauhan", "202301116", "Exercise design, AWS build, experiment runs"],
       ["Venkata L Subramanyam", "202301280", "Architecture diagrams, Logs Insights queries, cost analysis"]]
t = Table([[Paragraph(c, smallb if i == 0 else small) for c in r] for i, r in enumerate(cov)], colWidths=[2.1 * inch, 1.0 * inch, 3.2 * inch])
t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, colors.black), ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
                       ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDEDED")), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
story.append(t)
story.append(Spacer(1, 0.45 * inch))
story.append(Paragraph("Measurements taken on 12-13 November 2026 in AWS ap-south-1 (Mumbai). The stack is paused (all functions throttled) and can be restarted for the demonstration in under a minute (Appendix B).",
                       ParagraphStyle("cv", parent=small, alignment=TA_CENTER, textColor=colors.HexColor("#555555"))))
story.append(PageBreak())

# ================================================================== SUMMARY
P("Summary", h1)
P("This report completes the Shaadi.com case study. Sections 1-6 analyse how Shaadi.com (People Interactive Pvt. Ltd.) uses "
  "Amazon Web Services: the problems it faced, the architecture it moved to, what that cost, and what we would question "
  "(carried forward from Week 2, with corrections). Sections 7-9 report the hands-on part: we built a serverless proof of concept "
  "that mirrors the part of Shaadi.com that already runs on serverless, the photo moderation pipeline, plus a plain baseline "
  "function and the \"send interest\" API from the portal, and measured cold starts, memory sizing, concurrency and cost per "
  "1,000 requests in the same region Shaadi.com uses.")
P("Key findings", h2)
B(["<b>Cold starts cost 10-60x a warm call.</b> At the client, the first call to a new execution environment took 217-493 ms for "
   "the empty baseline, 699-1,950 ms for the DynamoDB function and 1,000-2,071 ms for the Rekognition function, against warm medians "
   "of 18 ms, 24-32 ms and 173-202 ms. Python start-up and importing boto3 (Init Duration up to 1.3 s) is most of it.",
   "<b>Cold starts are now billed.</b> Every cold REPORT line had Billed Duration = Init + handler time (for example 1,242 + 552 = 1,795 ms "
   "for the interest API at 128 MB), confirming the August 2025 change to INIT billing.",
   "<b>More memory helps CPU-bound start-up, not I/O.</b> Raising memory from 128 to 1,024 MB cut the interest API's cold start from "
   "1,950 to 699 ms, but the moderation function's warm time barely moved (202 to 173 ms) because it mostly waits for Rekognition, "
   "so its Lambda compute cost rose 7x. Both predictions from the Week 2 cost model held.",
   "<b>Rekognition is 99.6% of the moderation bill.</b> Measured cost per 1,000 requests: baseline $0.0012, interest API $0.0019, "
   "moderation $1.0038, of which $1.00 is the Rekognition call.",
   "<b>Account limits, not Lambda, capped throughput.</b> Our new account has a Lambda concurrency quota of 10, so Lambda allows 100 "
   "requests per second (10x concurrency). Served throughput flattened at 99-101 req/s; with 9 and 50 virtual users 59-63% of "
   "requests were rejected with HTTP 503. Shaadi.com's production account would need a raised quota and SQS buffering for spikes.",
   "<b>Two practical findings.</b> API Gateway answers <i>/ping</i> itself (\"Healthy Connection\"), so the planned GET /ping route "
   "never reached Lambda and was renamed /baseline; and renaming a route silently breaks the Lambda invoke permission scoped to the old path."])
P("What was delivered", h2)
table([["Planned in Week 2", "Status", "Where"],
       ["Lambda A (baseline) and Lambda B (S3 + Rekognition + DynamoDB) behind an HTTP API", "Done, live in ap-south-1", "Sec. 7, Fig. 6"],
       ["E1 cold vs warm, E2 memory 128/256/512/1,024 MB", "Done: 3 functions x 4 sizes, 8 cold + 50 warm each (696 calls)", "Sec. 8.1-8.2"],
       ["E3 concurrency 1/10/50 users for 60 s", "Done at 1/9/50 (quota of 10); 34,775 requests", "Sec. 8.3"],
       ["E4 measured vs modelled cost per 1,000", "Done from 10,954 CloudWatch REPORT lines", "Sec. 8.4"],
       ["SAM template, least-privilege IAM, $5 budget, tags", "Done (template in code/, budget healthy at $0.00)", "App. A"],
       ["Delete stack after measurements", "Changed: paused (throttled) for the live demo; delete after the presentation", "App. B"]],
      [3.0, 2.8, 1.2], "Plan versus delivery")
story.append(PageBreak())

# ================================================================== 1-2 (carried from Week 2)
P("1. Company Background", h1)
P("Shaadi.com was founded by Anupam Mittal in 1996 and is the flagship brand of People Interactive, Mumbai. It is a two-sided "
  "matchmaking platform: value comes from showing each user the right profiles and making it easy for both sides to express "
  "interest, chat and meet. That makes it read-heavy on profiles, write-heavy on interactions, spiky (evenings, weekends, festive "
  "seasons, the 2020 lockdown) and strongly dependent on data science for match quality.")
table([["Indicator", "Value", "Source"], ["Users (2016)", "Over 35 million", "10"], ["Matches made (2016)", "Over 4 million", "4"],
       ["Active profiles (2021)", "Over 3 million", "1"], ["People who found a partner (2022)", "Over 7 million", "2"],
       ["Peak interest requests (Apr 2020)", "2.5 million per day", "1"],
       ["Messaging data (2022)", "320 MySQL tables, about 100,000 new records a day", "2"],
       ["Event records (course headline)", "67 billion - not found in any primary source; not used in any calculation", "-"]],
      [2.4, 3.9, 0.7], "Scale indicators for Shaadi.com")
P("2. Problem Analysis", h1)
P("Each problem is stated as the symptom the business saw, the technical root cause, and the cloud property that addresses it. "
  "P1 and P4 drove the original move to AWS; P2 and P3 appeared later, once the platform was on AWS but still ran a self-managed database tier.")
table([["#", "Symptom", "Root cause", "Cloud property needed"],
       ["P1", "New features and algorithm tests were slow; only 1-2 algorithms per release cycle; business users could not query data themselves.",
        "Hosted private cloud: capacity bought per project, a single dedicated load balancer, reporting only through engineers.",
        "On-demand capacity, managed services, self-service analytics."],
       ["P2", "During the April 2020 lockdown, chats, interests and hourly match campaigns were delayed 10-500 s for about 2 hours a day.",
        "DB3 was bound by CPU, memory and IOPS. On gp2, IOPS are tied to volume size (3 IOPS per GB), so more IOPS meant buying more disk and more nodes.",
        "Elastic storage performance that scales independently of size."],
       ["P3", "Messaging was hard to scale and costly to run.",
        "Relational schema for a key-value access pattern: hot partitions, replica lag, an ORM layer that bottlenecked under spikes.",
        "A purpose-built, horizontally scaling database."],
       ["P4", "New photos waited for manual review before going live.",
        "Human-in-the-loop moderation of every upload; automating it on owned hardware needed new servers.",
        "Pay-per-use ML inference triggered by events."]],
      [0.35, 2.15, 2.6, 1.9], "Problems, root causes and the cloud property each needs")
P("The common thread is coupling: compute coupled to procurement (P1), IOPS coupled to disk size (P2), access pattern coupled "
  "to a relational engine (P3), and throughput coupled to people (P4). Each solution in Section 4 breaks one of these couplings; "
  "our proof of concept tests the serverless answer to P4 directly and the managed-database answer to P3 in miniature.")

# ================================================================== 3 Architecture
P("3. Architecture", h1)
P("3.1 Evolution", h2)
P("Shaadi.com moved in stages rather than in one cut-over. After a Redshift pilot proved that business users could answer their "
  "own questions with SQL, the company migrated everything in about three months, adopting a separate Elastic Load Balancer per "
  "service and managed databases (RDS and Aurora) where performance needs allowed (source 10).")
fig(W2IMG + "f-001.png", "From a hosted private cloud to AWS (sources 4, 6, 10)", 6.6)
table([["Year", "Milestone"], ["2015", "Amazon Redshift pilot for reporting; adopted as the corporate data warehouse"],
       ["Jan-Mar 2016", "Full migration to AWS using AWS DMS; Elasticsearch adds 30% faster search"],
       ["2018", "Serverless photo moderation with AWS Lambda and Amazon Rekognition"],
       ["2020-21", "Lockdown surge on DB3; gp2 to gp3 migration with Elastic Volumes"],
       ["2021-22", "Messaging moved from MySQL to DynamoDB with a strangler-fig migration"]],
      [1.3, 5.7], "Timeline of Shaadi.com's AWS adoption")
P("3.2 Matrimonial portal (three-tier)", h2)
P("Requests reach a public Application Load Balancer and a web tier in an Auto Scaling Group. An internal ALB routes to two "
  "microservices: Back 1 (profiles, photos, favourites) and the Profile API (interests, chat, inbox). The data tier is three MySQL "
  "clusters on EC2, each a primary with a synchronously replicated secondary on EBS volumes. DB3 carries the interaction traffic, "
  "including the hourly match campaigns, and is where the 2020 surge landed (source 1).")
fig(W2IMG + "f-003.png", "Portal architecture, reconstructed from sources 1, 2 and 4", 6.6)
P("3.3 Messaging data layer", h2)
P("To move messaging off MySQL without a risky big-bang switch, the team put a message service in front of both stores. It wrote "
  "to MySQL and DynamoDB at once, client apps were moved to the new API one at a time, reads were switched to DynamoDB, and history "
  "was backfilled: Martin Fowler's strangler-fig pattern (sources 2, 13).")
fig(W2IMG + "f-005.png", "Strangler-fig migration of messaging to DynamoDB (source 2)", 6.0)
P("3.4 Analytics, matching and ML", h2)
P("User events (views, likes, interests, blocks) land in Redshift, which feeds a morning metrics report and a live tracker used to "
  "judge A/B tests in real time (source 10). The data-science team uses this behaviour, together with stated preferences, to build "
  "match algorithms. Photo moderation is a separate, event-driven serverless path: an upload to S3 triggers Lambda, which calls "
  "Rekognition and either approves the photo or sends it to a human (source 3). This path is what our proof of concept rebuilds.")
fig(W2IMG + "f-007.png", "Analytics loop and serverless photo moderation (sources 3, 7, 8, 10)", 6.6)

# ================================================================== 4 Solution analysis
P("4. Solution Analysis", h1)
P("For each major decision: what was chosen, the alternatives available at the time, why the choice fits, its trade-off, and the course concept it illustrates.")
table([["Decision", "Alternatives", "Why it fits", "Trade-off", "Concept"],
       ["Redshift first, then full migration", "Lift everything at once; stay on private cloud", "Low-risk pilot proved value before the big move.", "Two environments for a few months.", "Incremental migration"],
       ["Auto Scaling Groups, one ALB per service", "Shared balancer; fixed fleet", "Each service scales on its own load.", "Needs stateless services and good policies.", "Elasticity"],
       ["gp3 volumes for DB3", "Bigger gp2 disks; io2; more nodes", "IOPS raised 6,000 to 10,000 without buying disk; changed live.", "Still a self-managed MySQL cluster.", "Right-sizing"],
       ["DynamoDB for messaging", "Aurora MySQL; sharded MySQL", "Key-value access; horizontal scale; no servers.", "Access patterns designed up front; AWS API.", "Purpose-built database"],
       ["Provisioned + auto scaling capacity", "On-demand mode", "Predictable daily traffic makes reserved throughput far cheaper.", "Must watch for throttling on spikes.", "Cost optimisation"],
       ["Lambda + Rekognition for photos", "Own GPU servers and model", "No hardware or training; pay per image; runs only when photos arrive.", "Per-image price at scale; black-box model.", "Serverless, managed AI"]],
      [1.35, 1.3, 1.75, 1.45, 1.15], "Design decisions and their trade-offs", fs=7.8)
P("What was not changed is telling: the three portal databases stayed as self-managed MySQL on EC2 even though RDS and Aurora were "
  "in use elsewhere. Likely reasons are control over replication and tuning, and the cost of re-platforming large live clusters. "
  "It meant the 2020 fix had to be done by the team at the storage layer, with help from AWS Enterprise Support.")

# ================================================================== 5 Cost
P("5. Cost and Outcome Analysis", h1)
P("The DB3 figures in source 1 let us go beyond the headline -25%. Dividing monthly cost by monthly interest requests "
  "(daily volume x 30) gives a unit cost that shows how efficiently each design served the load.")
fig(W2IMG + "f-009.png", "DB3 monthly cost and cost per 1,000 interest requests (derived from source 1)", 6.4)
table([["Stage", "Nodes, storage", "Requests/day", "Cost/month", "Per 1,000 requests"],
       ["Before lockdown", "6 x r5.8xlarge, gp2", "1.8 M", "$9,730", "$0.180"],
       ["Scaled on gp2", "8 x r5.8xlarge, gp2 2 TB", "2.5 M", "$13,373", "$0.178 (-1%)"],
       ["After gp3", "6 x r5.8xlarge, gp3 8,000 IOPS", "2.5 M", "$9,963", "$0.133 (-26%)"]],
      [1.4, 2.1, 1.0, 1.0, 1.5], "DB3 unit cost by stage")
P("Scaling out on gp2 kept unit cost flat; the gp3 change broke that link, serving 39% more requests than before the pandemic for "
  "only 2.4% more money. Other outcomes: storage cost -15% and CPU on DB3 secondaries -20% after gp3; DynamoDB messaging at least "
  "60% cheaper and over 40% faster at p50-p95; time for a photo to appear expected to fall 95% with manual review already halved; "
  "more than twice as many algorithms tested at a time (sources 1, 2, 3, 6, 10). Section 8.4 puts our own measured unit costs next "
  "to these: the serverless interest API costs about $0.0019 per 1,000 requests at list prices, against $0.133 for DB3 after gp3 "
  "(not like-for-like: DB3 serves reads, joins and campaigns too, but it shows how little the request path itself costs on serverless).")

# ================================================================== 6 Critical evaluation
P("6. Critical Evaluation", h1)
P("Strengths", h2)
B(["Changes were incremental and reversible (Redshift pilot, DMS, dual writes, in-place volume changes), so a small team migrated a live platform without long outages.",
   "Decisions were driven by measured bottlenecks and unit cost, not by moving everything to the newest service."])
P("Weaknesses and risks", h2)
B(["<b>Vendor lock-in.</b> DynamoDB, Rekognition and Lambda event wiring are AWS-specific; leaving AWS means rewriting the messaging store and the moderation pipeline.",
   "<b>Self-managed hot database.</b> DB3 still needs manual capacity planning. A managed engine (for example Aurora MySQL) is worth evaluating.",
   "<b>Personal data.</b> Profiles, photos and chats are personal data under India's Digital Personal Data Protection Act, 2023. Hosting in Mumbai helps with residency, but consent, retention and breach handling still need controls.",
   "<b>Automated moderation errors.</b> Rekognition can produce false positives and negatives. A confidence threshold with human review for borderline cases, as Shaadi.com kept and as our function implements (60-80% goes to review), is essential.",
   "<b>Serverless limits are real (new, from our experiment).</b> Account concurrency and request-rate quotas throttle a spike before Lambda's scaling does; cold starts add up to 2 s to the first request in each new environment."])
P("Lessons for other startups", h2)
B(["Prove value with one managed service before migrating everything.", "Track unit cost (per request, per user), not only the monthly bill.",
   "Match the database to the access pattern; migrate with dual writes, one app at a time.",
   "Check service quotas before a launch: a new account's defaults can be 100x below the documented ones."])

# ================================================================== 7 Implementation
story.append(CondPageBreak(3*inch))
P("7. Implementation", h1)
P("Course exercise: build a small serverless function with an API trigger and measure cold start and cost per 1,000 requests. "
  "Our version mirrors Shaadi.com's serverless moderation path, adds a baseline function so the cost and latency of the ML call can "
  "be separated from Lambda itself, and keeps the earlier \"send interest\" API as a database-backed middle case.")
fig(FIG + "fig6_architecture_built.png", "Exercise architecture as built (replaces the planned Figure 6 of Week 2)", 6.9)
P("7.1 Components as built", h2)
table([["Component", "Configuration"],
       ["Region, account", "ap-south-1 (Mumbai), same as Shaadi.com. New account: Lambda concurrent-executions quota 10 (default is 1,000)."],
       ["API", "API Gateway HTTP API ypq1jax2t5, $default stage, auto-deploy. Routes: GET / and POST /interest and GET /interest/{id} (interest API), GET /baseline (Lambda A), POST /moderate (Lambda B)."],
       ["Lambda A: shaadi-ping", "Python 3.15, 128 MB default. Returns {\"pong\": true, \"coldStart\": ...}; no AWS SDK or network calls. Role: logs only."],
       ["Interest API: shaadi-interest-api", "Python 3.15 + boto3. Writes an interest item (UUID key) to DynamoDB table Interests. Role: PutItem/GetItem on that table only."],
       ["Lambda B: shaadi-moderate", "Python 3.15 + boto3, 512 MB, 10 s timeout. Reads imageKey, calls DetectModerationLabels on the S3 object (min confidence 60), verdict = rejected if a label is at least 80%, review if any label, else approved; stores verdict, labels and Rekognition time in DynamoDB table verdicts. Role: s3:GetObject on photos/*, rekognition:DetectModerationLabels, dynamodb:PutItem on verdicts."],
       ["Harness: shaadi-loadgen", "Python 3.15, 1,024 MB, 15 min timeout, invoked from the console. Forces cold starts (changes memory and an env var), fires a synchronised burst, runs warm calls and timed load, queries Logs Insights, writes CSVs to s3://.../results/. Role: Get/UpdateFunctionConfiguration on the three functions, logs:StartQuery/GetQueryResults, s3:PutObject on results/*."],
       ["Storage", "S3 bucket it457-g47-shaadi-705029438856 (Block Public Access on) with 30 synthetic 640x480 JPEG test images in photos/. DynamoDB tables Interests and verdicts, on-demand."],
       ["Infrastructure as code", "code/template.yaml (AWS SAM) describes the whole stack, including the budget and tags, for one-command re-creation (sam build && sam deploy). The live stack itself was built in the console because CloudShell is unavailable while account verification is pending."],
       ["Guardrails", "AWS Budgets alert it457-g47-5usd ($5/month, email); tag project=it457-g47 on functions, bucket, tables and log groups; functions throttled (reserved concurrency 0) between sessions."]],
      [1.6, 5.4], "Components and configuration as built", fs=7.9, keep=False)
P("7.2 Deviations from the Week 2 plan", h2)
table([["Planned", "Done instead", "Reason and effect"],
       ["k6 on a laptop for load tests", "shaadi-loadgen Lambda in the same region", "No local tooling or CloudShell on the account; an in-region client also removes home-network noise. Client latency now means AWS-internal network + API Gateway + Lambda."],
       ["10 cold starts per level", "Bursts of 8 simultaneous calls (7-8 cold each)", "Concurrency quota 10, one slot used by the harness. 95 cold starts in total across 12 configurations."],
       ["Concurrency 1 / 10 / 50", "1 / 9 / 50", "Same quota; the 50-user level was kept to show throttling, which became a main finding."],
       ["GET /ping", "GET /baseline", "API Gateway reserves /ping for its own health check and replies \"Healthy Connection\" without calling Lambda (documented for REST/WebSocket APIs; we observed it on an HTTP API)."],
       ["Python 3.12", "Python 3.15", "Newest runtime offered in the console in November 2026."],
       ["Stock or own photos", "30 synthetic images", "Avoids uploading personal photos; side effect: every verdict is 'approved' (no labels), so accuracy is not evaluated."],
       ["Delete stack after measuring", "Pause (throttle) and keep", "Needed for the live demo; Appendix B lists restart and deletion steps."]],
      [1.35, 1.75, 3.9], "Deviations from the plan and their effect", fs=7.9)
P("7.3 Method", h2)
P("<b>E1/E2 (cold vs warm, memory).</b> For each of the 3 functions and each memory size (128, 256, 512, 1,024 MB) the harness "
  "changed MemorySize and a RUN_NONCE environment variable, waited for the update, then fired 8 requests released together by a "
  "thread barrier (all need a new execution environment) followed by 50 sequential requests (warm). Each response carries the "
  "function's own <i>coldStart</i> flag, so cold and warm are labelled by the function, not guessed. "
  "<b>E3 (concurrency).</b> 1, 9 and 50 virtual users each called GET /baseline in a closed loop for 60 s at 512 MB. "
  "<b>E4 (cost).</b> Logs Insights returned every REPORT line (Init Duration, Duration, Billed Duration, Max Memory Used); cost "
  "per 1,000 requests = 1,000 x (billed GB-s x $0.0000166667 + $0.20/M + $1.00/M API + per-request service charges), at the same "
  "US East list prices as the Week 2 model (Lambda's x86 prices are the same in Mumbai; the pricing pages render other regional "
  "prices dynamically, so they could not be confirmed in text).")

# ================================================================== 8 Results
story.append(CondPageBreak(4*inch))
P("8. Results", h1)
P("8.1 E1 and E2: cold versus warm, by memory", h2)
fig(FIG + "fig7_cold_warm.png", "Client-side latency (median) of cold and warm calls, 8 cold + 50 warm per bar pair, log scale", 6.9)
rows = [["Function", "Memory", "Cold starts", "Cold p50 (ms)", "Warm p50 (ms)", "Warm p95 (ms)", "Cold / warm"]]
import csv
for r in csv.DictReader(open("/home/claude/poc/data/run2/coldwarm_summary_console.csv")):
    name = {"ping": "A: baseline", "interest": "Interest API", "moderate": "B: moderation"}[r["target"]]
    rows.append([name, r["memory_mb"], f'{r["cold_starts"]} of 8', f'{float(r["cold_p50_ms"]):,.0f}', f'{float(r["warm_p50_ms"]):.1f}',
                 f'{float(r["warm_p95_ms"]):.1f}', f'{float(r["cold_p50_ms"]) / float(r["warm_p50_ms"]):.0f}x'])
table(rows, [1.4, 0.75, 0.9, 1.0, 1.0, 1.0, 0.95], "E1/E2 client latency, run 20261112T194523 (all 696 calls returned 200/201; p50 = nearest-rank percentile)")
P("A warm call to the empty function costs about 18 ms end to end, which is the floor set by API Gateway and the network inside "
  "the region; memory makes no difference to it. Cold calls are where memory matters for code that does work at start-up: the "
  "interest API's cold median fell from 1,950 ms at 128 MB to 699 ms at 1,024 MB because Lambda allocates CPU in proportion to "
  "memory, and importing boto3 and opening TLS connections is CPU-bound. The moderation function's warm time is dominated by the "
  "Rekognition call (median 151-171 ms of the 173-202 ms), so memory hardly changes it. Each warm series also had one or two "
  "outliers of 0.9-1.8 s in Rekognition itself, which is why its p95 is noisy.")
P("8.2 Inside a cold start (CloudWatch)", h2)
fig(FIG + "fig8_init_breakdown.png", "Server-side cold call = Init Duration + handler time, against the billed time of a warm call (medians/means from REPORT lines)", 6.9)
table([["Function", "Memory", "Init p50", "Cold handler p50", "Cold billed p50", "Warm billed mean", "Max memory used"],
       ["A: baseline", "128 / 1,024", "116 / 115 ms", "1.8 / 1.7 ms", "118 / 117 ms", "2.1 / 2.0 ms", "35 MB"],
       ["Interest API", "128 / 1,024", "1,242 / 502 ms", "552 / 65 ms", "1,831 / 569 ms", "38.0 / 7.4 ms", "95 MB"],
       ["B: moderation", "128 / 1,024", "1,320 / 1,207 ms", "649 / 239 ms", "1,954 / 1,447 ms", "237.8 / 214.7 ms", "97-100 MB"],
       ["B: moderation", "256 / 512", "428 / 642 ms", "402 / 282 ms", "866 / 924 ms", "209.2 / 188.7 ms", "97-100 MB"]],
      [1.15, 0.85, 1.05, 1.05, 1.05, 1.0, 0.85], "Server-side figures from 10,954 REPORT lines (Logs Insights, run 20261112T195330)", fs=7.9)
P("Three points stand out. First, the billed time of every cold call equals Init plus handler time, so a cold start is now paid "
  "for, not just waited for. Second, for the SDK-using functions the first handler call is also slow (552 ms at 128 MB) because "
  "clients and connections are created lazily; only the empty baseline has a cheap first call. Third, Init Duration for the "
  "moderation function did not fall monotonically with memory (median 428 ms at 256 MB but 1,207 ms at 1,024 MB); with 8 samples "
  "per level, start-up is dominated by variable work such as fetching the runtime and loading boto3 rather than by CPU alone, so "
  "small samples should be read as ranges. Every function used under 100 MB, so 128 MB is enough memory-wise; any extra memory is "
  "bought for CPU.")
P("8.3 E3: concurrency and throttling", h2)
fig(FIG + "fig10_concurrency.png", "60-second closed-loop load on GET /baseline at 512 MB: served vs rejected requests and latency over time", 6.9)
table([["Virtual users", "Requests", "HTTP 200", "HTTP 503", "Served req/s", "p50 / p95 / p99 of 200s (ms)", "Cold starts"],
       ["1", "3,969", "3,969", "0 (0%)", "66.2", "14.7 / 17.7 / 20.7", "1"],
       ["9", "15,983", "5,936", "10,047 (63%)", "98.9", "38.3 / 50.9 / 56.2", "8"],
       ["50", "14,823", "6,044", "8,779 (59%)", "100.7", "197.5 / 315.7 / 380.9", "0"]],
      [0.85, 0.75, 0.75, 1.0, 0.85, 1.75, 0.75], "E3 results, run 20261112T194909 (34,775 requests)")
P("With one user the function served 66 requests per second at a 15 ms median and no errors. From 9 users upward, served "
  "throughput stopped at about 100 requests per second however much load was offered, and the rest came back as HTTP 503 from "
  "API Gateway. CloudWatch showed peak concurrent executions of 9 and up to 8,581 throttles per minute (Appendix C). The ceiling "
  "matches the documented rule that Lambda limits requests per second to 10 times the account's concurrency quota (source 15): "
  "10 x 10 = 100. Because the function runs for under 2 ms, concurrency itself was never the bottleneck; the request-rate quota "
  "was. At 50 users the higher latency of successful calls (198 ms median) is mostly queueing inside the single harness function "
  "(50 threads on one 1,024 MB environment), so we read that level for throughput, not latency.")
P("8.4 E4: cost per 1,000 requests, measured versus modelled", h2)
table([["Item (per 1,000 warm requests)", "A: baseline, 128 MB", "Interest API, 512 MB", "B: moderation, 512 MB"],
       ["Lambda compute (measured billed time)", "$0.0000043 (2.1 ms)", "$0.0000578 (6.9 ms)", "$0.0015727 (188.7 ms)"],
       ["Lambda requests ($0.20/M)", "$0.0002", "$0.0002", "$0.0002"],
       ["API Gateway HTTP API ($1.00/M)", "$0.0010", "$0.0010", "$0.0010"],
       ["DynamoDB write ($0.625/M WRU)", "-", "$0.000625", "$0.000625"],
       ["Rekognition ($0.001/image) + S3 GET", "-", "-", "$1.0000 + $0.0004"],
       ["<b>Total measured</b>", "<b>$0.0012</b>", "<b>$0.0019</b>", "<b>$1.0038</b>"],
       ["Week 2 model", "$0.0012", "(not modelled)", "$1.007 (assumed 600 ms)"],
       ["Extra cost of one cold start", "$0.00000026", "$0.0000072", "$0.0000070"]],
      [2.2, 1.5, 1.5, 1.8], "Measured cost per 1,000 requests at list prices (Week 2 Table 7 for comparison)", fs=7.9)
fig(FIG + "fig9_compute_cost.png", "Lambda compute cost per 1,000 warm calls against memory: linear for I/O-bound functions, U-shaped for the CPU-bound interest API", 5.2)
P("The Week 2 model is confirmed in shape and close in value. Its two predictions both held: (1) Lambda itself is almost free at "
  "this scale, since the API Gateway request charge ($0.001) is larger than all Lambda charges for the baseline and the interest "
  "API; (2) for the moderation function, which waits on Rekognition, more memory raises cost without lowering latency (compute "
  "cost $0.0005 at 128 MB rising to $0.0036 at 1,024 MB for a 14% faster warm call). The model over-estimated Lambda B's duration "
  "(600 ms assumed, 189 ms measured), but that changes the total by less than 0.4% because Rekognition is 99.6% of it. A cold "
  "start adds well under a thousandth of a cent, so its cost matters only at Shaadi.com scale, while its latency matters to every user who hits one.")
P("8.5 What the experiment actually cost", h2)
P("About 17,500 Lambda invocations (another 18,826 requests were throttled before reaching Lambda), about 53,000 API Gateway "
  "requests, 236 Rekognition calls and under 1,000 DynamoDB writes: roughly $0.30 at list prices, most of it Rekognition; it is covered by the account's credits and free tier. AWS Budgets reported $0.00 actual spend for the month "
  "with the $5 alert healthy (screenshot 07). While paused, the only standing charges are S3 and DynamoDB storage of under 2 MB.")

# ================================================================== 9 Discussion
P("9. Discussion: what this means for Shaadi.com", h1)
B(["<b>Serverless fits the moderation path.</b> The pipeline's cost is set by the ML call, not by the compute around it, which is "
   "exactly the trade Shaadi.com made: no GPU servers, pay per photo. At 1 million photos a month the Lambda part is about $1.60 "
   "against $1,000 for Rekognition list price, so savings come from calling Rekognition less (resizing, skipping duplicates, volume pricing), not from tuning Lambda.",
   "<b>Size memory by what the function waits for.</b> CPU-bound start-up (the interest API) benefits up to 512-1,024 MB; an "
   "I/O-bound function (moderation) should run at 128-256 MB. AWS Lambda Power Tuning automates this sweep.",
   "<b>Plan for cold starts on user-facing paths.</b> A 1-2 s first response on \"send interest\" would be noticeable on mobile. "
   "Provisioned concurrency on the hot path, SnapStart for Python, keeping imports light and initialising SDK clients at module level "
   "are the standard options; moderation is asynchronous, so it can absorb cold starts.",
   "<b>Quotas and buffering decide spike behaviour.</b> The 2020 lockdown surge (+58%) hit DB3; on serverless the equivalent failure "
   "is throttling. The production design should trigger moderation from S3 events through an SQS queue (retries instead of 503s), "
   "request quota increases ahead of festive peaks, and alarm on the Throttles metric."])

# ================================================================== 10 Limitations
P("10. Limitations", h1)
B(["Eight cold starts per configuration give stable medians but wide tails; percentiles above p95 for cold calls are not reliable.",
   "The test images are synthetic, so every verdict was 'approved'; the false-positive and false-negative behaviour discussed in Section 6 was not measured.",
   "The account's quota of 10 limited E3; results show the behaviour of a new account, not of Lambda at production quotas.",
   "Client latency was measured from inside AWS (the harness); real users on mobile networks would see an extra 30-150 ms per call.",
   "Prices are list prices without free tier or credits; the CloudWatch export for the baseline function was capped at 10,000 lines, "
   "covering E1/E2 and the 1- and 9-user runs (the 50-user run is covered by client data and the Lambda metrics)."])

# ================================================================== 11 Roles + Conclusion
P("11. Team Roles", h1)
table([["Member", "Analysis phase (Weeks 1-2)", "Implementation and results"],
       ["Sri Sai Madhava Teja Yanduri (202301138)", "Sections 1, 2, 4, 6; editing; source checks", "Results write-up, measured vs modelled cost, discussion, final report"],
       ["Kavya Chauhan (202301116)", "Exercise design; AWS account and region checks", "Functions, IAM policies, API routes, SAM template, E1-E3 runs, pause/restart"],
       ["Venkata L Subramanyam (202301280)", "Figures 1-5; Section 3; Section 5 cost analysis", "Logs Insights queries, charts (Figures 6-10), workbook, cost per 1,000"]],
      [2.0, 2.3, 2.7], "Roles of team members")
P("12. Conclusion", h1)
P("Shaadi.com's AWS story is one of breaking couplings one at a time, and our proof of concept reproduces the serverless part of it "
  "with numbers. A three-function serverless stack in Mumbai answered warm requests in 18-200 ms for between a tenth of a cent and "
  "one dollar per thousand, with the dollar almost entirely the managed ML call. The costs of serverless that the case material does "
  "not show are equally clear in our data: cold starts of up to 2 s that are now billed, and quota limits that turn a spike into "
  "503 errors well before any server would be busy. Both are manageable with memory sizing, provisioned concurrency, queues and "
  "quota planning, and both belong in any startup's decision to go serverless.")

# ================================================================== References
P("References", h1)
refs = [
    "AWS Storage Blog, How Shaadi.com optimized compute costs using Amazon EBS gp3 volumes, Aug 2021. https://aws.amazon.com/blogs/storage/how-shaadi-com-optimized-compute-costs-using-amazon-ebs-gp3-volumes/",
    "AWS Database Blog, How Shaadi.com reduced costs and improved performance with DynamoDB, 19 May 2022. https://aws.amazon.com/blogs/database/how-shaadi-com-reduced-costs-and-improved-performance-with-dynamodb/",
    "AWS Machine Learning Blog, Amazon Rekognition is now available in the Asia Pacific (Seoul) and Asia Pacific (Mumbai) Regions, Aug 2018.",
    "AWS News Blog, Hot Startups on AWS - June 2016 - Shaadi.com, Capillary, Mondo, 2016. https://aws.amazon.com/blogs/aws/hot-startups-on-aws-june-2016-shaadi-com-capillary-mondo/",
    "Shaadi.com Engineering Blog. https://tech.shaadi.com",
    "PCQuest, Shaadi.com: Tech 4 Match Making, Nov 2018. https://www.pcquest.com/shadi-com-tech-4-match-making/",
    "FactorDaily, Marriages made in heaven with a little help from Bayes. https://archive.factordaily.com/all-about-that-bayes/",
    "Udayavani / PTI, AI helping matrimony sites suggest match, Mar 2019.",
    "CaseStudies.com, Shaadi.com customer index. https://www.casestudies.com/customer/shaadicom",
    "Amazon Web Services, Matchmaking Site Shaadi.com Doubles Algorithm Testing Using AWS (customer case study, 2016), copy at https://cdn.featuredcustomers.com/CustomerCaseStudy.document/shaadi.pdf",
    "AWS Lambda pricing; Amazon API Gateway pricing; Amazon Rekognition pricing; Amazon DynamoDB on-demand pricing. https://aws.amazon.com/pricing/ (accessed 13 Nov 2026)",
    "AWS Compute Blog, AWS Lambda standardizes billing for INIT phase, 2025. https://aws.amazon.com/blogs/compute/aws-lambda-standardizes-billing-for-init-phase/",
    "M. Fowler, Strangler Fig Application. https://martinfowler.com/bliki/StranglerFigApplication.html",
    "Amazon API Gateway Developer Guide, Amazon API Gateway important notes (reserved /ping and /sping paths). https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-known-issues.html",
    "AWS Lambda Developer Guide, Understanding Lambda function scaling (concurrency quota; requests per second = 10 x concurrency). https://docs.aws.amazon.com/lambda/latest/dg/lambda-concurrency.html",
    "Group 47 measurement data: code/, data/ and screenshots/ folders of this submission; raw CSVs in s3://it457-g47-shaadi-705029438856/results/.",
]
for i, r in enumerate(refs, 1):
    story.append(Paragraph(r, ParagraphStyle("r", parent=small, leftIndent=18, firstLineIndent=-18, spaceAfter=3), bulletText=None))
    story[-1].text = f"{i}.&nbsp;&nbsp;" + story[-1].text if False else story[-1].text
story[-len(refs):] = [Paragraph(f"{i}.&nbsp;&nbsp;{r}", ParagraphStyle("r", parent=small, leftIndent=18, firstLineIndent=-18, spaceAfter=3)) for i, r in enumerate(refs, 1)]
P("Sources 1-13 accessed 21-27 October 2026; 11, 14, 15 re-checked 13 November 2026.", small)

# ================================================================== Appendix A
story.append(PageBreak())
P("Appendix A. Requirement checklist", h1)
table([["Requirement (course guide / Week 2 plan)", "Evidence", "Status"],
       ["Case study: background, problems, architecture, solution analysis, cost, critique", "Sections 1-6, Figures 1-5, Tables 2-6", "Done"],
       ["Serverless function with an API trigger", "Lambda A/B behind HTTP API; screenshots 08, 09, 11", "Done"],
       ["Measure cold start", "Sections 8.1-8.2; data/run2/coldwarm_raw.csv, cloudwatch_report_summary.csv", "Done"],
       ["Measure cost per 1,000 requests", "Section 8.4, Table 12; workbook sheet Cost_Model (live formulas)", "Done"],
       ["E1 cold vs warm (A and B)", "Table 9 (plus the interest API)", "Done"],
       ["E2 memory 128/256/512/1,024 MB", "Figures 7, 8 and 10; Tables 9-10", "Done"],
       ["E3 concurrency 1/10/50, 60 s", "Figure 9, Table 11 (1/9/50 because of quota)", "Done, adapted"],
       ["E4 measured vs modelled cost", "Table 14", "Done"],
       ["Region ap-south-1, least-privilege IAM per function", "Table 7; code/iam_policy_*.json", "Done"],
       ["AWS SAM template", "code/template.yaml (validated YAML; stack built in console)", "Done"],
       ["Budget alert at $5; tags project=it457-g47", "Screenshot 07; Resource Explorer tagging", "Done"],
       ["Stack deleted after measurements", "Paused instead, for the live demo; deletion steps in Appendix B", "After demo"],
       ["Team roles", "Section 11", "Done"],
       ["References", "16 sources", "Done"]],
      [2.9, 3.1, 1.0], "Checklist against the implementation guide and the Week 2 plan", fs=7.9)

# ================================================================== Appendix B
P("Appendix B. Demo, restart and clean-up", h1)
P("<b>Restart on presentation day (about 1 minute).</b> In the Lambda console (ap-south-1), open each of shaadi-ping, "
  "shaadi-interest-api and shaadi-moderate, choose Configuration > Concurrency > Edit, select <i>Use unreserved account concurrency</i> "
  "and save. Leave shaadi-loadgen throttled unless an experiment is to be re-run. Then open "
  "https://ypq1jax2t5.execute-api.ap-south-1.amazonaws.com/baseline in a browser: the first response shows \"coldStart\": true, "
  "a refresh shows false.")
P("<b>Demo calls.</b> curl -X POST .../interest -d '{\"from\":\"demo\",\"to\":\"user_42\",\"message\":\"Hello\"}' returns 201 and the stored item; "
  "curl -X POST .../moderate -d '{\"imageKey\":\"photos/photo_07.jpg\"}' returns the verdict and the Rekognition time; the new "
  "items appear in DynamoDB tables Interests and verdicts. To show a cold start live, change any environment variable of a function and call it again.")
P("<b>Re-run an experiment.</b> Un-throttle shaadi-loadgen and run a console test event such as "
  "{\"mode\": \"coldwarm\", \"targets\": [\"ping\"], \"memories\": [128, 1024], \"burst\": 8, \"warm\": 50}; results land in s3://.../results/.")
P("<b>Pause again.</b> Choose Throttle on each function (sets reserved concurrency to 0); every route then returns HTTP 503.")
P("<b>Delete after grading.</b> Delete the four functions, the HTTP API, the tables Interests and verdicts, empty and delete the "
  "bucket, delete the /aws/lambda/shaadi-* log groups, the four IAM roles and the budget. If the stack is recreated from "
  "code/template.yaml, a single <i>sam delete</i> removes everything.")

# ================================================================== Appendix C screenshots
story.append(PageBreak())
P("Appendix C. Selected evidence (all screenshots are in screenshots/)", h1)
shots = [("08_lambda_functions_4.jpg", "The four functions in ap-south-1, all on Python 3.15"),
         ("11_live_api_responses.jpg", "Live calls to the three routes: baseline (warm), interest API (cold, 201 Created) and moderation verdict with Rekognition time"),
         ("13_ping_throttles_concurrency.jpg", "shaadi-ping metrics during E3: concurrent executions peak at 9, up to 8,581 throttles per minute, zero errors in the function"),
         ("10_dynamodb_verdicts.jpg", "Verdicts written by Lambda B to DynamoDB, with the coldStart flag and Rekognition time per photo"),
         ("12_s3_results.jpg", "Result CSVs written by the harness to s3://it457-g47-shaadi-705029438856/results/"),
         ("07_budget_5usd.jpg", "AWS Budgets: $5 monthly alert, $0.00 spent, healthy")]
for f, c in shots:
    fig(SHOT + f, c, 6.3, maxh=3.6)

doc.build(story)
print("built", OUT)
