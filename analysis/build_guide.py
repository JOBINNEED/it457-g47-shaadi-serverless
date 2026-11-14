"""IT-457 Group 47 - complete project study guide (everything needed to explain the project)."""
import csv
import json
import textwrap

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Frame, Image, KeepTogether, PageBreak, PageTemplate,
                                Paragraph, Preformatted, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

LIB = "/usr/share/fonts/truetype/liberation/"
for n, f in [("Sans", "Regular"), ("Sans-B", "Bold"), ("Sans-I", "Italic"), ("Sans-BI", "BoldItalic")]:
    pdfmetrics.registerFont(TTFont(n, LIB + f"LiberationSans-{f}.ttf"))
pdfmetrics.registerFont(TTFont("Mono", LIB + "LiberationMono-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Mono-B", LIB + "LiberationMono-Bold.ttf"))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-B", italic="Sans-I", boldItalic="Sans-BI")
pdfmetrics.registerFontFamily("Mono", normal="Mono", bold="Mono-B", italic="Mono", boldItalic="Mono-B")

SUB = "/home/claude/final/IT457_G47_Final_Submission/"
CODE = SUB + "code/"
W2 = "/home/claude/wk2/img/"
FIG = "/home/claude/final/fig/"
SHOT = "/home/claude/poc/screenshots/"
OUT = "/home/claude/guide/IT457_G47_Project_Complete_Guide.pdf"

INK = colors.HexColor("#1f2933")
ACC = colors.HexColor("#1F4E78")
body = ParagraphStyle("b", fontName="Sans", fontSize=9.6, leading=13.4, spaceAfter=5, textColor=INK)
small = ParagraphStyle("s", parent=body, fontSize=8.3, leading=10.8, spaceAfter=0)
smallb = ParagraphStyle("sb", parent=small, fontName="Sans-B")
h1 = ParagraphStyle("h1", fontName="Sans-B", fontSize=17, leading=21, spaceBefore=4, spaceAfter=8, textColor=ACC)
h2 = ParagraphStyle("h2", fontName="Sans-B", fontSize=12, leading=15.5, spaceBefore=9, spaceAfter=4, textColor=INK)
h3 = ParagraphStyle("h3", fontName="Sans-B", fontSize=10.2, leading=13.5, spaceBefore=6, spaceAfter=3, textColor=ACC)
cap = ParagraphStyle("c", fontName="Sans-I", fontSize=8, leading=10, textColor=colors.HexColor("#555555"),
                     alignment=TA_CENTER, spaceBefore=3, spaceAfter=9)
bul = ParagraphStyle("bu", parent=body, leftIndent=14, bulletIndent=3, spaceAfter=2.5)
mono = ParagraphStyle("m", fontName="Mono", fontSize=6.9, leading=8.6, textColor=colors.HexColor("#111111"))
qst = ParagraphStyle("q", parent=body, fontName="Sans-B", spaceAfter=1.5, spaceBefore=4)

story = []
cnt = {"t": 0, "f": 0}


class Doc(BaseDocTemplate):
    def afterFlowable(self, fl):
        if isinstance(fl, Paragraph) and fl.style.name in ("h1", "h2"):
            lvl = 0 if fl.style.name == "h1" else 1
            key = f"k{id(fl)}"
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(fl.getPlainText(), key, level=lvl, closed=lvl > 0)
            self.notify("TOCEntry", (lvl, fl.getPlainText(), self.page, key))


def P(t, s=body):
    if s in (h2, h3):
        story.append(CondPageBreak(1.2 * inch))
    story.append(Paragraph(t, s))


def H1(t):
    story.append(PageBreak())
    story.append(Paragraph(t, h1))


def B(items, style=bul):
    for t in items:
        story.append(Paragraph(t, style, bulletText="•"))


def N(items):
    for i, t in enumerate(items, 1):
        story.append(Paragraph(t, bul, bulletText=f"{i}."))


