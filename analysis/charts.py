"""Charts for the IT457 G47 final report. Reads the run-2 CSVs, writes PNGs to /home/claude/final/fig."""
import csv
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

D = "/home/claude/poc/data/run2"
OUT = "/home/claude/final/fig"
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({"font.family": "Liberation Sans", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titleweight": "bold", "axes.titlesize": 11,
                     "axes.edgecolor": "#555", "axes.labelcolor": "#222", "xtick.color": "#333", "ytick.color": "#333"})
C = {"ping": "#6b7a8f", "interest": "#c026d3", "moderate": "#2f9e44", "accent": "#e8590c", "grid": "#e6e6e6"}
LBL = {"ping": "A: baseline (/baseline)", "interest": "Interest API (/interest)", "moderate": "B: moderation (/moderate)"}
MEM = [128, 256, 512, 1024]


def pct(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(round(p / 100 * (len(v) - 1))))]


raw = list(csv.DictReader(open(f"{D}/coldwarm_raw.csv")))
g = defaultdict(lambda: {"c": [], "w": []})
for r in raw:
    k = (r["target"], int(r["memory_mb"]))
    if r["phase"] == "cold_burst":
        if r["cold"] == "True":
            g[k]["c"].append(float(r["ms"]))
    else:
        g[k]["w"].append(float(r["ms"]))
cw = {(r["function"].replace("-api", ""), int(r["memory_mb"]), r["start_type"]): r
      for r in csv.DictReader(open(f"{D}/cloudwatch_report_summary.csv")) if r["experiment"] == "cw"}


def save(fig, name):
    fig.savefig(f"{OUT}/{name}.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---- Fig 7: client cold p50 vs warm p50 per function and memory
fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.4), sharey=True)
for ax, t in zip(axes, ["ping", "interest", "moderate"]):
    x = range(len(MEM))
    cold = [pct(g[(t, m)]["c"], 50) for m in MEM]
    warm = [pct(g[(t, m)]["w"], 50) for m in MEM]
    ax.bar([i - 0.2 for i in x], cold, 0.4, color=C[t], label="cold (p50)")
    ax.bar([i + 0.2 for i in x], warm, 0.4, color=C[t], alpha=0.35, label="warm (p50)")
    for i, (a, b) in enumerate(zip(cold, warm)):
        ax.text(i - 0.2, a * 1.08, f"{a:.0f}", ha="center", fontsize=7.5)
        ax.text(i + 0.2, b * 1.08, f"{b:.0f}", ha="center", fontsize=7.5)
    ax.set_yscale("log")
    ax.set_ylim(8, 12000)
    ax.set_xticks(list(x), [str(m) for m in MEM])
    ax.set_xlabel("Memory (MB)")
    ax.set_title(LBL[t], fontsize=10)
    ax.grid(axis="y", color=C["grid"], which="both", lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
axes[0].set_ylabel("Client latency, ms (log scale)")
fig.tight_layout()
save(fig, "fig7_cold_warm")

# ---- Fig 8: what a cold start is made of (CloudWatch): init + handler, vs warm billed
fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.3), sharey=True)
for ax, t in zip(axes, ["ping", "interest", "moderate"]):
    init = [float(cw[(t, m, "cold")]["init_p50_ms"]) for m in MEM]
    dur = [float(cw[(t, m, "cold")]["duration_p50_ms"]) for m in MEM]
    warm = [float(cw[(t, m, "warm")]["billed_mean_ms"]) for m in MEM]
    x = range(len(MEM))
    ax.bar([i - 0.2 for i in x], init, 0.4, color=C[t], label="Init Duration, p50 (bar colour)")
    ax.bar([i - 0.2 for i in x], dur, 0.4, bottom=init, color=C["accent"], label="handler, cold call (p50)")
    ax.bar([i + 0.2 for i in x], warm, 0.4, color="#adb5bd", label="billed, warm call (mean)")
    for i in x:
        ax.text(i - 0.2, init[i] + dur[i] + 25, f"{init[i] + dur[i]:.0f}", ha="center", fontsize=7.5)
        ax.text(i + 0.2, warm[i] + 25, f"{warm[i]:.0f}", ha="center", fontsize=7.5)
    ax.set_xticks(list(x), [str(m) for m in MEM])
    ax.set_xlabel("Memory (MB)")
    ax.set_title(LBL[t], fontsize=10)
    ax.grid(axis="y", color=C["grid"], lw=0.6)
    ax.set_axisbelow(True)
