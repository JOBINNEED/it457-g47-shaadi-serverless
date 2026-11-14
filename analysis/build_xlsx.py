"""IT457 G47 results workbook: raw data + formula-driven summaries, cost model and charts."""
import csv
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

D = "/home/claude/poc/data/run2"
OUT = "/home/claude/final/IT457_G47_Serverless_Results.xlsx"
F = "Arial"
H, HF = Font(name=F, bold=True, color="FFFFFF"), PatternFill("solid", fgColor="1F4E78")
BLUE, YEL, BOLD = Font(name=F, color="0000FF"), PatternFill("solid", fgColor="FFF2CC"), Font(name=F, bold=True)
thin = Side(style="thin", color="BFBFBF")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
wb = Workbook()


def header(ws, row, cols, start=1):
    for i, c in enumerate(cols, start):
        cell = ws.cell(row=row, column=i, value=c)
        cell.font, cell.fill, cell.border = H, HF, BOX
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def num(v):
    if v in ("True", "False"):
        return 1 if v == "True" else 0
    try:
        return float(v) if "." in v else int(v)
    except (ValueError, TypeError):
        return v if v != "" else None


def load(ws, path, note):
    rows = list(csv.reader(open(path)))
    header(ws, 1, rows[0])
    for r, row in enumerate(rows[1:], 2):
        for c, v in enumerate(row, 1):
            ws.cell(r, c, num(v))
    ws.freeze_panes = "A2"
    ncol = len(rows[0])
    ws.cell(1, ncol + 2, "Source").font = BOLD
    for i, line in enumerate(note, 2):
        ws.cell(i, ncol + 2, line)
    for i in range(1, ncol + 1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = 15
    return len(rows)


# ---- raw sheets
raw = wb.active
raw.title = "E1E2_Client_Raw"
N = load(raw, f"{D}/coldwarm_raw.csv", [
    "shaadi-loadgen run 20261112T194523 (ap-south-1). For each function and memory: 8 calls released together (cold_burst),",
    "then 50 sequential calls (warm_sequential). cold = the function's own coldStart flag (1 = cold). ms = client latency incl. API Gateway.",
    "rekognition_ms = time of the DetectModerationLabels call inside shaadi-moderate."])
cwr = wb.create_sheet("CloudWatch_Summary")
load(cwr, f"{D}/cloudwatch_report_summary.csv", [
    "Logs Insights over REPORT lines (run 20261112T195330, 10,954 lines). experiment cw = E1/E2 window, conc = E3 window.",
    "Billed duration of a cold call = Init Duration + handler time (INIT is billed since Aug 2025)."])
cs = wb.create_sheet("E3_Concurrency")
load(cs, f"{D}/concurrency_summary.csv", ["Run 20261112T194909: closed-loop load on GET /baseline at 512 MB, 60 s per level.",
                                          "Non-200 responses were all HTTP 503 (Lambda throttling via API Gateway).",
                                          "Served throughput ~100 req/s = 10 x account concurrency quota (10)."])
ts = wb.create_sheet("E3_Timeseries_5s")
load(ts, f"{D}/concurrency_timeseries_5s.csv", ["Same run, aggregated into 5-second windows (computed from 34,775 raw rows)."])

# ---- summary with formulas over raw
sm = wb.create_sheet("Summary", 0)
sm["A1"] = "Shaadi.com serverless PoC - cold start, memory, concurrency and cost (IT-457 Group 47)"
sm["A1"].font = Font(name=F, bold=True, size=14)
sm["A2"] = "ap-south-1, Python 3.15, HTTP API ypq1jax2t5. All figures below are formulas over the raw sheets."
cols = ["Function", "Memory (MB)", "Cold starts", "Cold mean (ms)", "Cold median (ms)", "Warm mean (ms)", "Warm median (ms)",
        "Cold / warm (median)", "Init p50 (ms, CW)", "Warm billed mean (ms, CW)", "Compute $ per 1,000 warm"]
header(sm, 4, cols)
T, M, PH, CO, MS = (f"E1E2_Client_Raw!${c}$2:${c}${N}" for c in "ABCFG")
r = 5
for t, cwname in [("ping", "ping"), ("interest", "interest-api"), ("moderate", "moderate")]:
    for mem in [128, 256, 512, 1024]:
        sm.cell(r, 1, t)
        sm.cell(r, 2, mem)
        sm.cell(r, 3, f'=COUNTIFS({T},A{r},{M},B{r},{PH},"cold_burst",{CO},1)')
        sm.cell(r, 4, f'=AVERAGEIFS({MS},{T},A{r},{M},B{r},{PH},"cold_burst",{CO},1)')
        sm.cell(r, 5, f'=MEDIAN(IF(({T}=A{r})*({M}=B{r})*({PH}="cold_burst")*({CO}=1),{MS}))')
        sm.cell(r, 6, f'=AVERAGEIFS({MS},{T},A{r},{M},B{r},{PH},"warm_sequential")')
        sm.cell(r, 7, f'=MEDIAN(IF(({T}=A{r})*({M}=B{r})*({PH}="warm_sequential"),{MS}))')
        sm.cell(r, 8, f"=E{r}/G{r}")
        cwk = "CloudWatch_Summary!"
        sm.cell(r, 9, f'=SUMIFS({cwk}$G:$G,{cwk}$A:$A,"cw",{cwk}$B:$B,"{cwname}",{cwk}$C:$C,B{r},{cwk}$D:$D,"cold")')
        sm.cell(r, 10, f'=SUMIFS({cwk}$K:$K,{cwk}$A:$A,"cw",{cwk}$B:$B,"{cwname}",{cwk}$C:$C,B{r},{cwk}$D:$D,"warm")')
        sm.cell(r, 11, f"=1000*J{r}/1000*B{r}/1024*Cost_Model!$B$5")
        for c, fmt in zip(range(3, 12), ["0", "0", "0", "0.0", "0.0", '0.0"x"', "0", "0.00", "$0.0000000"]):
            sm.cell(r, c).number_format = fmt
        for c in range(1, 12):
            sm.cell(r, c).border = BOX
        r += 1
# array formulas for MEDIAN(IF())
from openpyxl.worksheet.formula import ArrayFormula
for rr in range(5, 17):
    for col in ("E", "G"):
        f = sm[f"{col}{rr}"].value
        sm[f"{col}{rr}"] = ArrayFormula(f"{col}{rr}", f)
sm.row_dimensions[4].height = 45
for col, w in zip("ABCDEFGHIJK", [11, 10, 9, 11, 11, 11, 11, 11, 11, 13, 15]):
    sm.column_dimensions[col].width = w
sm["A18"] = "Reading: cold calls cost 10-60x a warm call; more memory shortens CPU-bound start-up (interest API) but not the Rekognition wait."
sm["A20"] = "Note: MEDIAN averages the two middle values (8 cold samples), so it can differ from the nearest-rank p50 in the report and harness output."
sm["A19"] = "E3: served throughput capped at ~100 req/s (10 x quota 10); see E3_Concurrency."

# ---- cost model
cm = wb.create_sheet("Cost_Model", 1)
cm["A1"] = "Cost per 1,000 requests (list prices, USD) - blue cells are inputs"
cm["A1"].font = Font(name=F, bold=True, size=13)
header(cm, 3, ["Price input", "Value", "Unit / source"])
inputs = [("Lambda requests", 0.20, "USD per 1M requests"), ("Lambda compute (x86)", 0.0000166667, "USD per GB-second"),
          ("API Gateway HTTP API", 1.00, "USD per 1M requests"), ("DynamoDB on-demand write", 0.625, "USD per 1M WRU"),
          ("Rekognition DetectModerationLabels", 0.001, "USD per image"), ("S3 GET", 0.0004, "USD per 1,000 requests")]
for i, (n, v, s) in enumerate(inputs, 4):
    cm.cell(i, 1, n)
    c = cm.cell(i, 2, v)
    c.font, c.fill = BLUE, YEL
    c.number_format = "0.0000000000" if v < 0.0001 else "0.0000"
    cm.cell(i, 3, s)
header(cm, 11, ["Function", "Memory (MB)", "Warm billed mean (ms)", "Compute", "Lambda requests", "API Gateway", "DynamoDB",
                "Rekognition + S3", "Total $ per 1,000", "Share of total: Rekognition"])
for k, (t, mem, ddb, rek) in enumerate([("ping", 128, 0, 0), ("interest", 512, 1, 0), ("moderate", 512, 1, 1), ("moderate", 128, 1, 1)]):
    r = 12 + k
    cm.cell(r, 1, t)
    cm.cell(r, 2, mem)
    cm.cell(r, 3, f"=INDEX(Summary!$J$5:$J$16,MATCH(1,(Summary!$A$5:$A$16=A{r})*(Summary!$B$5:$B$16=B{r}),0))")
    cm[f"C{r}"] = ArrayFormula(f"C{r}", cm[f"C{r}"].value)
    cm.cell(r, 4, f"=1000*C{r}/1000*B{r}/1024*$B$5")
    cm.cell(r, 5, "=1000*$B$4/1000000")
    cm.cell(r, 6, "=1000*$B$6/1000000")
    cm.cell(r, 7, f"={ddb}*1000*$B$7/1000000")
    cm.cell(r, 8, f"={rek}*(1000*$B$8+$B$9)")
    cm.cell(r, 9, f"=SUM(D{r}:H{r})")
    cm.cell(r, 10, f"=IF(I{r}=0,0,{rek}*1000*$B$8/I{r})")
    for c, fmt in zip(range(3, 11), ["0.00", "$0.0000000", "$0.0000", "$0.0000", "$0.000000", "$0.0000", "$0.0000", "0.0%"]):
        cm.cell(r, c).number_format = fmt
    for c in range(1, 11):
        cm.cell(r, c).border = BOX
cm["A17"] = "Week 2 model for comparison: Lambda A about $0.0012; Lambda B about $1.007 (assumed 512 MB, 600 ms)."
cm.column_dimensions["A"].width = 32
for col in "BCDEFGHIJ":
    cm.column_dimensions[col].width = 14
cm.row_dimensions[11].height = 45

# ---- charts on Summary
bar = BarChart()
bar.type = "col"
bar.title = "Cold vs warm median latency (ms)"
bar.add_data(Reference(sm, min_col=5, max_col=5, min_row=4, max_row=16), titles_from_data=True)
bar.add_data(Reference(sm, min_col=7, max_col=7, min_row=4, max_row=16), titles_from_data=True)
bar.set_categories(Reference(sm, min_col=1, max_col=2, min_row=5, max_row=16))
bar.y_axis.scaling.logBase = 10
bar.x_axis.delete = False
bar.y_axis.delete = False
bar.height, bar.width = 9, 24
sm.add_chart(bar, "A22")
cc = BarChart()
cc.type = "col"
cc.grouping = "stacked"
cc.overlap = 100
cc.title = "E3: served (200) vs throttled (503) requests"
cc.add_data(Reference(cs, min_col=4, max_col=5, min_row=1, max_row=4), titles_from_data=True)
cc.set_categories(Reference(cs, min_col=2, min_row=2, max_row=4))
cc.x_axis.title = "Virtual users"
cc.x_axis.delete = False
cc.y_axis.delete = False
cc.height, cc.width = 8, 14
cs.add_chart(cc, "A8")

for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            f = c.font
            c.font = Font(name=F, bold=f.bold, italic=f.italic, size=f.size, color=f.color)
wb.save(OUT)
print("saved", OUT)
