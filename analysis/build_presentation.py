"""IT-457 G47 presentation guide and demo runbook (PDF)."""
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

LIB = "/usr/share/fonts/truetype/liberation/"
for n, f in [("Sans", "Regular"), ("Sans-B", "Bold"), ("Sans-I", "Italic"), ("Sans-BI", "BoldItalic")]:
    pdfmetrics.registerFont(TTFont(n, LIB + f"LiberationSans-{f}.ttf"))
pdfmetrics.registerFont(TTFont("Mono", LIB + "LiberationMono-Regular.ttf"))
pdfmetrics.registerFontFamily("Sans", normal="Sans", bold="Sans-B", italic="Sans-I", boldItalic="Sans-BI")

OUT = "/home/claude/guide/IT457_G47_Presentation_Guide.pdf"
SH = "/home/claude/guide/shots/"
INK, ACC, GOLD = colors.HexColor("#1f2933"), colors.HexColor("#1F4E78"), colors.HexColor("#B7791F")
body = ParagraphStyle("b", fontName="Sans", fontSize=9.6, leading=13.4, spaceAfter=5, textColor=INK)
small = ParagraphStyle("s", parent=body, fontSize=8.3, leading=10.8, spaceAfter=0)
smallb = ParagraphStyle("sb", parent=small, fontName="Sans-B")
h1 = ParagraphStyle("h1", fontName="Sans-B", fontSize=17, leading=21, spaceAfter=8, textColor=ACC)
h2 = ParagraphStyle("h2", fontName="Sans-B", fontSize=12, leading=15.5, spaceBefore=9, spaceAfter=4, textColor=INK)
cap = ParagraphStyle("c", fontName="Sans-I", fontSize=8, leading=10, textColor=colors.HexColor("#555"), alignment=TA_CENTER, spaceBefore=3, spaceAfter=9)
bul = ParagraphStyle("bu", parent=body, leftIndent=14, bulletIndent=3, spaceAfter=2.5)
mono = ParagraphStyle("m", fontName="Mono", fontSize=7.6, leading=9.6)
story = []

API = "https://ypq1jax2t5.execute-api.ap-south-1.amazonaws.com"
DEMO = API + "/demo"
C = "https://ap-south-1.console.aws.amazon.com"
R = "?region=ap-south-1"
LINK = {
    "demo": DEMO,
    "signin": "https://705029438856.signin.aws.amazon.com/console",
    "rg": C + "/resource-groups/group/it457-g47-shaadi-project" + R,
    "lambda": C + "/lambda/home" + R + "#/functions",
    "fn": lambda f, t="code": C + "/lambda/home" + R + f"#/functions/{f}?tab={t}",
    "conc": lambda f: C + "/lambda/home" + R + f"#/functions/{f}/edit/concurrency?tab=configure",
    "routes": C + "/apigateway/main/develop/routes?api=ypq1jax2t5&region=ap-south-1",
    "integ": C + "/apigateway/main/develop/integrations/manage?api=ypq1jax2t5&region=ap-south-1",
    "ddb": lambda t: C + "/dynamodbv2/home" + R + f"#item-explorer?table={t}",
    "s3": lambda p: C + "/s3/buckets/it457-g47-shaadi-705029438856" + R + f"&prefix={p}",
    "logs": C + "/cloudwatch/home" + R + "#logsV2:log-groups$3FlogGroupNameFilter$3Dshaadi",
    "insights": C + "/cloudwatch/home" + R + "#logsV2:logs-insights",
    "iam": "https://us-east-1.console.aws.amazon.com/iam/home#/roles?search=shaadi",
    "budget": "https://us-east-1.console.aws.amazon.com/billing/home#/budgets",
    "quota": C + "/servicequotas/home/services/lambda/quotas",
    "repo": "https://github.com/JOBINNEED/it457-g47-shaadi-serverless",
}


def P(t, s=body):
    if s in (h2,):
        story.append(CondPageBreak(1.1 * inch))
    story.append(Paragraph(t, s))


def H1(t, brk=True):
    if brk:
        story.append(PageBreak())
    story.append(Paragraph(t, h1))


def B(items):
    for t in items:
        story.append(Paragraph(t, bul, bulletText="•"))


def N(items):
    for i, t in enumerate(items, 1):
        story.append(Paragraph(t, bul, bulletText=f"{i}."))