axes[0].set_ylabel("Server-side time, ms (CloudWatch)")
axes[2].legend(frameon=False, fontsize=7.5, loc="upper right")
fig.tight_layout()
save(fig, "fig8_init_breakdown")

# ---- Fig 9: Lambda compute cost per 1,000 warm calls vs memory
GBS = 0.0000166667
fig, ax = plt.subplots(figsize=(6.2, 3.2))
for t in ["ping", "interest", "moderate"]:
    cost = [1000 * float(cw[(t, m, "warm")]["billed_mean_ms"]) / 1000 * m / 1024 * GBS for m in MEM]
    ax.plot(MEM, cost, marker="o", color=C[t], label=LBL[t], lw=2)
    ax.annotate(f"${cost[-1]:.6f}", (MEM[-1], cost[-1]), textcoords="offset points", xytext=(6, -3), fontsize=8, color=C[t])
    ax.annotate(f"${cost[0]:.6f}", (MEM[0], cost[0]), textcoords="offset points", xytext=(-8, 7), fontsize=8, color=C[t])
ax.set_xscale("log", base=2)
ax.set_yscale("log")
ax.set_xticks(MEM, [str(m) for m in MEM])
ax.set_xlabel("Memory (MB)")
ax.set_ylabel("USD per 1,000 warm calls\n(Lambda compute only, log)")
ax.grid(color=C["grid"], which="both", lw=0.6)
ax.legend(frameon=False, fontsize=8, loc="upper left")
ax.set_xlim(100, 1500)
fig.tight_layout()
save(fig, "fig9_compute_cost")

# ---- Fig 10: concurrency - offered vs successful throughput, and latency
cs = list(csv.DictReader(open(f"{D}/concurrency_summary.csv")))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.2))
lv = [int(r["virtual_users"]) for r in cs]
ok = [int(r["ok"]) / 60 for r in cs]
bad = [int(r["throttled_or_error"]) / 60 for r in cs]
x = range(len(lv))
a1.bar(x, ok, 0.55, color=C["ping"], label="HTTP 200")
a1.bar(x, bad, 0.55, bottom=ok, color=C["accent"], label="HTTP 503 (throttled)")
a1.axhline(100, color="#222", ls="--", lw=1, label="100 req/s limit (10 x quota of 10)")
for i in x:
    a1.text(i, ok[i] / 2, f"{ok[i]:.0f}/s", ha="center", color="white", fontsize=8.5, fontweight="bold")
    if bad[i]:
        a1.text(i, ok[i] + bad[i] / 2, f"{bad[i]:.0f}/s\n({bad[i] / (ok[i] + bad[i]) * 100:.0f}%)", ha="center", color="white", fontsize=8)
a1.set_xticks(list(x), [f"{v} VU" for v in lv])
a1.set_ylabel("Requests per second (60 s run)")
a1.set_title("Throughput: offered vs served", fontsize=10)
a1.legend(frameon=False, fontsize=8, loc="upper left", bbox_to_anchor=(0, 0.9))
a1.grid(axis="y", color=C["grid"], lw=0.6)
a1.set_axisbelow(True)
a1.set_ylim(0, 300)
ts = list(csv.DictReader(open(f"{D}/concurrency_timeseries_5s.csv")))
for L, col in zip([1, 9, 50], [C["ping"], C["interest"], C["moderate"]]):
    rows = [r for r in ts if int(r["virtual_users"]) == L]
    a2.plot([int(r["window_start_s"]) + 2.5 for r in rows], [float(r["ok_p50_ms"]) for r in rows], marker="o", ms=3, color=col, label=f"{L} VU p50")
    a2.plot([int(r["window_start_s"]) + 2.5 for r in rows], [float(r["ok_p95_ms"]) for r in rows], ls=":", color=col, label=f"{L} VU p95")
a2.set_yscale("log")
from matplotlib.ticker import FixedLocator, ScalarFormatter, NullFormatter
a2.yaxis.set_major_locator(FixedLocator([10, 20, 50, 100, 200, 400]))
a2.yaxis.set_major_formatter(ScalarFormatter())
a2.yaxis.set_minor_formatter(NullFormatter())
a2.set_ylim(10, 450)
a2.set_xlabel("Time into the 60 s run (s)")
a2.set_ylabel("Latency of successful calls, ms (log)")
a2.set_title("Latency over time (5 s windows)", fontsize=10)
a2.grid(color=C["grid"], which="both", lw=0.6)
a2.legend(frameon=False, fontsize=7.5, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.22))
fig.tight_layout()
save(fig, "fig10_concurrency")