def T(rows, widths, text=None, fs=8.2, header=True, zebra=False):
    st_cell = ParagraphStyle("x", parent=small, fontSize=fs, leading=fs + 2.4)
    data = [[Paragraph(str(c), smallb if (header and i == 0) else st_cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * inch for w in widths], repeatRows=1 if header else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8C8C8")),
          ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#8a8a8a")), ("TOPPADDING", (0, 0), (-1, -1), 3),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("LEFTPADDING", (0, 0), (-1, -1), 4)]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E3EAF2")), ("LINEBELOW", (0, 0), (-1, 0), 0.9, ACC)]
    t.setStyle(TableStyle(st))
    if text:
        cnt["t"] += 1
        story.append(KeepTogether([t, Paragraph(f"Table {cnt['t']}: {text}", cap)]) if len(rows) < 18 else t)
        if len(rows) >= 18:
            story.append(Paragraph(f"Table {cnt['t']}: {text}", cap))
    else:
        story.append(t)
        story.append(Spacer(1, 6))


def F(path, text, width=6.8, maxh=None):
    w, h = PILImage.open(path).size
    ww, hh = width * inch, width * inch * h / w
    if maxh and hh > maxh * inch:
        hh = maxh * inch
        ww = hh * w / h
    cnt["f"] += 1
    story.append(KeepTogether([Image(path, width=ww, height=hh), Paragraph(f"Figure {cnt['f']}: {text}", cap)]))


def box(title, lines, color="#EEF4FA", edge=ACC):
    inner = [Paragraph(f"<b>{title}</b>", ParagraphStyle("bt", parent=body, textColor=edge, spaceAfter=3))]
    for l in lines:
        inner.append(Paragraph(l, ParagraphStyle("bl", parent=body, fontSize=9.2, leading=12.6, spaceAfter=3)))
    t = Table([[inner]], colWidths=[7 * inch])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(color)), ("BOX", (0, 0), (-1, -1), 0.8, edge),
                           ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(t)
    story.append(Spacer(1, 8))


def code(text, title=None, wrap=112, numbers=True):
    lines = []
    for i, line in enumerate(text.rstrip("\n").split("\n"), 1):
        parts = textwrap.wrap(line, wrap, subsequent_indent="      ", drop_whitespace=False, replace_whitespace=False) or [""]
        for j, p in enumerate(parts):
            pre = f"{i:>3} " if (numbers and j == 0) else ("    " if numbers else "")
            lines.append(pre + p)
    chunk = 70
    blocks = [lines[k:k + chunk] for k in range(0, len(lines), chunk)]
    for n, bl in enumerate(blocks):
        pf = Preformatted("\n".join(bl), mono)
        t = Table([[pf]], colWidths=[7 * inch])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F6F8FA")),
                               ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#C9D1D9")),
                               ("LEFTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 5),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        if title and n == 0:
            story.append(Paragraph(f"<font name='Mono-B' size='8'>{title}</font>", ParagraphStyle("ct", parent=small, spaceAfter=2)))
        story.append(t)
    story.append(Spacer(1, 7))


def explain(rows):
    T([["Lines", "What they do and why"]] + rows, [0.75, 6.25], None, fs=8.3)


def QA(q, a):
    story.append(KeepTogether([Paragraph("Q. " + q, qst), Paragraph(a, ParagraphStyle("a", parent=body, leftIndent=12))]))


def page(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setFont("Sans", 7.5)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(0.75 * inch, 10.62 * inch, "IT-457 Group 47  |  Shaadi.com serverless project")
        canvas.drawRightString(7.75 * inch, 10.62 * inch, "Complete project guide")
        canvas.setStrokeColor(colors.HexColor("#C8C8C8"))
        canvas.line(0.75 * inch, 10.56 * inch, 7.75 * inch, 10.56 * inch)
        canvas.drawCentredString(4.25 * inch, 0.5 * inch, str(doc.page))
    canvas.restoreState()


def read(p):
    return open(p).read()


# ====================================================================================== COVER
story.append(Spacer(1, 1.4 * inch))
story.append(Paragraph("The Complete Project Guide", ParagraphStyle("t", fontName="Sans-B", fontSize=28, leading=34, alignment=TA_CENTER, textColor=ACC)))
story.append(Paragraph("IT-457 Cloud Computing | Case Study Project | Group 47",
                       ParagraphStyle("t2", fontName="Sans", fontSize=13, leading=18, alignment=TA_CENTER, spaceBefore=8)))
story.append(Paragraph("Shaadi.com on AWS, and a serverless proof of concept built, measured and costed in ap-south-1 (Mumbai)",
                       ParagraphStyle("t3", fontName="Sans-I", fontSize=11, leading=15, alignment=TA_CENTER, spaceBefore=10, textColor=colors.HexColor("#444"))))
story.append(Spacer(1, 0.5 * inch))
story.append(Paragraph("Everything in one place: the case, the cloud concepts, every tool, every line of code with its explanation, "
                       "how the system was built step by step, what broke and how it was fixed, the experiments, the numbers and "
                       "what they mean, the cost arithmetic, a demo script and a bank of likely questions with answers.",
                       ParagraphStyle("t4", parent=body, alignment=TA_CENTER, fontSize=10.5, leading=15)))
story.append(Spacer(1, 0.6 * inch))
cov = [["Name", "Student ID"], ["Sri Sai Madhava Teja Yanduri", "202301138"], ["Kavya Chauhan", "202301116"], ["Venkata L Subramanyam", "202301280"]]
t = Table([[Paragraph(c, smallb if i == 0 else small) for c in r] for i, r in enumerate(cov)], colWidths=[2.6 * inch, 1.3 * inch])
t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.8, colors.black), ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.grey),
                       ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E3EAF2")), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
story.append(t)
story.append(Spacer(1, 0.9 * inch))
story.append(Paragraph("Companion to the final report (202301138_IT457_Group47_Final_Report.pdf). Measurements: 12-13 November 2026.",
                       ParagraphStyle("cv", parent=small, alignment=TA_CENTER, textColor=colors.HexColor("#666"))))

# ====================================================================================== TOC
story.append(PageBreak())
story.append(Paragraph("Contents", ParagraphStyle("h1c", parent=h1)))
toc = TableOfContents()
toc.levelStyles = [ParagraphStyle("l0", fontName="Sans-B", fontSize=9.6, leading=13, leftIndent=0, spaceBefore=3),
                   ParagraphStyle("l1", fontName="Sans", fontSize=8.6, leading=11, leftIndent=16)]
story.append(toc)

# ====================================================================================== 0. HOW TO USE
H1("0. How to use this guide")
P("Read Sections 1-2 first: they give you the whole story in a few minutes. Sections 3-5 are the background knowledge "
  "(the case and the cloud concepts) that every answer builds on. Sections 6-9 explain exactly what we built and every line of "
  "code. Sections 10-13 are the experiments, the numbers and the cost arithmetic. Sections 14-17 are for the presentation itself: "
  "problems and fixes, limitations, the demo script, and about fifty questions with model answers.")
box("The 60-second pitch (memorise this)", [
    "\"Our case is Shaadi.com, India's largest matrimony site, which moved from a hosted private cloud to AWS and later put its "
    "photo moderation on serverless: S3, Lambda and Amazon Rekognition. We analysed why they moved, what they built and what it saved. "
    "Then we rebuilt the serverless part ourselves in the same AWS region, Mumbai: an HTTP API in front of three Lambda functions. "
    "One does nothing (a baseline), one writes an 'interest' to DynamoDB like the real portal, and one sends a photo from S3 to "
    "Rekognition and stores the verdict.\"",
    "\"We measured four things. Cold starts cost 10 to 60 times a warm call and are now billed. More memory speeds up CPU-bound "
    "start-up but not waiting on Rekognition, so it only raises cost there. Per thousand requests the baseline costs about a tenth of a cent "
    "and moderation about a dollar, 99.6% of it Rekognition. And our account's quota, not Lambda, capped us at 100 requests per second; "
    "beyond that, 60% of requests were throttled with HTTP 503. So serverless is cheap and elastic, but cold starts and quotas have to be planned for.\""],
    color="#FFF8E6", edge=colors.HexColor("#B7791F"))
P("Numbers you should know by heart", h2)
T([["Fact", "Value"],
   ["Region", "ap-south-1, Asia Pacific (Mumbai): same region as Shaadi.com"],
   ["Warm latency (client, median)", "Baseline 18 ms; interest API 24-32 ms; moderation 173-202 ms"],
   ["Cold latency (client, p50)", "Baseline 217-493 ms; interest API 699-1,950 ms; moderation 1,000-2,071 ms"],
   ["Init Duration (CloudWatch, p50)", "Baseline about 93-116 ms; interest API 502-1,242 ms; moderation 428-1,320 ms"],
   ["Cost per 1,000 requests", "Baseline $0.0012; interest API $0.0019; moderation $1.0038"],
   ["Biggest cost item", "Rekognition: $1.00 per 1,000 images = 99.6% of the moderation cost"],
   ["Throughput ceiling", "About 100 requests/second = 10 x our concurrency quota of 10"],
   ["Throttled share at 9 and 50 users", "63% and 59% (HTTP 503)"],
   ["Calls measured", "696 cold/warm calls; 34,775 load-test requests; 10,954 CloudWatch REPORT lines"],
   ["Money spent", "Roughly $0.30 at list price (covered by credits); Budgets shows $0.00; $5 alert set"],
   ["API base URL", "https://ypq1jax2t5.execute-api.ap-south-1.amazonaws.com"]],
  [2.2, 4.8], "Key facts")

# ====================================================================================== 1. PROJECT IN ONE PAGE
H1("1. The project in one page")
P("What was the assignment?", h2)
P("IT-457 is a cloud computing course. Each group analyses a real company's use of the cloud (a case study) and does a small "
  "hands-on exercise linked to the case. Our group (47) was given <b>Shaadi.com</b> under <b>Theme 4: Serverless and Startups</b>. "
  "The course headline for the case is \"AI/ML on AWS to analyse 67 billion event records\". The exercise suggested by the guide for "
  "this theme: <i>build a small serverless function with an API trigger and measure cold start and cost per 1,000 requests.</i>")
P("What did we deliver, week by week?", h2)
T([["Phase", "What we produced"],
   ["Week 1", "Research report: company background, sources and links, first look at the AWS services Shaadi.com uses."],
   ["Week 2", "Analysis and plan: problems P1-P4 with root causes, architecture diagrams (Figures 1-5), solution analysis, "
              "DB3 cost per 1,000 requests, critical evaluation, and a plan for the exercise (two Lambdas, experiments E1-E4, a cost model, risks)."],
   ["Implementation", "Built the serverless stack in AWS Mumbai, ran a pilot (run 1), then the full experiments (run 2), "
                      "collected CloudWatch data, built the results workbook and the final report; paused the stack for the demo."],
   ["Final submission", "Zip: final report (18 pages), results workbook, code, SAM template, data, 14 screenshots, figures, Week 1-2 reports."]],
  [1.3, 5.7], "Project phases")
P("What did we find? (the four results)", h2)
N(["<b>E1 Cold vs warm.</b> The first call that has to start a new execution environment is 10-60x slower than a warm call.",
   "<b>E2 Memory.</b> Lambda gives CPU in proportion to memory. That helps code that computes at start-up (the interest API's cold start "
   "fell from 1,950 to 699 ms), but not code that waits on another service (moderation stayed at about 175-200 ms warm), where extra memory only adds cost.",
   "<b>E3 Concurrency.</b> Our new account allows only 10 concurrent executions, so Lambda allows at most 100 requests per second. Served throughput "
   "flattened at 99-101 req/s; the rest got HTTP 503.",
   "<b>E4 Cost.</b> Measured cost per 1,000 requests matched our Week 2 model: Lambda itself is nearly free; the API Gateway request fee and "
   "(for moderation) the Rekognition fee dominate. Cold starts are now billed (Init time is included in Billed Duration)."])
F(FIG + "fig6_architecture_built.png", "What we built (detailed in Section 6)", 6.8)

# ====================================================================================== 2. STORY / TIMELINE
H1("2. The story of the project, start to finish")
P("Tell it in this order; every step has a reason.", body)
N(["<b>Understand the case.</b> We read the AWS blogs and case studies about Shaadi.com (gp3 migration, DynamoDB messaging, Rekognition "
   "moderation, the 2016 migration study). We noticed the course headline \"67 billion event records\" is not in any primary source, so we did not use it in any calculation.",
   "<b>Analyse.</b> We reduced the story to four problems (P1-P4), each with a symptom, root cause and the cloud property that fixes it, and "
   "computed the database (DB3) cost per 1,000 requests from the published numbers: $0.180 -> $0.178 -> $0.133.",
   "<b>Pick the exercise.</b> Of Shaadi.com's systems, only photo moderation is serverless, so we rebuilt that path (Lambda B) and added "
   "an empty function (Lambda A) so we could separate the cost of Lambda itself from the cost of the ML call. We kept the 'send interest' "
   "API from our first prototype as a database-backed middle case.",
   "<b>Set guardrails.</b> Region Mumbai; a $5 AWS Budgets alert to email; one IAM role per function with only the permissions it needs; tags on resources.",
   "<b>Pilot (run 1).</b> First we built only the interest API (API Gateway -> Lambda -> DynamoDB) and measured it from the browser at 128, 512 and 1,024 MB. "
   "This proved the method: first call cold, the rest warm, and CloudWatch showed Init Duration.",
   "<b>Build the full stack.</b> S3 bucket with 30 test photos, DynamoDB table <i>verdicts</i>, three new functions (shaadi-ping, shaadi-moderate, "
   "shaadi-loadgen), their IAM policies, and two new API routes.",
   "<b>Hit and fix problems.</b> /ping is reserved by API Gateway (renamed to /baseline); renaming broke the invoke permission (re-created the integration); "
   "the boto3 waiter needed a permission we had not granted (switched waiter); CSVs downloaded instead of displaying (changed content type).",
   "<b>Run the experiments.</b> One combined cold/warm run (3 functions x 4 memory sizes), one concurrency run (1/9/50 users x 60 s), one CloudWatch export.",
   "<b>Analyse and write up.</b> Raw data into CSVs, charts, a workbook with live formulas, and the final report with measured versus modelled cost.",
   "<b>Pause.</b> All four functions throttled (reserved concurrency 0) so nothing runs or bills until the demo."])
T([["When (Nov 2026, IST)", "Event"],
   ["12 Nov, evening", "Pilot run 1 on the interest API (browser client, 128/512/1,024 MB); CloudWatch Logs Insights queries"],
   ["12 Nov, about 00:30-01:10 (13th)", "Budget created; quota checked (10); bucket, photos, table, 3 functions, IAM policies, routes"],
   ["13 Nov 01:11", "First cold/warm run (ping + interest), run 20261112T194146 (UTC)"],
   ["13 Nov 01:15-01:18", "Final cold/warm run on all three functions, run 20261112T194523"],
   ["13 Nov 01:19-01:23", "Concurrency run 20261112T194909"],
   ["13 Nov 01:23", "CloudWatch export run 20261112T195330"],
   ["13 Nov 01:25-01:35", "Screenshots, tagging, then all functions throttled (paused)"]],
  [2.2, 4.8], "Timeline of the build and runs (run IDs are UTC timestamps)")

# ====================================================================================== 3. THE CASE
H1("3. The case: Shaadi.com on AWS")
P("3.1 The company", h2)
P("Shaadi.com was founded by Anupam Mittal in 1996 and is the flagship brand of People Interactive Pvt. Ltd., Mumbai. It is a two-sided "
  "matchmaking platform: users browse profiles, send 'interests', chat and meet. Technically this means: read-heavy on profiles, "
  "write-heavy on interactions, very spiky traffic (evenings, weekends, wedding season, the 2020 lockdown), and heavy use of data "
  "science to rank matches.")
T([["Indicator", "Value", "Source"], ["Users (2016)", "Over 35 million", "AWS case study 2016"],
   ["Matches (2016)", "Over 4 million", "AWS Hot Startups 2016"], ["Active profiles (2021)", "Over 3 million", "gp3 blog"],
   ["People who found a partner (2022)", "Over 7 million", "DynamoDB blog"], ["Peak interests (April 2020)", "2.5 million/day", "gp3 blog"],
   ["Messaging data (2022)", "320 MySQL tables, ~100,000 new records/day", "DynamoDB blog"],
   ["'67 billion event records'", "Course headline only; not found in primary sources; not used", "-"]],
  [2.3, 3.0, 1.7], "Scale of Shaadi.com")
P("3.2 Four problems (P1-P4)", h2)
T([["#", "Symptom (business)", "Root cause (technical)", "Cloud property that fixes it", "AWS answer"],
   ["P1", "Slow feature delivery, 1-2 algorithms per cycle, no self-service analytics", "Hosted private cloud: capacity bought per project, one shared load balancer",
    "On-demand capacity, managed services", "Full migration 2016, Redshift, ASGs, ELB per service"],
   ["P2", "Lockdown 2020: chats/interests delayed 10-500 s for ~2 h/day", "DB3 MySQL limited by IOPS; on gp2, IOPS = 3 per GB, so more IOPS = more disk",
    "Storage performance independent of size", "EBS gp3 (IOPS set separately), Elastic Volumes"],
   ["P3", "Messaging hard and costly to scale", "Relational DB for a key-value access pattern",
    "Purpose-built, horizontally scaling DB", "DynamoDB, migrated with a strangler fig"],
   ["P4", "New photos waited for manual review", "Humans checked every upload",
    "Pay-per-use ML triggered by events", "S3 -> Lambda -> Rekognition (2018)"]],
  [0.3, 1.6, 1.85, 1.45, 1.8], "Problems, causes and fixes", fs=7.8)
box("How to say it", ["\"The common thread is <b>coupling</b>: compute was coupled to procurement, IOPS to disk size, the access pattern to a "
                      "relational engine, and moderation throughput to people. Each AWS change broke one coupling. Our exercise tests the serverless fix for P4.\""])
P("3.3 Architecture of Shaadi.com", h2)
F(W2 + "f-001.png", "Evolution from a hosted private cloud to AWS (from our Week 2 report)", 6.3)
F(W2 + "f-003.png", "Matrimonial portal: ALB -> web tier (ASG) -> internal ALB -> microservices -> three MySQL clusters on EC2; DB3 is the hot one", 6.3)
F(W2 + "f-005.png", "Strangler-fig migration of messaging from MySQL to DynamoDB: dual writes, move clients one by one, switch reads, backfill", 5.8)
F(W2 + "f-007.png", "Analytics loop (events -> Redshift -> reports, A/B tracker) and the serverless photo moderation path we rebuilt", 6.3)
P("3.4 Key decisions and trade-offs", h2)
T([["Decision", "Why it fits", "Trade-off", "Concept"],
   ["Redshift pilot first, then full migration (DMS, ~3 months)", "Proved value with low risk", "Two environments for a while", "Incremental migration"],
   ["Auto Scaling Groups + one ALB per service", "Each service scales by its own load", "Services must be stateless", "Elasticity"],
   ["gp2 -> gp3 for DB3", "IOPS 6,000 -> 10,000 without buying disk; done live", "Still self-managed MySQL", "Right-sizing"],
   ["DynamoDB for messaging", "Key-value pattern, scales horizontally, serverless", "Design access patterns up front; lock-in", "Purpose-built DB"],
   ["Provisioned capacity + auto scaling (not on-demand)", "Predictable daily traffic is cheaper reserved", "Throttling risk on spikes", "Cost optimisation"],
   ["Lambda + Rekognition for photos", "No GPUs, no training, pay per image", "Per-image price at scale; black-box model", "Serverless, managed AI"]],
  [2.0, 1.95, 1.75, 1.3], "Shaadi.com's decisions", fs=7.9)
P("3.5 Cost and outcomes", h2)
F(W2 + "f-009.png", "DB3 monthly cost and cost per 1,000 interest requests", 6.0)
T([["Stage", "Setup", "Requests/day", "Cost/month", "Per 1,000 requests"],
   ["Before lockdown", "6 x r5.8xlarge, gp2", "1.8 M", "$9,730", "$0.180"],
   ["Scaled on gp2", "8 x r5.8xlarge, gp2 2 TB", "2.5 M", "$13,373", "$0.178"],
   ["After gp3", "6 x r5.8xlarge, gp3 8,000 IOPS", "2.5 M", "$9,963", "$0.133 (-26%)"]],
  [1.4, 2.1, 1.0, 1.0, 1.5], "DB3 unit cost (our calculation: monthly cost / (daily requests x 30) x 1,000)")
P("How the unit cost was calculated, e.g. after gp3: $9,963 / (2.5 M x 30 = 75 M requests) x 1,000 = $0.133. Other published outcomes: "
  "storage cost -15%, DB3 secondary CPU -20%, messaging on DynamoDB at least 60% cheaper and over 40% faster, photo go-live time expected to fall 95%, "
  "twice as many algorithms tested at a time.")
P("3.6 Critique (what we would question)", h2)
B(["Vendor lock-in: DynamoDB, Rekognition, Lambda event wiring are AWS-only.",
   "DB3 stayed self-managed MySQL; Aurora could remove manual capacity planning.",
   "Personal data (photos, chats) falls under India's Digital Personal Data Protection Act 2023; Mumbai hosting helps residency but not consent or retention.",
   "Automated moderation makes mistakes; keep humans for borderline cases (our function sends 60-80% confidence to 'review').",
   "From our experiment: serverless has its own limits, namely cold starts and account quotas."])

# ====================================================================================== 4. CONCEPTS
H1("4. Cloud concepts you must be able to explain")
P("4.1 Serverless and AWS Lambda", h2)
P("<b>Serverless</b> means you deploy code (a function) and the cloud provider runs it on demand, scales it automatically and bills only "
  "for actual use. You do not manage servers, operating systems or capacity. <b>AWS Lambda</b> runs a function when an event arrives "
  "(an HTTP request through API Gateway, an S3 upload, a queue message, a console test).")
P("4.2 The execution environment and its life cycle", h2)
P("Lambda runs each function inside an <b>execution environment</b>: a lightweight micro-VM (Firecracker) with the runtime (Python 3.15) "
  "and your code. Its life has three phases:")
T([["Phase", "What happens", "Seen in our data as"],
   ["INIT", "Lambda creates the environment, downloads the code, starts the Python runtime and runs everything outside the handler "
            "(imports such as boto3, creating clients, global variables). Happens once per environment.", "Init Duration in the REPORT line; COLD_START flag = True"],
   ["INVOKE", "Lambda calls lambda_handler(event, context) for one request. One environment handles one request at a time.", "Duration and Billed Duration"],
   ["SHUTDOWN", "After some idle time (minutes, not guaranteed) Lambda freezes and later destroys the environment.", "Next call is cold again"]],
  [0.9, 4.3, 1.8], "Lambda execution environment phases")
box("Cold start vs warm start", [
    "<b>Cold start</b>: a request arrives and no idle environment exists, so Lambda must run INIT first. Happens on the first request, "
    "after a deployment or configuration change, after idle time, and whenever traffic needs more environments than exist (scaling out).",
    "<b>Warm start</b>: an idle environment already exists; Lambda skips INIT and only runs the handler. Global variables survive between "
    "warm calls, which is how our COLD_START flag works and why SDK clients are created at module level (reused, not rebuilt each call)."])
P("4.3 Memory, CPU and why memory changes speed", h2)
P("You choose only memory (128 MB to 10,240 MB). Lambda allocates CPU in proportion: at 1,769 MB a function gets the equivalent of one full vCPU; "
  "at 128 MB it gets about 7% of one. So more memory makes CPU-bound work faster (Python start-up, importing boto3, TLS handshakes), but does "
  "nothing for time spent waiting on a network call (Rekognition, DynamoDB). That is exactly what E2 shows.")
P("4.4 How Lambda is billed", h2)
B(["<b>Requests</b>: $0.20 per million invocations.",
   "<b>Compute</b>: $0.0000166667 per GB-second (x86). GB-seconds = (memory in GB) x (billed seconds). Billed duration is rounded up to the next 1 ms.",
   "<b>INIT is now billed</b>: since August 2025, the init phase of on-demand functions is included in Billed Duration. Our cold REPORT lines show "
   "Billed = Init + Duration (e.g. 1,242 + 552 = about 1,795 ms, billed 1,831 ms at p50).",
   "Free tier: 1 million requests and 400,000 GB-s per month (our usage was far below)."])
P("4.5 Concurrency, quotas and throttling", h2)
P("<b>Concurrency</b> = number of requests being processed at the same moment = number of busy environments. Rule of thumb: "
  "concurrency = requests per second x average duration in seconds. Limits:")
B(["<b>Account concurrency quota</b>: default 1,000 per region; <b>our new account had 10</b> (AWS gives new accounts low limits until usage history builds).",
   "<b>Requests-per-second limit</b>: Lambda allows at most 10 x the concurrency quota invocations per second (documented in the Lambda scaling guide). "
   "For us: 10 x 10 = 100 req/s. This, not concurrency, is what capped E3, because our function runs in about 1.5 ms.",
   "<b>Throttling</b>: when a limit is exceeded Lambda rejects the call (TooManyRequestsException, HTTP 429 from Lambda). API Gateway HTTP APIs "
   "turn that into <b>HTTP 503 Service Unavailable</b> for the client, which is what we saw.",
   "<b>Reserved concurrency</b>: a per-function setting. Setting it to 0 (the console's Throttle button) blocks all invocations. That is how we paused the stack.",
   "<b>Provisioned concurrency</b>: pre-initialised environments kept warm (paid), the standard cure for cold starts on user-facing APIs."])
P("4.6 Amazon API Gateway (HTTP API)", h2)
P("API Gateway is the managed 'front door' that turns HTTPS requests into Lambda invocations. We used an <b>HTTP API</b> (cheaper and simpler "
  "than a REST API: $1.00 vs $3.50 per million). Terms: a <b>route</b> = method + path (e.g. POST /moderate); an <b>integration</b> = where the "
  "route sends the request (our Lambda functions, using <b>payload format 2.0</b>); a <b>stage</b> = a deployment ($default, with auto-deploy, so "
  "changes go live immediately). API Gateway also needs a <b>resource-based permission</b> on each Lambda function to be allowed to invoke it; "
  "the console adds it automatically when you tick 'Grant API Gateway permission', scoped to the route's path.")
P("4.7 Amazon DynamoDB", h2)
P("A fully managed key-value / document NoSQL database. Each table has a <b>partition key</b> (ours: interestId and verdictId, both strings, "
  "filled with random UUIDs so writes spread evenly). <b>On-demand</b> capacity mode bills per request ($0.625 per million write request units, "
  "one WRU per write of up to 1 KB), with no capacity planning. Shaadi.com used provisioned capacity because its traffic is predictable; for a "
  "spiky test, on-demand is right.")
P("4.8 Amazon S3", h2)
P("Object storage. Our bucket <i>it457-g47-shaadi-705029438856</i> (bucket names are global, so we added the account ID) holds <i>photos/</i> (30 test "
  "images) and <i>results/</i> (CSV outputs). Block Public Access is on: nothing is public; only roles with permission can read or write.")
P("4.9 Amazon Rekognition (content moderation)", h2)
P("A managed computer-vision service. <b>DetectModerationLabels</b> takes an image (bytes or an S3 object) and returns labels for unsafe "
  "content (explicit, violence, drugs, etc.) with a confidence score. <i>MinConfidence</i> filters out low-confidence labels. Price about $0.001 per "
  "image (first tier). Rekognition reads the image from S3 directly, so the image never passes through our Lambda.")
P("4.10 IAM: roles, policies and least privilege", h2)
B(["<b>IAM role</b>: an identity a service assumes. Each Lambda function has an <b>execution role</b>; its policies decide what AWS APIs the code may call.",
   "<b>Identity-based policy</b> (attached to the role): JSON with Effect, Action, Resource. We added one <b>inline policy</b> per function, naming exact actions and exact resource ARNs.",
   "<b>Resource-based policy</b> (attached to the function): who may <i>invoke</i> it (API Gateway, scoped by source ARN).",
   "<b>Least privilege</b>: grant only what is needed. Example: the moderation role can read only photos/* in our bucket and write only to the verdicts table.",
   "<b>AWSLambdaBasicExecutionRole</b> (auto-created): lets the function write its logs to CloudWatch."])
P("4.11 CloudWatch Logs, REPORT lines and Logs Insights", h2)
P("Every invocation writes logs to the log group <i>/aws/lambda/&lt;function&gt;</i>. Lambda adds one <b>REPORT</b> line per invocation, e.g.:")
code("REPORT RequestId: 6ac4de16-...  Duration: 552.20 ms  Billed Duration: 1831 ms  Memory Size: 128 MB  Max Memory Used: 95 MB  Init Duration: 1242.48 ms",
     numbers=False, wrap=120)
P("Init Duration appears only on cold invocations, which is how cold starts are identified server-side. <b>Logs Insights</b> is a query language "
  "over logs; our harness used it to pull every REPORT line (fields @initDuration, @duration, @billedDuration, @memorySize, @maxMemoryUsed).")
P("4.12 Budgets, tags, infrastructure as code", h2)
B(["<b>AWS Budgets</b>: emails an alert when cost passes a threshold. Ours: it457-g47-5usd, $5/month.",
   "<b>Tags</b>: key-value labels on resources (project=it457-g47) for cost tracking and clean-up. We tagged in bulk with Resource Explorer.",
   "<b>AWS SAM</b> (Serverless Application Model): a CloudFormation extension; one template.yaml describes the whole stack and "
   "<i>sam deploy</i> creates it, <i>sam delete</i> removes it. We wrote the template for reproducibility; the live stack was built in the console because CloudShell was unavailable."])

# ====================================================================================== 5. TOOLS
H1("5. Tools and services used")
T([["Tool / service", "What it is", "What we used it for"],
   ["AWS Management Console (web)", "Browser UI for all AWS services", "All building and configuration (CloudShell/CLI unavailable while account verification was pending)"],
   ["AWS Lambda (Python 3.15)", "Serverless compute", "4 functions: shaadi-ping, shaadi-interest-api, shaadi-moderate, shaadi-loadgen"],
   ["Amazon API Gateway (HTTP API)", "Managed HTTPS front door", "API ypq1jax2t5 with 5 routes, Lambda integrations, $default stage"],
   ["Amazon DynamoDB", "Serverless NoSQL database", "Tables Interests and verdicts (on-demand)"],
   ["Amazon S3", "Object storage", "Test photos (input to Rekognition) and experiment CSVs (output)"],
   ["Amazon Rekognition", "Managed computer vision", "DetectModerationLabels on each photo"],
   ["AWS IAM", "Identity and permissions", "One execution role per function plus least-privilege inline policies"],
   ["Amazon CloudWatch Logs + Logs Insights + Metrics", "Logging, queries, metrics", "REPORT lines (init/billed time), throttles and concurrency graphs"],
   ["AWS Budgets", "Cost alerts", "$5 monthly alert by email"],
   ["Service Quotas", "View account limits", "Found Lambda concurrent executions = 10"],
   ["AWS Resource Explorer (Tag Editor)", "Find and tag resources", "Bulk-tagged 9 resources project=it457-g47"],
   ["AWS SAM (template.yaml)", "Infrastructure as code", "Reproducible definition of the whole stack"],
   ["boto3", "AWS SDK for Python (built into the Lambda runtime)", "Calls to DynamoDB, Rekognition, S3, Lambda and CloudWatch Logs"],
   ["Python standard library", "urllib, threading, concurrent.futures, csv", "HTTP load generation and CSV writing inside the harness"],
   ["Google Chrome + DevTools JavaScript (fetch, canvas)", "Browser", "Run-1 pilot measurements, generating test images, live demo page"],
   ["Python (pandas-free) + matplotlib", "Analysis and charts", "Figures 6-10 of the report"],
   ["ReportLab, openpyxl, LibreOffice", "PDF, Excel, formula recalculation", "Final report, workbook with live formulas (0 formula errors)"]],
  [1.9, 1.9, 3.2], "Every tool used", fs=7.9)

# ====================================================================================== 6. ARCHITECTURE
H1("6. Architecture as built")
F(FIG + "fig6_architecture_built.png", "Exercise architecture in ap-south-1", 6.9)
P("6.1 Resource inventory", h2)
T([["Resource", "Name / identifier", "Key settings"],
   ["AWS account", "705029438856", "Region ap-south-1; Lambda concurrency quota 10"],
   ["HTTP API", "shaadi-interest-http-api (ypq1jax2t5)", "$default stage, auto-deploy; URL https://ypq1jax2t5.execute-api.ap-south-1.amazonaws.com"],
   ["Routes", "GET /, POST /interest, GET /interest/{id}", "-> shaadi-interest-api"],
   ["", "GET /baseline", "-> shaadi-ping (was /ping)"],
   ["", "POST /moderate", "-> shaadi-moderate"],
   ["Lambda", "shaadi-ping", "128 MB, Python 3.15, no env vars, role shaadi-ping-role-ic5uaa9m"],
   ["Lambda", "shaadi-interest-api", "1,024 MB at pause time (experiment changed it), 10 s timeout, TABLE_NAME=Interests"],
   ["Lambda", "shaadi-moderate", "512 MB at start, 10 s timeout, BUCKET, TABLE_NAME=verdicts, role shaadi-moderate-role-tgglr5c0 + policy ModeratePhotosAccess"],
   ["Lambda", "shaadi-loadgen", "1,024 MB, 15 min timeout, API_URL, BUCKET, role shaadi-loadgen-role-yjq13mu3 + policy LoadgenExperimentAccess"],
   ["DynamoDB", "Interests", "Partition key interestId (S), on-demand"],
   ["DynamoDB", "verdicts", "Partition key verdictId (S), on-demand, tag project=it457-g47"],
   ["S3", "it457-g47-shaadi-705029438856", "Block Public Access on; photos/ (30 JPEGs, 532 KB), results/ (7 CSVs)"],
   ["Budget", "it457-g47-5usd", "$5/month, email alert"],
   ["Log groups", "/aws/lambda/shaadi-*", "One per function"]],
  [1.0, 2.5, 3.5], "Everything that exists in the account", fs=7.9)
box("Note on memory at pause time", ["The harness changes MemorySize to force cold starts, so each function is left at the last size tested "
                                     "(1,024 MB for ping/interest/moderate after the cold/warm run, then ping at 512 MB after the concurrency run). That is harmless; you can show it in the demo as proof the harness works."])
P("6.2 What happens on each request (walk-throughs)", h2)
P("<b>GET /baseline</b>: client -> HTTPS -> API Gateway matches the route -> invokes shaadi-ping with a payload-2.0 event -> handler returns "
  "{\"pong\": true, \"coldStart\": ...} -> API Gateway returns HTTP 200. No other AWS service is touched, so this measures pure Lambda + API Gateway overhead.")
P("<b>POST /interest</b> with {from, to, message}: API Gateway -> shaadi-interest-api -> builds an item with a new UUID and timestamp -> "
  "DynamoDB PutItem into Interests -> returns 201 Created with the saved item. Same pattern as Shaadi.com's 'send interest' action (which hits DB3 in production).")
P("<b>POST /moderate</b> with {imageKey}: API Gateway -> shaadi-moderate -> calls Rekognition DetectModerationLabels pointing at "
  "s3://bucket/photos/... -> Rekognition fetches the image from S3 itself -> returns labels -> function decides approved / review / rejected "
  "-> PutItem into verdicts -> returns 200 with verdict, labels, rekognitionMs, coldStart. In production Shaadi.com triggers this from an S3 upload event rather than an API call.")
P("<b>shaadi-loadgen</b> (console test event, no route): runs inside AWS and calls the public API URL like a client would, so client latency "
  "= network inside the region + API Gateway + Lambda. It also changes the target functions' configuration (to force cold starts), queries "
  "CloudWatch Logs Insights, and writes results to S3.")

# ====================================================================================== 7. CODE
H1("7. The code, line by line")
P("All code is Python 3.15 for Lambda (handler signature <font name='Mono'>lambda_handler(event, context)</font>) plus a few JSON/YAML/JS files. "
  "Line numbers below match the files in the submission's <i>code/</i> folder. In the console each function's file is named lambda_function.py; "
  "the submission uses descriptive names.")
P("7.1 shaadi-ping (Lambda A, the baseline)", h2)
code(read(CODE + "ping_function.py"), "code/ping_function.py")
explain([["1", "Docstring: what the function is for. API Gateway reserves /ping, so the route is /baseline."],
         ["2", "Only the json module: no boto3, no network, so INIT is as small as Python allows (about 100 ms)."],
         ["4", "COLD_START = True is module-level code, which runs once per execution environment during INIT."],
         ["7", "lambda_handler is the entry point Lambda calls; event = request data, context = runtime info (unused)."],
         ["8-9", "<font name='Mono'>global</font> lets us modify the module variable. The tuple swap stores the current value in <i>cold</i> and sets the global to False, "
                 "so the first call in an environment reports True and every later (warm) call False."],
         ["10-14", "Returns the format API Gateway (payload 2.0) expects: statusCode, headers, body as a JSON string. API Gateway turns it into the HTTP response."]])
P("7.2 shaadi-interest-api (the portal's 'send interest')", h2)
code(read(CODE + "interest_function.py"), "code/interest_function.py")
explain([["7", "boto3 is the AWS SDK. Importing it is the main reason this function's INIT takes 0.5-1.2 s."],
         ["9", "The DynamoDB Table object is created at module level, during INIT, so warm calls reuse it (and its connection). Table name comes from an environment variable with a default."],
         ["10", "The cold-start flag, as in ping."],
         ["13-18", "Helper that builds the HTTP response; CORS header '*' so a browser page on another origin can call the API (used by the run-1 pilot script)."],
         ["21-24", "Detect cold/warm; read the HTTP method from the payload-2.0 event (requestContext.http.method)."],
         ["26-37", "POST: parse the JSON body; build the item with a random UUID (spreads writes across partitions), sender, receiver, message truncated to 200 chars, timestamp in ms; PutItem; log a JSON line; return 201 Created."],
         ["39-43", "GET /interest/{id}: path parameter 'id'; GetItem by key; 200 if found, else 404."],
         ["45", "GET /: a health response."]])
P("7.3 shaadi-moderate (Lambda B, photo moderation)", h2)
code(read(CODE + "moderate_function.py"), "code/moderate_function.py")
explain([["13-15", "Configuration from environment variables (BUCKET is required, so the function fails fast if it is missing). Rekognition client and DynamoDB Table are created once, in INIT."],
         ["16-17", "Business rules as constants: ignore labels below 60% confidence; a label of 80% or more rejects the photo; anything between goes to human review (mirrors Shaadi.com keeping humans for borderline cases)."],
         ["29-32", "Read imageKey from the JSON body; return 400 if missing (input validation)."],
         ["34-37", "Call DetectModerationLabels with an S3Object reference: Rekognition reads the image from S3 directly, so no image bytes go through Lambda. We time the call with perf_counter to separate ML time from everything else."],
         ["39-41", "Turn the response into a simple list; take the highest confidence; decide the verdict with a conditional expression."],
         ["43-46", "Store an audit record in DynamoDB: verdictId (UUID), image, verdict, labels as JSON text, Rekognition time, cold flag, timestamp."],
         ["47-49", "Structured log line and the 200 response (the harness reads rekognitionMs and coldStart from it)."]])
P("7.4 shaadi-loadgen (the experiment harness)", h2)
P("This is the most important file to understand: it is how every number in the results was produced. It runs inside AWS and is started "
  "from the Lambda console with a JSON test event that picks a mode.")
code(read(CODE + "loadgen_function.py"), "code/loadgen_function.py")
explain([["1-14", "Docstring with the three test events used and what each mode does."],
         ["15-27", "Imports: csv/io to build CSV text in memory; threading + ThreadPoolExecutor for parallel calls; urllib.request to make HTTP calls with no extra packages; uuid for a random nonce; boto3 for AWS APIs."],
         ["29-33", "Configuration and clients: API base URL and bucket from environment variables; clients for Lambda (to change configuration), CloudWatch Logs (queries) and S3 (results)."],
         ["35-39", "TARGETS maps a short name to the function name, HTTP method and path. Note ping uses /baseline."],
         ["42-47", "body_for builds a request body per target: an interest message, or an imageKey cycling through photo_01..photo_30 so different photos are moderated."],
         ["50-69", "call() makes one HTTP request and returns status, the function's coldStart flag, client latency in ms (perf_counter, high resolution) and, for moderation, rekognitionMs. "
                   "HTTP errors (like 503) are recorded with their status code; network errors as -1. It never raises, so one failure cannot stop an experiment."],
         ["72-78", "force_cold(): reads the function's configuration, adds a new random RUN_NONCE environment variable and sets MemorySize. Any configuration change makes Lambda discard all existing environments, "
                   "so the next requests are guaranteed cold. The waiter 'function_updated' polls GetFunctionConfiguration until the update is finished; then we wait 3 s more for safety."],
         ["81-86", "put_csv(): writes rows as CSV into memory and uploads to S3 as text/plain (so the file opens in a browser instead of downloading)."],
         ["89-91", "pct(): nearest-rank percentile (sort, pick index round(p/100 x (n-1)))."],
         ["94-121", "coldwarm mode. For each target and memory: force_cold; create a Barrier for n threads (burst=8) so all 8 requests are released at the same instant: since one environment serves one request at a time, "
                    "8 simultaneous requests need 8 new environments, i.e. 8 cold starts in one go. Then 50 sequential requests, which reuse warm environments. Every result row is kept; a summary computes cold p50, warm p50/p95 and errors. Both are written to S3."],
         ["124-157", "concurrency mode. Optionally force_cold at a given memory. For each level (number of virtual users) start that many threads; each loops calling the API until the deadline (60 s), recording status, latency and time. "
                     "Summary: requests, successes, throttled/errors, requests per second, p50/p95/p99 and cold starts. 5 s pause between levels."],
         ["160-184", "logs mode. For each function's log group, run a Logs Insights query selecting REPORT lines and the fields we need, poll until complete, convert @memorySize and @maxMemoryUsed from bytes to MB, write all rows to S3. Limit 10,000 lines per query."],
         ["187-191", "Handler: timestamp run ID (UTC), dispatch to the mode named in the event, return the summary (shown in the console)."]])
box("Why a barrier-synchronised burst?", ["Because one execution environment handles exactly one request at a time. If 8 requests arrive simultaneously and "
                                          "no environment exists, Lambda must create 8, so we get 8 cold measurements per configuration in about 2 seconds, instead of waiting 10+ minutes between single cold starts. "
                                          "The function's own coldStart flag confirms each one (7 or 8 of 8 were cold; when 7, one request was served by an environment that had just finished)."])
P("7.5 IAM policies", h2)
for f, title, rows in [
    ("iam_policy_InterestsTableAccess.json", "Interest API: read/write one table", [["Statement", "PutItem and GetItem only, only on table/Interests in our account and region."]]),
    ("iam_policy_moderate.json", "Moderation: three narrow permissions", [["ReadTestPhotos", "s3:GetObject only under photos/ of our bucket. Rekognition uses the caller's permissions to read the S3 object, so the role must be able to read it."],
                                                                          ["ModeratePhotos", "rekognition:DetectModerationLabels; Rekognition does not support resource-level restriction for this action, so Resource is '*'."],
                                                                          ["WriteVerdicts", "dynamodb:PutItem only on table/verdicts."]]),
    ("iam_policy_loadgen.json", "Harness: change config, query logs, write results", [["ForceColdStarts", "Get/UpdateFunctionConfiguration on the three target functions only (not on itself, not on others)."],
                                                                                       ["QueryReportLines", "logs:StartQuery / GetQueryResults (Logs Insights)."],
                                                                                       ["WriteResults", "s3:PutObject only under results/."]])]:
    code(json.dumps(json.load(open(CODE + f)), indent=2), f"code/{f}  ({title})")
    explain(rows)
P("7.6 SAM template (infrastructure as code)", h2)
code(read(CODE + "template.yaml"), "code/template.yaml")
explain([["1-3", "CloudFormation version and the SAM transform that enables AWS::Serverless::* resource types."],
         ["9-16", "Globals applied to every function: runtime, architecture x86_64, 10 s timeout, 512 MB, tag. (python3.13 here because SAM's validated runtime list may lag the console's 3.15.)"],
         ["19-24", "The HTTP API resource with the $default stage."],
         ["26-42", "Two DynamoDB tables, on-demand (PAY_PER_REQUEST), with their partition keys."],
         ["44-53", "S3 bucket named with the account ID (!Sub), all four Block Public Access settings on."],
         ["55-128", "Four functions: CodeUri and Handler, environment variables using !Ref to other resources, inline least-privilege policies (Statement blocks), and Events of type HttpApi that create the routes and the invoke permissions automatically."],
         ["130-137", "The $5 monthly cost budget."],
         ["139-141", "Output: the API URL after deployment."]])
P("Deploy: <font name='Mono'>sam build &amp;&amp; sam deploy --guided --region ap-south-1</font>. Remove: <font name='Mono'>sam delete</font>.")
P("7.7 CloudWatch Logs Insights queries (used in run 1)", h2)
code(read(CODE + "cloudwatch_queries.txt"), "code/cloudwatch_queries.txt", wrap=118)
explain([["2", "All REPORT lines grouped by memory: count, init stats, duration, billed and max memory."],
         ["5", "Only cold starts: ispresent(@initDuration) is true only when INIT happened."],
         ["8", "Only warm calls: percentiles of duration and billed duration by memory."]])
P("7.8 Browser script for the run-1 pilot", h2)
code(read(CODE + "measure_latency.js"), "code/measure_latency.js", wrap=118)
explain([["4-5", "Store results on window; define runTest(label) for one configuration."],
         ["7-14", "call(): POST to /interest with performance.now() timing, record status, coldStart, latency and time."],
         ["15-17", "Request 1 (cold, right after a config change), 100 sequential warm requests, then 10 concurrent requests (extra environments, more cold starts)."]])
P("7.9 Generating the test images", h2)
code(read(CODE + "generate_test_images.js"), "code/generate_test_images.js", wrap=118)
P("Draws 30 coloured 640x480 JPEGs on an HTML canvas and attaches them to the S3 console's upload form (DataTransfer sets the file input). "
  "We used synthetic images to avoid uploading real people's photos; the trade-off is that Rekognition found nothing, so every verdict is 'approved'.")

# ====================================================================================== 8. BUILD LOG
H1("8. How it was built, step by step")
P("Everything was done in the AWS web console (Chrome). The order matters because later steps depend on earlier ones.")
steps = [
    ("Account and region", "Logged in, selected Asia Pacific (Mumbai) ap-south-1 (top-right region menu). Checked credits (~$120). CloudShell refused to start (account verification pending), so no CLI."),
    ("Budget", "Billing and Cost Management > Budgets > Create budget: cost budget it457-g47-5usd, $5 monthly, email alert. Status Healthy, $0.00 used."),
    ("Quota check", "Service Quotas > AWS Lambda > Concurrent executions: applied value 10 (default 1,000). This decided burst size 8 and levels 1/9/50."),
    ("Pilot (run 1)", "Created table Interests (key interestId), function shaadi-interest-api, inline policy InterestsTableAccess, HTTP API with routes GET /, POST /interest, GET /interest/{id}. "
                      "Measured from the browser at 128, 512, 1,024 MB with measure_latency.js; queried CloudWatch with Logs Insights."),
    ("S3 bucket", "S3 > Create bucket: general purpose, name it457-g47-shaadi-705029438856, Block all public access on, tag project=it457-g47."),
    ("Test photos", "Upload page with prefix photos/; generated 30 images with generate_test_images.js; Upload. 30 objects, 531.6 KB."),
    ("Verdicts table", "DynamoDB > Create table: verdicts, partition key verdictId (String), default settings = on-demand, tag project=it457-g47."),
    ("shaadi-ping", "Lambda > Create function: author from scratch, Python 3.15. Pasted the code; Deploy (Ctrl/Cmd+Shift+U). Left at 128 MB."),
    ("shaadi-moderate", "Created the same way; pasted code; Configuration > General: 512 MB, timeout 10 s; Environment variables BUCKET and TABLE_NAME=verdicts."),
    ("Moderate permissions", "IAM > Roles > shaadi-moderate-role-tgglr5c0 > Add permissions > Create inline policy > JSON: pasted iam_policy_moderate.json; named ModeratePhotosAccess."),
    ("shaadi-loadgen", "Created; pasted code; 1,024 MB, timeout 15 min; env API_URL and BUCKET; inline policy LoadgenExperimentAccess on role shaadi-loadgen-role-yjq13mu3."),
    ("Routes", "API Gateway > shaadi-interest-http-api > Routes > Create: GET /ping and POST /moderate."),
    ("Integrations", "Integrations > select route > Create and attach: Lambda function (ARN), 'Grant API Gateway permission' on. Payload format 2.0."),
    ("Smoke test", "fetch() from the API's origin: /moderate returned approved with rekognitionMs 257 and coldStart true. /ping returned 'Healthy Connection' (problem 1)."),
    ("Fix /ping", "Edited the route to GET /baseline; got 500 (problem 2); detached and re-created the integration; /baseline then returned pong with cold then warm."),
    ("First run", "Lambda test event {\"mode\":\"coldwarm\",...}: failed with AccessDenied on GetFunction (problem 3); changed the waiter; re-ran: success in 85 s."),
    ("Content type", "Changed CSV content type to text/plain so results open in the browser (problem 4)."),
    ("Final runs", "coldwarm on 3 functions x 4 memories (about 4 min); concurrency 1/9/50 x 60 s (about 3.5 min); logs export (about 20 s)."),
    ("Evidence", "Opened result CSVs from S3, aggregated in the browser, saved datasets; took screenshots of functions, integrations, verdicts, live responses, metrics, S3, budget."),
    ("Tags", "Resource Explorer: searched 'shaadi', selected 9 resources, Manage tags, project=it457-g47."),
    ("Pause", "Each function > Throttle > Confirm (reserved concurrency 0). Verified: every route returns HTTP 503.")]
T([["#", "Step", "What exactly was done"]] + [[str(i), a, b] for i, (a, b) in enumerate(steps, 1)], [0.3, 1.25, 5.45], "Build log", fs=7.9)

# ====================================================================================== 9. PROBLEMS
H1("9. Problems we hit and how we solved them")
P("These are excellent things to talk about: they show you actually built it.")
probs = [
    ("CloudShell would not start", "New account still under verification.", "Did everything in the web console; wrote the SAM template anyway so the stack is reproducible from code."),
    ("Concurrency quota only 10", "New accounts get low default quotas.", "Bursts of 8 (one slot used by the harness), concurrency levels 1/9/50; turned the limit into a finding (E3)."),
    ("GET /ping returned 'Healthy Connection', function never ran", "API Gateway reserves /ping and /sping for its own health check (documented for REST/WebSocket; we observed it on HTTP API).",
     "Renamed the route to /baseline."),
    ("After renaming, /baseline returned HTTP 500", "The invoke permission API Gateway added to the function was scoped to the old path (.../*/*/ping), so API Gateway was no longer allowed to call Lambda.",
     "Detached the integration and created a new one with 'Grant permission', which added a permission for /baseline."),
    ("Harness failed: AccessDenied lambda:GetFunction", "boto3's waiter 'function_updated_v2' polls GetFunction, which least-privilege policy did not allow.",
     "Switched to waiter 'function_updated', which uses GetFunctionConfiguration (already allowed). Kept the policy minimal."),
    ("Result CSVs downloaded instead of opening", "ContentType text/csv makes browsers download.", "Upload with text/plain; charset=utf-8."),
    ("Logs Insights cap of 10,000 rows", "ping had about 16,400 invocations in the window.", "Used the 10,000 lines that cover E1/E2 and the 1- and 9-user levels; the 50-user level is covered by client data and CloudWatch metrics."),
    ("Large CSVs hard to move out of AWS", "35k-row file.", "Aggregated in the browser into 5-second windows and per-level summaries; raw files kept in S3."),
    ("All moderation verdicts 'approved'", "Synthetic images contain nothing unsafe.", "Stated as a limitation; accuracy not evaluated (we chose not to upload real people's photos).")]
T([["Problem", "Cause", "Fix"]] + [list(p) for p in probs], [1.85, 2.55, 2.6], "Problems and fixes", fs=7.9)

# ====================================================================================== 10. EXPERIMENT DESIGN
H1("10. Experiment design")
T([["Exp.", "Question", "Independent variable", "Measured", "How"],
   ["E1", "How much slower is a cold call than a warm one?", "cold vs warm", "client latency; coldStart flag", "8-call burst after force_cold, then 50 sequential"],
   ["E2", "What does memory do to speed and cost?", "128/256/512/1,024 MB", "latency, Init, billed time, cost", "Repeat E1 at each memory for each function"],
   ["E3", "How does it behave under parallel load?", "1/9/50 virtual users", "req/s, status codes, p50/p95/p99", "Closed loop for 60 s per level on /baseline at 512 MB"],
   ["E4", "Does measured cost match the Week 2 model?", "-", "billed GB-s per request", "REPORT lines x price list"]],
  [0.45, 1.75, 1.3, 1.5, 2.0], "Experiments", fs=7.9)
P("Why three functions? So we can attribute latency and cost: ping isolates Lambda + API Gateway; interest adds an SDK and a database write; "
  "moderation adds a managed ML call. The difference between them is the cost of each extra layer.", body)
P("Why in-region load generation instead of k6 on a laptop? No local tooling or CloudShell was available, and an in-region client removes "
  "home-network noise, so the numbers reflect AWS, not our Wi-Fi.")
P("Run 1 (pilot) results, interest API from the browser", h2)
T([["Memory", "First (cold) request", "100th request (warm)", "Cold starts seen", "Avg Init (CloudWatch)", "Warm billed p50"],
   ["128 MB", "2,118 ms", "79.3 ms", "8", "1,067.7 ms", "34 ms"], ["512 MB", "862 ms", "36.5 ms", "3", "600.2 ms", "7 ms"],
   ["1,024 MB", "664 ms", "37.7 ms", "2", "781.9 ms", "7 ms"]],
  [0.8, 1.2, 1.2, 1.1, 1.4, 1.3], "Run 1 pilot (browser in India -> Mumbai, so latencies include the home network)")
P("The pilot showed the same pattern as the final run, which made us confident in the method before scaling it up.")

# ====================================================================================== 11. RESULTS
H1("11. Results and how to interpret them")
P("11.1 E1/E2: cold versus warm", h2)
F(FIG + "fig7_cold_warm.png", "Client latency medians, log scale", 6.9)
rows = [["Function", "Memory", "Cold starts", "Cold p50", "Warm p50", "Warm p95", "Ratio"]]
for r in csv.DictReader(open("/home/claude/poc/data/run2/coldwarm_summary_console.csv")):
    nm = {"ping": "A: baseline", "interest": "Interest API", "moderate": "B: moderation"}[r["target"]]
    rows.append([nm, r["memory_mb"], f'{r["cold_starts"]}/8', f'{float(r["cold_p50_ms"]):,.0f} ms', f'{float(r["warm_p50_ms"]):.1f} ms',
                 f'{float(r["warm_p95_ms"]):.1f} ms', f'{float(r["cold_p50_ms"]) / float(r["warm_p50_ms"]):.0f}x'])
T(rows, [1.4, 0.75, 0.85, 1.0, 1.0, 1.0, 1.0], "Run 20261112T194523: 696 calls, 0 errors")
P("<b>How to read it.</b> (1) Warm baseline about 18 ms at every memory size: that is the floor (network inside the region + API Gateway). "
  "(2) Cold calls fall with memory for the interest API (1,950 -> 699 ms) because start-up is CPU work (importing boto3, TLS). "
  "(3) Moderation's warm time hardly moves (202 -> 173 ms) because most of it is waiting for Rekognition (median 151-171 ms). "
  "(4) Occasional 0.9-1.8 s spikes inside Rekognition make its p95 noisy.")
P("11.2 What a cold start is made of (server side)", h2)
F(FIG + "fig8_init_breakdown.png", "Init Duration + first handler call, versus a warm call's billed time", 6.9)
T([["Function", "Memory", "Init p50", "Cold handler p50", "Cold billed p50", "Warm billed mean", "Max memory"],
   ["Baseline", "128 / 1,024", "116 / 115 ms", "1.8 / 1.7 ms", "118 / 117 ms", "2.1 / 2.0 ms", "35 MB"],
   ["Interest API", "128 / 1,024", "1,242 / 502 ms", "552 / 65 ms", "1,831 / 569 ms", "38.0 / 7.4 ms", "95 MB"],
   ["Moderation", "128 / 1,024", "1,320 / 1,207 ms", "649 / 239 ms", "1,954 / 1,447 ms", "237.8 / 214.7 ms", "97-100 MB"],
   ["Moderation", "256 / 512", "428 / 642 ms", "402 / 282 ms", "866 / 924 ms", "209.2 / 188.7 ms", "97-100 MB"]],
  [1.0, 0.85, 1.05, 1.05, 1.05, 1.1, 0.9], "From 10,954 REPORT lines", fs=7.9)
B(["<b>Billed = Init + handler</b> on cold calls: INIT is billed (August 2025 change).",
   "<b>The first handler call is slow too</b> for SDK users (552 ms at 128 MB): connections and credentials are set up lazily on first use.",
   "<b>Init is noisy</b> with 8 samples: moderation's Init was 428 ms at 256 MB but 1,207 ms at 1,024 MB. Start-up includes variable work (fetching the runtime, loading libraries), so read small samples as ranges.",
   "<b>All functions used under 100 MB</b>, so 128 MB is enough memory; extra memory buys CPU only."])
P("11.3 E3: concurrency and throttling", h2)
F(FIG + "fig10_concurrency.png", "Served vs throttled throughput; latency over time", 6.9)
T([["Users", "Requests", "200 OK", "503", "Served/s", "p50 / p95 / p99", "Cold starts"],
   ["1", "3,969", "3,969", "0", "66.2", "14.7 / 17.7 / 20.7 ms", "1"],
   ["9", "15,983", "5,936", "10,047 (63%)", "98.9", "38.3 / 50.9 / 56.2 ms", "8"],
   ["50", "14,823", "6,044", "8,779 (59%)", "100.7", "197.5 / 315.7 / 380.9 ms", "0"]],
  [0.6, 0.8, 0.8, 1.0, 0.8, 1.9, 0.8], "Run 20261112T194909, 34,775 requests")
box("The key explanation (be ready to derive it)", [
    "Concurrency needed = requests/s x duration. At 100 req/s and about 1.5 ms per call, only 0.15 environments are busy on average, so the concurrency cap of 10 was <b>not</b> the limit.",
    "Lambda also limits <b>requests per second to 10 x the concurrency quota</b>: 10 x 10 = 100 req/s. Served throughput was 98.9 and 100.7 req/s: exactly that ceiling.",
    "Everything above it was rejected immediately (HTTP 503 from API Gateway), which is why throttled responses were fast. CloudWatch showed up to 8,581 throttles per minute and peak concurrency 9.",
    "At 50 users the slower successful calls (198 ms median) are mostly queueing inside our single harness function (50 threads in one environment), so read that level for throughput, not latency."])
P("11.4 Memory versus cost", h2)
F(FIG + "fig9_compute_cost.png", "Lambda compute cost per 1,000 warm calls by memory", 5.3)
P("For I/O-bound functions (baseline, moderation) duration barely changes, so cost rises in proportion to memory (moderation: $0.0005 at 128 MB to $0.0036 at 1,024 MB, 7x more for a 14% faster call). "
  "For the CPU-bound interest API, duration falls as memory rises, so cost first falls then rises: the cheapest point is 256-512 MB.")

# ====================================================================================== 12. COST MATH
H1("12. Cost arithmetic, worked out")
P("Prices used (US East list prices, same as the Week 2 model; Lambda x86 prices are identical in Mumbai):")
T([["Item", "Price"], ["Lambda requests", "$0.20 per 1 million"], ["Lambda compute (x86)", "$0.0000166667 per GB-second"],
   ["API Gateway HTTP API", "$1.00 per 1 million requests"], ["DynamoDB on-demand writes", "$0.625 per 1 million WRU"],
   ["Rekognition DetectModerationLabels", "$0.001 per image"], ["S3 GET", "$0.0004 per 1,000 requests"]], [3.0, 4.0], "Price inputs")
P("Worked example: moderation at 512 MB, per 1,000 warm requests", h2)
code("""Measured mean billed duration (warm)      = 188.72 ms = 0.18872 s
Memory                                    = 512 MB = 0.5 GB
GB-seconds per call                       = 0.5 x 0.18872 = 0.09436 GB-s
Compute for 1,000 calls                   = 1,000 x 0.09436 x $0.0000166667 = $0.0015727
Lambda requests                           = 1,000 x $0.20 / 1,000,000       = $0.0002
API Gateway                               = 1,000 x $1.00 / 1,000,000       = $0.0010
DynamoDB write (1 per call)               = 1,000 x $0.625 / 1,000,000      = $0.000625
Rekognition (1 image per call)            = 1,000 x $0.001                  = $1.0000
S3 GET by Rekognition                     = $0.0004
-------------------------------------------------------------------------------------
TOTAL per 1,000                           = $1.0038   (Rekognition share = 1.0000 / 1.0038 = 99.6%)""", numbers=False, wrap=120)
T([["Per 1,000 warm requests", "Baseline 128 MB", "Interest 512 MB", "Moderation 512 MB"],
   ["Billed ms (mean)", "2.06", "6.94", "188.72"], ["Compute", "$0.0000043", "$0.0000578", "$0.0015727"],
   ["Requests + API", "$0.0012", "$0.0012", "$0.0012"], ["DynamoDB", "-", "$0.000625", "$0.000625"], ["Rekognition + S3", "-", "-", "$1.0004"],
   ["<b>Total</b>", "<b>$0.0012</b>", "<b>$0.0019</b>", "<b>$1.0038</b>"], ["Week 2 model", "$0.0012", "-", "$1.007 (assumed 600 ms)"]],
  [2.0, 1.6, 1.6, 1.8], "Measured cost per 1,000 requests")
P("<b>Cost of one cold start</b> (extra billed time x memory x price): interest API at 512 MB, (869 - 7) ms x 0.5 GB x $0.0000166667 = $0.0000072. "
  "Tiny in money; the problem with cold starts is latency, not cost.")
P("<b>Scaling it to Shaadi.com</b>: 1 million photos/month at 512 MB: Lambda about $1.57 compute + $0.20 requests; Rekognition about $1,000 at the first-tier price. "
  "So savings come from fewer Rekognition calls (deduplication, resizing, volume tiers), not from tuning Lambda.")
P("<b>What our experiment cost</b>: about 17,500 Lambda invocations, about 53,000 API requests, 236 Rekognition calls, under 1,000 DynamoDB writes: "
  "roughly $0.30 at list price, covered by credits. Budgets shows $0.00.")

# ====================================================================================== 13. LIMITATIONS
H1("13. Limitations and what we would do next")
T([["Limitation", "Effect", "Next step"],
   ["8 cold samples per configuration", "Medians fine; tails (p95+) unreliable", "More bursts, or Lambda Power Tuning"],
   ["Synthetic images", "No unsafe labels; accuracy not measured", "Use a labelled public test set"],
   ["Quota of 10", "E3 shows a new account, not production scale", "Request a quota increase; re-run at 100+ users"],
   ["In-region client", "Real mobile users add 30-150 ms", "Add an external client (k6 from India)"],
   ["List prices", "Ignores free tier, credits, volume tiers", "Use AWS Pricing Calculator for Mumbai"],
   ["Logs Insights 10,000-row cap", "50-user level not in REPORT data", "Paginate by time window"],
   ["API-triggered moderation", "Production would be event-driven", "S3 event -> SQS -> Lambda with retries and a dead-letter queue"]],
  [2.0, 2.4, 2.6], "Limitations")
P("Recommendations for Shaadi.com (from our data)", h2)
B(["Size memory by what the function waits for: 512-1,024 MB for CPU-bound start-up, 128-256 MB for I/O-bound calls.",
   "Use provisioned concurrency (or SnapStart for Python) on user-facing paths like 'send interest'; keep imports light; create clients at module level.",
   "Trigger moderation from S3 events through SQS so spikes queue instead of failing with 503.",
   "Raise quotas before festive peaks and alarm on the Lambda Throttles metric."])

# ====================================================================================== 14. DEMO
H1("14. Presentation-day demo script")
P("Before the session (about 2 minutes)", h2)
N(["Log in to the AWS console, region <b>Asia Pacific (Mumbai)</b>.",
   "Lambda > Functions > shaadi-ping > Configuration > Concurrency > Edit > <i>Use unreserved account concurrency</i> > Save. Repeat for shaadi-interest-api and shaadi-moderate. (Leave shaadi-loadgen throttled.)",
   "Open https://ypq1jax2t5.execute-api.ap-south-1.amazonaws.com/baseline: expect {\"pong\": true, \"coldStart\": true}; refresh: false. Do not refresh again before the demo if you want to show a cold start live (or change an env var just before).",
   "Open tabs: the architecture figure, the Lambda functions list, DynamoDB verdicts, CloudWatch metrics of shaadi-ping, S3 results/."])
P("During the demo (5 minutes)", h2)
T([["Step", "Do", "Say"],
   ["1", "Show the architecture figure", "\"Client, HTTP API, three functions, DynamoDB, Rekognition, S3; a harness inside AWS generates load.\""],
   ["2", "Open /baseline (first time)", "\"coldStart true: Lambda had to create an environment. Refresh: false, about 18 ms, this is the floor.\""],
   ["3", "curl POST /interest", "\"201 Created; the item is in DynamoDB. Same pattern as Shaadi.com's send-interest.\""],
   ["4", "curl POST /moderate photo_07", "\"Rekognition read the photo straight from S3 in about 200 ms, verdict approved, stored in verdicts.\""],
   ["5", "Show verdicts table", "\"Each row records the verdict, Rekognition time and whether it was a cold start.\""],
   ["6", "Show ping metrics (Throttles, concurrency 9)", "\"This is E3: our account allows 100 requests per second, so above that 60% were throttled.\""],
   ["7", "Show the cost table", "\"Per thousand: a tenth of a cent for Lambda paths, a dollar for moderation, 99.6% Rekognition.\""],
   ["8 (optional)", "Change an env var of shaadi-ping, call again", "\"Any configuration change discards environments, which is how our harness forced cold starts.\""]],
  [0.6, 2.2, 4.2], "Demo flow", fs=7.9)
P("Demo commands", h2)
code("""API=https://ypq1jax2t5.execute-api.ap-south-1.amazonaws.com
curl $API/baseline
curl -X POST $API/interest -H 'Content-Type: application/json' -d '{"from":"demo","to":"user_42","message":"Hello"}'
curl -X POST $API/moderate -H 'Content-Type: application/json' -d '{"imageKey":"photos/photo_07.jpg"}'""", numbers=False, wrap=120)
P("After the demo: Throttle each function again (Function page > Throttle > Confirm). After grading: delete functions, API, tables, bucket (empty first), log groups, IAM roles, budget.")

# ====================================================================================== 15. Q&A
H1("15. Questions you may be asked, with answers")
qa = [
    ("Why did you choose this exercise?", "Theme 4 is serverless; the only serverless part of Shaadi.com is photo moderation (S3, Lambda, Rekognition), so we rebuilt it and measured what the guide asks: cold start and cost per 1,000 requests."),
    ("Why ap-south-1?", "Shaadi.com runs in Mumbai and Rekognition launched there in 2018; same region means comparable latency and prices and Indian data residency."),
    ("What exactly is a cold start?", "A request that finds no idle execution environment, so Lambda must create one: start the micro-VM, load the runtime and our code, and run module-level code (imports, client creation) before the handler. It is the INIT phase."),
    ("How did you know a request was cold?", "Two ways that agree: the function's own COLD_START global (True only on the first call in an environment), and CloudWatch REPORT lines, where Init Duration appears only on cold invocations."),
    ("How did you force cold starts?", "The harness changed the function's memory and a RUN_NONCE environment variable. Any configuration change makes Lambda retire existing environments, so the next calls must cold-start. Then 8 simultaneous requests need 8 new environments."),
    ("Why does the interest API have a much longer cold start than the baseline?", "Importing boto3 and creating the DynamoDB client happen during INIT, and the first call also opens TLS connections and fetches credentials. The baseline imports only json."),
    ("Why does more memory make it faster?", "Lambda allocates CPU proportionally to memory; start-up work is CPU-bound, so more CPU finishes it sooner. 128 MB is about 7% of a vCPU."),
    ("Then why not always use more memory?", "You pay per GB-second. If the function mostly waits on another service (Rekognition), more CPU does not shorten the wait, so cost rises with no benefit: moderation compute cost went up 7x for a 14% faster call."),
    ("Are cold starts billed?", "Yes, since August 2025 for on-demand functions. Our cold REPORT lines show Billed Duration equals Init Duration plus handler Duration."),
    ("What limited your throughput?", "The requests-per-second limit, which is 10 times the account concurrency quota. Our quota is 10, so 100 req/s, and served throughput flattened at 99-101 req/s."),
    ("Why not the concurrency limit itself?", "Concurrency = rate x duration = 100 x 0.0015 s = 0.15 on average, far below 10. Peak concurrency in CloudWatch was 9 because of bursts."),
    ("Why HTTP 503 and not 429?", "Lambda throttles with a 429 TooManyRequests error to its caller; the caller here is API Gateway, and HTTP APIs return 503 Service Unavailable to the client."),
    ("Why is your account limited to 10?", "New AWS accounts start with low quotas that rise with usage; the documented default is 1,000. A quota increase can be requested in Service Quotas."),
    ("Why an HTTP API rather than a REST API?", "Cheaper ($1.00 vs $3.50 per million), lower latency, simpler; we needed no REST-only features (usage plans, request validation, caching)."),
    ("Why DynamoDB on-demand when Shaadi.com uses provisioned?", "Our traffic is a short spiky test; on-demand needs no planning. Shaadi.com's daily pattern is predictable, so provisioned with auto scaling is cheaper for them."),
    ("Why UUIDs as keys?", "Random keys spread writes evenly over partitions (no hot partition) and need no coordination."),
    ("How does Rekognition get the image?", "We pass an S3Object reference; Rekognition reads it from S3 using our role's permission, so image bytes never pass through Lambda (less time, less memory)."),
    ("Explain your moderation thresholds.", "MinConfidence 60 drops weak labels. Top label at 80% or more: rejected; any label between 60 and 80: human review; no label: approved. Mirrors Shaadi.com keeping humans for borderline cases."),
    ("Why were all verdicts approved?", "We used synthetic images to avoid uploading real people's photos, so there was nothing unsafe. Accuracy is a stated limitation."),
    ("What is least privilege in your project?", "Each function has its own role with exact actions on exact ARNs, e.g. moderation can read only photos/* and write only to verdicts; the harness can modify only the three target functions."),
    ("Why is the Rekognition resource '*'?", "DetectModerationLabels does not support resource-level permissions, so AWS requires '*' for that action; we still restricted the action itself."),
    ("Why did /ping not work?", "API Gateway reserves /ping (and /sping) as its own health-check path and replies 'Healthy Connection' without calling the backend. We renamed the route /baseline."),
    ("And why did renaming give a 500?", "API Gateway's permission to invoke the function was scoped to the original path; the new path was not allowed. Re-creating the integration added a new permission."),
    ("Why build a harness in Lambda instead of using k6?", "No CLI or local tools on that account, and an in-region client removes home-network noise. It also let us change configuration and query logs from the same place."),
    ("What does the barrier do?", "threading.Barrier(8) makes all 8 threads wait until the last one arrives, then releases them together, so the requests hit Lambda at the same moment and each needs its own environment."),
    ("What is p50, p95, p99?", "Percentiles: p50 is the median (half the calls faster), p95 means 95% were faster than this value. The harness uses the nearest-rank method; the workbook's MEDIAN averages the two middle values, so 8-sample cold medians can differ slightly."),
    ("Where does the 18 ms floor come from?", "Network inside the region plus API Gateway processing plus Lambda invoke overhead; the handler itself takes about 1.5 ms (CloudWatch)."),
    ("What did each experiment cost?", "All together about $0.30 at list price, mostly 236 Rekognition calls; covered by credits. Budgets showed $0.00."),
    ("How do you know the measured cost matches the model?", "Week 2 predicted about $0.0012 per 1,000 for Lambda A and $1.007 for B; we measured $0.0012 and $1.0038. The model over-estimated B's duration (600 vs 189 ms) but that is under 0.4% of the total."),
    ("Is serverless cheaper than Shaadi.com's DB3?", "Not like-for-like (DB3 does joins, reads and campaigns), but the request path costs about $0.0019 per 1,000 on serverless versus $0.133 for DB3 after gp3, which shows how little a simple request costs serverless."),
    ("How would you fix cold starts in production?", "Provisioned concurrency on hot user paths, SnapStart for Python, fewer/lighter imports, clients created at module level, and asynchronous designs where users do not wait (moderation)."),
    ("How would you handle the 2020-style spike on serverless?", "Queue work with SQS, request quota increases ahead of peaks, alarm on Throttles, use reserved concurrency to protect critical functions."),
    ("What is the strangler-fig pattern?", "Put a new service in front of the old system, write to both, move clients one at a time, switch reads, backfill history, then retire the old system. Shaadi.com used it for DynamoDB messaging."),
    ("Why gp3 instead of gp2?", "gp2 gives 3 IOPS per GB, so more IOPS means buying more disk; gp3 sets IOPS and throughput independently of size, so DB3 got 10,000 IOPS without extra storage, live, via Elastic Volumes."),
    ("What is the 67 billion figure?", "It is the course's headline for the case; we did not find it in any primary source, so we did not use it in calculations."),
    ("What does SAM give you?", "The whole stack as one YAML file: one command creates it, one deletes it, and it documents exactly what was built, including policies, routes, budget and tags."),
    ("Why python3.13 in the template but 3.15 in the console?", "SAM's validated runtime list can lag the console; the code runs on both. Change the Runtime line when SAM supports 3.15."),
    ("How did you pause everything?", "Throttle = reserved concurrency 0 on each function. Every route returns 503; no compute runs; only storage of a few MB remains."),
    ("What would you measure next?", "Real labelled images for moderation accuracy, provisioned concurrency's effect on cold starts and cost, higher concurrency after a quota raise, and an external client from India."),
    ("What did the team members do?", "Sri Sai: case analysis lead, results write-up, report editor. Kavya: exercise design, AWS build and runs. Venkata: diagrams, Logs Insights queries, charts and cost analysis (as stated in the report; confirm with the team).")]
for q, a in qa:
    QA(q, a)

# ====================================================================================== 16. GLOSSARY
H1("16. Glossary")
gl = [("ARN", "Amazon Resource Name, the unique ID of a resource, e.g. arn:aws:dynamodb:ap-south-1:705029438856:table/verdicts."),
      ("boto3", "AWS SDK for Python; included in the Lambda Python runtime."), ("Billed Duration", "Time Lambda charges for, rounded up to 1 ms; includes INIT on cold calls."),
      ("Cold start", "Invocation that needed a new execution environment (INIT ran)."), ("Concurrency", "Number of invocations running at the same moment."),
      ("Execution environment", "Isolated micro-VM that runs one function instance and serves one request at a time."),
      ("GB-second", "Billing unit: memory in GB x seconds of billed time."), ("Handler", "The function Lambda calls per request (lambda_handler)."),
      ("HTTP API", "Lighter, cheaper API Gateway type used here."), ("IAM role", "Identity a service assumes; its policies define permissions."),
      ("Init Duration", "Time of the INIT phase, reported only for cold starts."), ("Integration", "API Gateway link from a route to a backend (our Lambda functions)."),
      ("Least privilege", "Granting only the permissions strictly needed."), ("Logs Insights", "CloudWatch's query language over logs."),
      ("On-demand (DynamoDB)", "Capacity mode billed per request, no planning."), ("Payload format 2.0", "The event structure HTTP APIs send to Lambda."),
      ("Percentile (p95)", "Value below which 95% of measurements fall."), ("Provisioned concurrency", "Paid, pre-warmed environments that eliminate cold starts."),
      ("Quota", "Account limit, e.g. 10 concurrent executions."), ("REPORT line", "Per-invocation log line with durations and memory."),
      ("Reserved concurrency", "Per-function cap; 0 = throttled (paused)."), ("Route", "Method + path in API Gateway, e.g. POST /moderate."),
      ("SAM", "Serverless Application Model: infrastructure as code for serverless."), ("Stage", "A deployment of an API; $default with auto-deploy."),
      ("Strangler fig", "Incremental migration pattern via a facade and dual writes."), ("Throttling", "Lambda rejecting invocations above a limit (client sees 503 via HTTP API)."),
      ("Warm start", "Invocation served by an existing idle environment.")]
T([["Term", "Meaning"]] + [list(g) for g in gl], [1.6, 5.4], "Glossary", fs=8.2)

# ====================================================================================== 17. FILE MAP + EVIDENCE
H1("17. Submission file map and evidence")
T([["Path", "Contents"],
   ["202301138_IT457_Group47_Final_Report.pdf", "Final report (18 pages)"],
   ["IT457_G47_Serverless_Results.xlsx", "Raw data + Summary and Cost_Model sheets with live formulas (blue = price inputs)"],
   ["code/", "ping, interest, moderate, loadgen functions; template.yaml; three IAM policies; Logs Insights queries; pilot JS; image generator"],
   ["data/run2/", "coldwarm_raw.csv (696 rows), coldwarm_summary_console.csv, cloudwatch_report_summary.csv, concurrency_summary.csv, concurrency_timeseries_5s.csv, concurrency_status_codes.csv"],
   ["data/run1_pilot/", "Pilot client latencies and workbook"],
   ["screenshots/", "01-14: API, functions, code, DynamoDB, CloudWatch, live responses, budget, integrations, verdicts, S3, metrics"],
   ["figures/", "Figures 6-10 as PNG"], ["build_scripts/", "Scripts that regenerate charts, report and workbook"],
   ["previous_reports/", "Week 1 and Week 2 reports"],
   ["S3 results/ (in AWS)", "Raw CSVs of runs 20261112T194146, 194523, 194909, 195330"]], [2.4, 4.6], "Where everything is")
for f, c in [("11_live_api_responses.jpg", "Live responses from the three routes"),
             ("13_ping_throttles_concurrency.jpg", "E3 evidence: throttles up to 8,581/min, peak concurrency 9, zero function errors"),
             ("10_dynamodb_verdicts.jpg", "Verdicts stored by Lambda B"),
             ("08_lambda_functions_4.jpg", "The four functions"),
             ("09_api_integrations.jpg", "API Gateway integrations (ping, moderate, interest)"),
             ("07_budget_5usd.jpg", "Budget alert healthy at $0.00")]:
    F(SHOT + f, c, 6.2, maxh=3.5)

doc = Doc(OUT, pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch, topMargin=0.75 * inch, bottomMargin=0.75 * inch,
          title="IT-457 Group 47 - Complete Project Guide (Shaadi.com serverless project)",
          author="Group 47: Sri Sai Madhava Teja Yanduri, Kavya Chauhan, Venkata L Subramanyam")
doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(0.75 * inch, 0.75 * inch, 7 * inch, 9.7 * inch, id="f")], onPage=page)])
doc.multiBuild(story)
print("built", OUT)