def a(url, text=None):
    return f'<link href="{url}" color="#1F4E78"><u>{text or url}</u></link>'


def T(rows, widths, fs=8.2, header=True, title=None):
    st_cell = ParagraphStyle("x", parent=small, fontSize=fs, leading=fs + 2.4)
    data = [[Paragraph(str(c), smallb if (header and i == 0) else st_cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * inch for w in widths], repeatRows=1 if header else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8C8C8")),
          ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#8a8a8a")), ("TOPPADDING", (0, 0), (-1, -1), 3),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("LEFTPADDING", (0, 0), (-1, -1), 4)]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E3EAF2")), ("LINEBELOW", (0, 0), (-1, 0), 0.9, ACC)]
    t.setStyle(TableStyle(st))
    story.append(t)
    story.append(Spacer(1, 8))


def box(title, lines, bg="#FFF8E6", edge=GOLD):
    inner = [Paragraph(f"<b>{title}</b>", ParagraphStyle("bt", parent=body, textColor=edge, spaceAfter=3))]
    inner += [Paragraph(l, ParagraphStyle("bl", parent=body, fontSize=9.2, leading=12.6, spaceAfter=3)) for l in lines]
    t = Table([[inner]], colWidths=[7 * inch])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)), ("BOX", (0, 0), (-1, -1), 0.8, edge),
                           ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(KeepTogether([t, Spacer(1, 8)]))


def shot(path, text, width=6.8, maxh=3.8):
    w, h = PILImage.open(path).size
    ww, hh = width * inch, width * inch * h / w
    if hh > maxh * inch:
        hh = maxh * inch
        ww = hh * w / h
    story.append(KeepTogether([Image(path, width=ww, height=hh), Paragraph(text, cap)]))