# ---- Fig 6: as-built architecture
def box(ax, x, y, w, h, title, sub, ec, fc="white", fs=9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", ec=ec, fc=fc, lw=1.6))
    ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center", fontsize=fs, fontweight="bold", color="#222")
    if sub:
        ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center", fontsize=7, color="#555")


def arrow(ax, a, b, label="", color="#444", ls="-", lx=0, ly=0.12):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color=color, lw=1.2, ls=ls))
    if label:
        ax.text((a[0] + b[0]) / 2 + lx, (a[1] + b[1]) / 2 + ly, label, fontsize=6.8, ha="center", color="#444")


fig, ax = plt.subplots(figsize=(10.5, 5.0))
ax.set_xlim(0, 21)
ax.set_ylim(0, 10)
ax.axis("off")
ax.add_patch(FancyBboxPatch((3.0, 0.25), 17.7, 9.4, boxstyle="round,pad=0.02,rounding_size=0.2", ec="#222", fc="#fafafa", lw=1.4))
ax.text(3.3, 9.25, "AWS account, ap-south-1 (Mumbai)", fontsize=9.5, fontweight="bold")
ax.text(3.3, 8.75, "tag project=it457-g47 | Budgets alert at $5 | Python 3.15, one least-privilege IAM role per function", fontsize=7.6, color="#555")
box(ax, 0.1, 4.3, 2.4, 1.4, "Client", "browser / curl", "#222")
box(ax, 3.5, 4.0, 2.9, 2.0, "API Gateway", "HTTP API\n$default stage", "#c026d3", "#fdf0ff")
box(ax, 7.4, 6.6, 3.3, 1.5, "shaadi-ping (A)", "GET /baseline\nno AWS calls", C["ping"], "#f1f3f5")
box(ax, 7.4, 4.25, 3.3, 1.5, "shaadi-interest-api", "GET /, POST /interest,\nGET /interest/{id}", "#c026d3", "#fdf0ff")
box(ax, 7.4, 1.9, 3.3, 1.5, "shaadi-moderate (B)", "POST /moderate", C["moderate"], "#ebfbee")
box(ax, 12.4, 4.25, 2.9, 1.5, "DynamoDB", "Interests (on-demand)", "#1971c2", "#e7f5ff")
box(ax, 12.4, 1.9, 2.9, 1.5, "Rekognition", "DetectModeration-\nLabels, min conf 60", C["moderate"], "#ebfbee")
box(ax, 17.0, 1.9, 3.3, 1.5, "S3 bucket", "photos/ (30 images)\nresults/ (CSV output)", "#e8590c", "#fff4e6")
box(ax, 12.4, 0.45, 2.9, 1.1, "DynamoDB", "verdicts (on-demand)", "#1971c2", "#e7f5ff")
box(ax, 17.0, 6.6, 3.3, 1.5, "CloudWatch Logs", "REPORT: Init, Duration,\nBilled, Max memory", "#495057", "#f8f9fa")
box(ax, 3.5, 0.6, 3.6, 1.6, "shaadi-loadgen", "harness (1024 MB): load, then\nLogs Insights -> CSV in S3", "#495057", "#fff")
arrow(ax, (2.5, 5.0), (3.5, 5.0), "HTTPS")
arrow(ax, (6.4, 5.6), (7.4, 7.2))
arrow(ax, (6.4, 5.0), (7.4, 5.0))
arrow(ax, (6.4, 4.4), (7.4, 2.8))
arrow(ax, (10.7, 5.0), (12.4, 5.0), "PutItem")
arrow(ax, (10.7, 2.65), (12.4, 2.65), "1. detect")
arrow(ax, (15.3, 2.65), (17.0, 2.65), "2. read image")
arrow(ax, (10.0, 1.9), (12.4, 1.0), "3. save verdict", lx=-0.9, ly=-0.25)
arrow(ax, (4.95, 2.2), (4.95, 4.0), "HTTPS load", color="#868e96", ls="--", lx=-0.75, ly=0)
arrow(ax, (10.7, 7.35), (17.0, 7.35), "logs from all functions", color="#868e96", ls="--")
save(fig, "fig6_architecture_built")
print("charts ok", sorted(os.listdir(OUT)))