def step(title, link, show, click, say, expect, fail):
    rows = [["Open", a(link) if link.startswith("http") else link], ["On screen", show], ["Do", click],
            ["Say", f"<i>{say}</i>"], ["Expect", expect], ["If it fails", fail]]
    st_cell = ParagraphStyle("x", parent=small, fontSize=8.4, leading=11)
    data = [[Paragraph(f"<b>{title}</b>", ParagraphStyle("st", parent=body, textColor=colors.white, fontSize=10)), ""]] + \
           [[Paragraph(f"<b>{k}</b>", st_cell), Paragraph(v, st_cell)] for k, v in rows]
    t = Table(data, colWidths=[1.0 * inch, 6.0 * inch])
    t.setStyle(TableStyle([("SPAN", (0, 0), (1, 0)), ("BACKGROUND", (0, 0), (1, 0), ACC), ("BOX", (0, 0), (-1, -1), 0.7, ACC),
                           ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#D0D7E0")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("BACKGROUND", (0, 4), (1, 4), colors.HexColor("#FFF8E6")), ("TOPPADDING", (0, 0), (-1, -1), 3.5),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5)]))
    story.append(KeepTogether([t, Spacer(1, 10)]))


def page(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setFont("Sans", 7.5)
        canvas.setFillColor(colors.HexColor("#666"))
        canvas.drawString(0.75 * inch, 10.62 * inch, "IT-457 Group 47  |  Presentation guide and demo runbook")
        canvas.drawRightString(7.75 * inch, 10.62 * inch, "Live page: " + DEMO)
        canvas.setStrokeColor(colors.HexColor("#C8C8C8"))
        canvas.line(0.75 * inch, 10.56 * inch, 7.75 * inch, 10.56 * inch)
        canvas.drawCentredString(4.25 * inch, 0.5 * inch, str(doc.page))
    canvas.restoreState()


# ===================================================================== COVER
story.append(Spacer(1, 1.3 * inch))
story.append(Paragraph("Presentation Guide and Demo Runbook", ParagraphStyle("t", fontName="Sans-B", fontSize=26, leading=32, alignment=TA_CENTER, textColor=ACC)))
story.append(Paragraph("IT-457 Cloud Computing | Group 47 | Shaadi.com serverless project",
                       ParagraphStyle("t2", fontName="Sans", fontSize=13, leading=18, alignment=TA_CENTER, spaceBefore=8)))
story.append(Spacer(1, 0.4 * inch))
story.append(Paragraph("Everything you open, click and say in front of the panel, in order, with every link. "
                       "Any of the three of us can run the demo from their own laptop.",
                       ParagraphStyle("t3", parent=body, alignment=TA_CENTER, fontSize=11, leading=15)))
story.append(Spacer(1, 0.4 * inch))
box("The one link you need", [f"<font size=12><b>{a(DEMO)}</b></font>",
                              "Opens the presentation page: overview, case, architecture, live demo with outputs, results, cost and every fallback link. "
                              "No login needed for the page itself; log in to AWS only for the console fallbacks."], bg="#EEF4FA", edge=ACC)
story.append(Spacer(1, 0.3 * inch))
T([["Name", "Student ID", "AWS console user", "Presents"],
   ["Sri Sai Madhava Teja Yanduri", "202301138", "root (owner)", "Opening, case, wrap-up"],
   ["Kavya Chauhan", "202301116", "kavya", "Architecture and live demo"],
   ["Venkata L Subramanyam", "202301280", "venkat", "Results and cost"]], [2.3, 1.0, 1.4, 2.3])

# ===================================================================== 1 LINKS
H1("1. All links at a glance")
P("Bookmark these. Console links work after you sign in (step 2.2) with region <b>Asia Pacific (Mumbai)</b>.")
T([["What", "Link"],
   ["Presentation page (main screen)", a(LINK["demo"])],
   ["AWS sign-in for IAM users (kavya, venkat)", a(LINK["signin"])],
   ["Whole project in one place (Resource Group)", a(LINK["rg"])],
   ["All Lambda functions", a(LINK["lambda"])],
   ["shaadi-ping code / metrics", a(LINK["fn"]("shaadi-ping"), "code") + " | " + a(LINK["fn"]("shaadi-ping", "monitoring"), "metrics (throttles, concurrency)")],
   ["shaadi-interest-api code", a(LINK["fn"]("shaadi-interest-api"))],
   ["shaadi-moderate code", a(LINK["fn"]("shaadi-moderate"))],
   ["shaadi-loadgen (experiment harness)", a(LINK["fn"]("shaadi-loadgen"))],
   ["shaadi-demo (serves the presentation page)", a(LINK["fn"]("shaadi-demo"))],
   ["API Gateway routes / integrations", a(LINK["routes"], "routes") + " | " + a(LINK["integ"], "integrations")],
   ["DynamoDB verdicts / Interests", a(LINK["ddb"]("verdicts"), "verdicts") + " | " + a(LINK["ddb"]("Interests"), "Interests")],
   ["S3 test photos / experiment CSVs", a(LINK["s3"]("photos/"), "photos/") + " | " + a(LINK["s3"]("results/"), "results/")],
   ["CloudWatch log groups / Logs Insights", a(LINK["logs"], "log groups") + " | " + a(LINK["insights"], "Logs Insights")],
   ["IAM roles (one per function)", a(LINK["iam"])],
   ["AWS Budgets ($5 alert)", a(LINK["budget"])],
   ["Lambda quotas (concurrency 10)", a(LINK["quota"])],
   ["GitHub repository (private)", a(LINK["repo"])],
   ["Raw API (for curl)", a(API + "/baseline", API + "/baseline")]], [2.4, 4.6], fs=7.8)

# ===================================================================== 2 BEFORE
H1("2. Before the presentation")
P("2.1 The day before (owner: Sri Sai)", h2)
N(["Make sure the functions are <b>not throttled</b>. Open " + a(LINK["demo"], "the presentation page") + ", go to <b>4 Live demo</b>, click <b>Call once</b>. "
   "HTTP 200 = running. HTTP 503 = still paused: un-throttle as in step 2.3.",
   "Check the budget is still $0-1: " + a(LINK["budget"], "AWS Budgets") + ".",
   "Download the report and guides to the laptop (offline copies in case Wi-Fi fails).",
   "Each presenter reads their section of this guide and the 'Questions' section of the Complete Guide."])
P("2.2 Signing in (Kavya / Venkata)", h2)
N(["Open " + a(LINK["signin"]) + ". The account ID 705029438856 is pre-filled.",
   "IAM user name: <b>kavya</b> or <b>venkat</b>, plus the password Sri Sai set for you.",
   "Top-right region menu: choose <b>Asia Pacific (Mumbai) ap-south-1</b>. Most 'nothing here' problems are the wrong region."])
P("2.3 If the stack is paused: un-throttle (about 1 minute)", h2)
P("For each of <b>shaadi-ping, shaadi-interest-api, shaadi-moderate, shaadi-demo</b> open its concurrency page, select "
  "<i>Use unreserved account concurrency</i>, click <b>Save</b>:")
T([["Function", "Direct link to its concurrency setting"]] +
  [[f, a(LINK["conc"](f))] for f in ["shaadi-demo", "shaadi-ping", "shaadi-interest-api", "shaadi-moderate"]], [1.7, 5.3], fs=7.6)
P("Leave <b>shaadi-loadgen</b> throttled; it is only needed to re-run experiments. Un-throttle shaadi-demo first, otherwise the page itself returns 503.")
P("2.4 30 minutes before", h2)
N(["Open the presentation page full screen (Cmd+Ctrl+F on Mac). Arrow keys switch tabs.",
   "In a second browser window, sign in to AWS and open three tabs: " + a(LINK["fn"]("shaadi-moderate"), "shaadi-moderate code") + ", " +
   a(LINK["ddb"]("verdicts"), "DynamoDB verdicts") + ", " + a(LINK["fn"]("shaadi-ping", "monitoring"), "shaadi-ping metrics") + ".",
   "Do <b>not</b> click around the Live demo yet if you want the first call to show a cold start. (The Cold start lab can force one at any time anyway.)",
   "Zoom the browser to 110-125% so the panel can read it."])

# ===================================================================== 3 RUN SHEET
H1("3. Run sheet (about 12 minutes plus questions)")
T([["Time", "Presenter", "Page / tab", "Content"],
   ["0:00-1:00", "Sri Sai", "Tab 1 Overview", "60-second pitch, key numbers"],
   ["1:00-3:30", "Sri Sai", "Tab 2 Case", "Shaadi.com, problems P1-P4, DB3 cost per 1,000"],
   ["3:30-5:00", "Kavya", "Tab 3 Architecture", "What we built, request flow, least privilege"],
   ["5:00-8:30", "Kavya", "Tab 4 Live demo", "Baseline cold/warm, interest, moderation, cold start lab"],
   ["8:30-10:30", "Venkata", "Tab 5 Results", "E1/E2 memory, INIT billing, E3 throttling at 100 req/s"],
   ["10:30-11:30", "Venkata", "Tab 6 Cost", "Cost per 1,000; calculator; Rekognition is 99.6%"],
   ["11:30-12:00", "Sri Sai", "Tab 1 / conclusion", "Lessons: serverless is cheap, plan for cold starts and quotas"],
   ["Questions", "All", "Tab 7 Links + console", "Open the console page that proves the answer"]], [0.9, 0.9, 1.5, 3.7])

# ===================================================================== 4 PAGE BY PAGE
H1("4. Page by page: what to open, click and say")
step("Tab 1 - Overview (Sri Sai)", LINK["demo"] + "#overview",
     "Title, team, eight key-number cards, presentation order.",
     "Nothing to click. Point at the cards while you speak.",
     "Our case is Shaadi.com, India's largest matrimony site. It moved to AWS and runs photo moderation on serverless: S3, Lambda and Rekognition. "
     "We analysed the case and then rebuilt that serverless path ourselves in Mumbai, and measured what serverless really costs and where it breaks. "
     "In short: cold starts cost 10 to 60 times a warm call, moderation costs about a dollar per thousand photos and 99.6% of that is Rekognition, "
     "and our account's quota capped us at 100 requests per second.",
     "Page loads in under a second.", "If the page shows 503, shaadi-demo is throttled: step 2.3. Meanwhile present from the final report PDF.")
step("Tab 2 - Case (Sri Sai)", LINK["demo"] + "#case",
     "Company facts, P1-P4 table, DB3 cost per 1,000 table.",
     "Walk down the P1-P4 rows; finish on P4 (highlighted).",
     "Every AWS change broke one coupling: compute to procurement, IOPS to disk size with gp3, relational engine to access pattern with DynamoDB, "
     "and moderation to people with Rekognition. Their gp3 move cut DB3's cost per thousand requests from 18 to 13 cents. P4 is the one we rebuilt.",
     "-", "Static content; cannot fail.")
step("Tab 3 - Architecture (Kavya)", LINK["demo"] + "#arch",
     "Clickable diagram and route table.",
     "Optionally click the <b>shaadi-moderate</b> box: it opens the function code in the console (must be signed in).",
     "A client calls an HTTP API in API Gateway with three routes, each backed by a Lambda function in Python 3.15. The baseline does nothing, so it measures pure overhead. "
     "The interest API writes to DynamoDB like the real 'send interest'. The moderation function asks Rekognition to read the photo straight from S3, "
     "so the image never passes through Lambda, and stores the verdict. Each function has its own role with only the permissions it needs.",
     "Console tab opens on the code.", "If the console asks to log in, use step 2.2; carry on with the page.")
step("Tab 4A - Baseline (Kavya)", LINK["demo"] + "#demo",
     "Card A with 'Call once' and 'Call 5 times'.",
     "Click <b>Call 5 times</b>.",
     "The first call had to start a new execution environment, a cold start, so it took a few hundred milliseconds. The next four reused it: warm, tens of milliseconds from here.",
     "First row COLD (about 250-700 ms), then WARM (about 40-90 ms from India). Session log fills.",
     "If all WARM: someone already called it; use the Cold start lab (4D). If 503: throttled, step 2.3.")
step("Tab 4B - Send interest (Kavya)", LINK["demo"] + "#demo",
     "Card B with three inputs.",
     "Type a name in the first box (optional), click <b>Send</b>, then <b>Show latest in DynamoDB</b>.",
     "This is the portal's 'send interest'. The function saved it to DynamoDB with a random ID and returned 201 Created. Here it is in the table.",
     "HTTP 201, the saved item, and the newest row in the table list.",
     "If 500: check " + a(LINK["fn"]("shaadi-interest-api", "monitoring"), "its metrics/logs") + "; show screenshot 04 in the report.")
step("Tab 4C - Photo moderation (Kavya)", LINK["demo"] + "#demo",
     "Card C with a photo picker and preview.",
     "Pick any photo, click <b>Moderate</b>, then <b>Latest verdicts</b>.",
     "Rekognition read the photo directly from S3 and returned moderation labels; none here, so it is approved. About 200 ms of the call is Rekognition itself. "
     "Our rule: a label at 80% or more rejects, 60 to 80 goes to human review, as Shaadi.com keeps humans for borderline cases. Every verdict is stored with its timing.",
     "Verdict APPROVED, Rekognition time about 150-250 ms, table of latest verdicts.",
     "If the photo preview is blank but moderation works, it is only the preview; carry on.")
step("Tab 4D - Cold start lab (Kavya)", LINK["demo"] + "#demo",
     "Function picker and two buttons.",
     "Choose <b>shaadi-interest-api</b> (most dramatic), click <b>Force cold start, then call 1 + 5</b>. Wait about 5 s.",
     "Any configuration change makes Lambda retire its environments. The first call now pays the INIT phase: starting Python and importing the AWS SDK. "
     "For this function that is over a second, and since 2025 that INIT time is billed. The next five are warm. This is exactly how our harness forced 95 cold starts.",
     "Call 1 COLD and much longer (about 0.7-2 s), calls 2-6 WARM.",
     "If the message shows an error instead of a nonce, shaadi-demo lacks permission: show Tab 5 results instead.")
step("Tab 5 - Results (Venkata)", LINK["demo"] + "#results",
     "Cold vs warm chart and table; cold-start internals; concurrency chart and table.",
     "Point at the purple bars (interest API) falling with memory, then the green ones (moderation) staying flat; then the concurrency chart.",
     "Lambda gives CPU in proportion to memory. Start-up work is CPU, so the interest API's cold start fell from 1,950 to 699 milliseconds. Moderation mostly waits for Rekognition, "
     "so more memory only raised its cost. In the load test, served throughput stopped at 100 requests per second whatever we offered: Lambda allows ten times the "
     "concurrency quota per second, and our new account's quota is ten. Everything above that came back as HTTP 503, about 60 percent.",
     "-", "Static; cannot fail. Optional proof: open " + a(LINK["fn"]("shaadi-ping", "monitoring"), "shaadi-ping metrics") + " (Throttles graph).")
step("Tab 6 - Cost (Venkata)", LINK["demo"] + "#cost",
     "Cost per 1,000 table and calculator.",
     "Type 1000000 requests, choose 128 then 1024 MB, click <b>Calculate</b> each time.",
     "Per thousand requests, the baseline costs a tenth of a cent, the interest API two tenths, moderation about a dollar, of which 99.6% is Rekognition. "
     "Our Week 2 model predicted 0.0012 and 1.007 dollars; we measured 0.0012 and 1.0038. So with serverless, savings come from fewer ML calls, not from tuning Lambda.",
     "Calculator shows monthly cost; moderation dominated by Rekognition.", "Static; cannot fail.")
step("Close (Sri Sai)", LINK["demo"] + "#overview",
     "Back to Overview.",
     "Return to Tab 1.",
     "Serverless gave us an API in minutes that costs fractions of a cent per thousand requests. Its real costs are cold starts, which are now billed, and quotas that turn a spike into 503s. "
     "Both are manageable: right-size memory, provisioned concurrency on hot paths, queues for spikes, and quota planning. Thank you.",
     "-", "-")

# ===================================================================== 5 CONSOLE DEEP DIVE
H1("5. If the panel asks to see the console")
P("Open these only when asked. Each row says what proves what.")
T([["Question", "Open", "Show"],
   ["Show us the code", a(LINK["fn"]("shaadi-moderate"), "shaadi-moderate code"), "Rekognition call with S3Object (no download); verdict rules; PutItem to verdicts"],
   ["What memory/timeout?", a(LINK["fn"]("shaadi-moderate", "configure"), "Configuration tab"), "General configuration: memory, timeout; Environment variables BUCKET, TABLE_NAME"],
   ["Prove the cold starts", a(LINK["logs"], "CloudWatch log groups"), "Open /aws/lambda/shaadi-interest-api, newest stream: REPORT line with Init Duration (cold) vs without (warm)"],
   ["Prove the throttling", a(LINK["fn"]("shaadi-ping", "monitoring"), "shaadi-ping Monitor"), "Throttles graph spike (up to 8,581/min) and Concurrent executions max 9 on 12-13 Nov (set range to 1w)"],
   ["Why only 10?", a(LINK["quota"], "Lambda quotas"), "Concurrent executions: applied value 10 (default 1,000)"],
   ["Where are results?", a(LINK["s3"]("results/"), "S3 results/"), "CSV per run: coldwarm, concurrency, cloudwatch report lines"],
   ["Least privilege?", a(LINK["iam"], "IAM roles"), "Open shaadi-moderate-role: inline policy ModeratePhotosAccess, three narrow statements"],
   ["How is the API wired?", a(LINK["routes"], "API routes"), "Routes /baseline, /interest, /moderate, /demo; integrations to each function"],
   ["Data stored?", a(LINK["ddb"]("verdicts"), "DynamoDB verdicts"), "Explore items: every verdict with coldStart and rekognitionMs"],
   ["Cost control?", a(LINK["budget"], "Budgets"), "it457-g47-5usd, $5 monthly, healthy"],
   ["Everything in one place?", a(LINK["rg"], "Resource Group"), "14 resources tagged project=it457-g47"],
   ["Code history?", a(LINK["repo"], "GitHub repo"), "Folders src, infra, experiments, data, docs; commits by each member"]], [1.35, 1.75, 3.9], fs=7.7)
P("How to read a REPORT line live", h2)
story.append(Preformatted("REPORT RequestId: ...  Duration: 552.20 ms  Billed Duration: 1831 ms  Memory Size: 128 MB\n"
                          "        Max Memory Used: 95 MB  Init Duration: 1242.48 ms      <- present only on a cold start", mono))
story.append(Spacer(1, 6))
P("Billed (1,831) is about Init (1,242) + Duration (552): INIT is billed. A warm line has no Init Duration and bills a few ms.")

# ===================================================================== 6 TROUBLESHOOTING
H1("6. Troubleshooting during the presentation")
T([["Symptom", "Cause", "Fix (seconds)"],
   ["Page or calls return 503 Service Unavailable", "Function throttled (paused), or rate limit", "Un-throttle (step 2.3). During a burst it is the 100 req/s limit: that is a result, explain it."],
   ["500 Internal Server Error", "Missing permission or code error", "Show the report screenshots; check the function's Monitor/logs afterwards."],
   ["First call slow (1-2 s)", "Cold start", "That is the point: explain INIT."],
   ["Console shows nothing / 'not found'", "Wrong region", "Region menu: Asia Pacific (Mumbai)."],
   ["Console login refused", "Wrong sign-in page or user", "Use " + a(LINK["signin"], "the account sign-in link") + " with kavya / venkat."],
   ["Photo preview blank", "Preview only (S3 read via demo function)", "Ignore; moderation itself still runs."],
   ["No internet", "-", "Present from the final report PDF and the screenshots folder."]], [1.9, 1.9, 3.2], fs=8)

# ===================================================================== 7 AFTER
H1("7. After the presentation")
P("7.1 Pause again (2 minutes)", h2)
P("Open each function page and click <b>Throttle</b> then <b>Confirm</b> (sets reserved concurrency to 0): " +
  ", ".join(a(LINK["fn"](f), f) for f in ["shaadi-demo", "shaadi-ping", "shaadi-interest-api", "shaadi-moderate"]) +
  ". Check: the presentation page now returns 503.")
P("7.2 Delete after grading", h2)
B(["Lambda: delete shaadi-ping, shaadi-interest-api, shaadi-moderate, shaadi-loadgen, shaadi-demo.",
   "API Gateway: delete shaadi-interest-http-api. DynamoDB: delete Interests and verdicts.",
   "S3: empty, then delete it457-g47-shaadi-705029438856. CloudWatch: delete /aws/lambda/shaadi-* log groups.",
   "IAM: delete the five shaadi-*-role-* roles; consider removing AdministratorAccess from kavya and venkat or deleting those users.",
   "Resource Groups: delete it457-g47-shaadi-project. Budgets: delete it457-g47-5usd (optional)."])
P("7.3 Security note on the IAM users", h2)
P("Both kavya and venkat have <b>AdministratorAccess</b> with console passwords and <b>no MFA</b>. That is full control of the account. "
  "For a short project it works, but turn on MFA for both (IAM, user, Security credentials, Assign MFA device), or swap AdministratorAccess for "
  "ReadOnlyAccess plus permission to change function concurrency, and delete both users after grading.")

# ===================================================================== 8 QUICK ANSWERS
H1("8. Twelve quick answers")
qa = [("What is a cold start?", "A request that needs a new execution environment, so Lambda runs INIT (start runtime, imports, clients) before the handler."),
      ("How did you know?", "The function's own coldStart flag, and Init Duration in the REPORT line, which appears only on cold calls."),
      ("Why does memory help?", "Lambda gives CPU in proportion to memory; start-up is CPU work. Waiting on Rekognition is not, so there it only adds cost."),
      ("Is INIT billed?", "Yes since August 2025: cold Billed Duration = Init + handler time, visible in our REPORT lines."),
      ("Why 100 req/s?", "Lambda allows 10 x the concurrency quota per second; our new account's quota is 10."),
      ("Why 503?", "Lambda throttles with 429 to API Gateway; HTTP APIs return 503 to the client."),
      ("Cost per 1,000?", "Baseline $0.0012, interest $0.0019, moderation $1.0038 (Rekognition $1.00)."),
      ("Did the model match?", "Yes: predicted $0.0012 and $1.007; measured $0.0012 and $1.0038."),
      ("Why /baseline, not /ping?", "API Gateway reserves /ping for its own health check and answers 'Healthy Connection' itself."),
      ("Least privilege?", "One role per function, exact actions on exact ARNs (e.g. read only photos/*, write only verdicts)."),
      ("How would you fix cold starts?", "Provisioned concurrency or SnapStart on hot paths, lighter imports, clients at module level, async where users do not wait."),
      ("What did it cost?", "About $0.30 at list price, covered by credits; $5 budget alert set.")]
T([["Question", "Answer"]] + [[q, x] for q, x in qa], [1.8, 5.2], fs=8.2)

P("Screens you will see", h2)
for f, c in [("demo_overview.png", "Tab 1 Overview"), ("demo_live.png", "Tab 4 Live demo after running the calls"), ("demo_results.png", "Tab 5 Results")]:
    try:
        shot(SH + f, c, 6.6, 3.7)
    except FileNotFoundError:
        pass

doc = BaseDocTemplate(OUT, pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch, topMargin=0.75 * inch, bottomMargin=0.75 * inch,
                      title="IT-457 Group 47 - Presentation Guide and Demo Runbook", author="Group 47")
doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(0.75 * inch, 0.75 * inch, 7 * inch, 9.7 * inch, id="f")], onPage=page)])
doc.build(story)
print("built", OUT)
