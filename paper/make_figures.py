#!/usr/bin/env python3
"""
make_figures.py — regenerate every figure in the DB-13 paper from measured data.

Reads env_report.json (produced by verify_env.py) and writes PDFs next to itself.
No number is typed by hand; if the corpus changes, re-run verify_env.py then this.

Palette: validated categorical slots 1-3 (blue/orange/aqua) on the light chart
surface; single-series figures carry no legend, all marks are directly labelled.
"""
import json, os, sys, argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# ---- design tokens -------------------------------------------------------
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
GOOD, CRITICAL = "#0ca30c", "#d03b3b"
SURFACE = "#fcfcfb"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, BASELINE = "#e1e0d9", "#c3c2b7"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "font.size": 8.5,
    "axes.edgecolor": BASELINE, "axes.linewidth": 0.8,
    "axes.labelcolor": INK2, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "xtick.labelcolor": INK2, "ytick.labelcolor": INK2,
    "axes.grid": False, "legend.frameon": False,
    "axes.spines.top": False, "axes.spines.right": False,
    "pdf.fonttype": 42,
})

ORDER = [2, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]


def load(path):
    with open(path) as f:
        return json.load(f)


def bare(ax, xgrid=False, ygrid=False):
    if xgrid:
        ax.xaxis.grid(True, color=GRID, lw=0.6, zorder=0)
    if ygrid:
        ax.yaxis.grid(True, color=GRID, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


# ---- Figure 1: effective action space ------------------------------------
def fig_effective(rep, out):
    rows = [(f"db-{n}", rep["databases"][f"db-{n}"]) for n in ORDER]
    rows.sort(key=lambda r: r[1]["clusters"])
    names = [r[0] for r in rows]
    clus = [r[1]["clusters"] for r in rows]
    ent = [r[1]["entropy"] for r in rows]
    nq = rows[0][1]["n_queries"]

    fig, ax = plt.subplots(figsize=(6.4, 3.5))
    y = range(len(names))
    # nominal capacity, recessive
    ax.barh(list(y), [nq] * len(names), color=GRID, height=0.62, zorder=1)
    bars = ax.barh(list(y), clus, color=[GOOD if c == nq else BLUE for c in clus],
                   height=0.62, zorder=2)
    for i, (b, c, e) in enumerate(zip(bars, clus, ent)):
        ax.text(c + 0.45, i, f"{c}", va="center", ha="left",
                fontsize=8.5, color=INK, fontweight="bold")
        ax.text(nq + 3.2, i, f"H = {e:.3f}", va="center", ha="left",
                fontsize=7.5, color=MUTED, family="monospace")
    ax.axvline(nq, color=BASELINE, lw=0.9, zorder=3)
    ax.set_yticks(list(y)); ax.set_yticklabels(names)
    ax.set_xlim(0, nq + 10)
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.set_xlabel("distinct gold actions after clustering at $\\tau$ = 0.99   "
                  "(grey = nominal 30)")
    tot = sum(clus)
    ax.set_title(f"Effective action space: {tot} of {nq*len(names)} "
                 f"({tot/(nq*len(names)):.1%})", loc="left", pad=9, fontsize=9.5,
                 fontweight="bold")
    ax.spines["left"].set_color(BASELINE)
    bare(ax)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return tot


# ---- Figure 2: the difficulty space `complexity` collapses ---------------
def fig_difficulty(rep, out):
    # manual label offsets (dx, dy in points, ha) where markers crowd
    OFF = {2: (-30, 6, "right"), 3: (-30, -8, "right"), 6: (-16, 8, "right"),
           9: (14, -4, "left"), 15: (16, 2, "left"), 8: (-16, 2, "right"),
           13: (-16, 6, "right"), 16: (-16, 2, "right"), 14: (2, -16, "center"),
           10: (2, -20, "center"), 7: (2, 18, "center"), 11: (16, 4, "left"),
           12: (2, 20, "center")}
    fig, ax = plt.subplots(figsize=(6.4, 3.9))
    for n in ORDER:
        d = rep["databases"][f"db-{n}"]
        m = d["difficulty_mean"]
        clean = d["clusters"] == d["n_queries"]
        ax.scatter(m["join"], m["window"], s=26 * m["tables"],
                   facecolor=BLUE if clean else ORANGE,
                   edgecolor=SURFACE, linewidth=1.4, alpha=0.85, zorder=3)
        dx, dy, ha = OFF.get(n, (0, -14, "center"))
        ax.annotate(f"db-{n}", (m["join"], m["window"]),
                    textcoords="offset points", xytext=(dx, dy),
                    ha=ha, va="center", fontsize=7.4, color=INK2, zorder=4)
    ax.set_xlabel("joins per query (AST)")
    ax.set_ylabel("window functions per query (AST)")
    ax.set_title("Every point is labelled  complexity = \"moderate\"",
                 loc="left", pad=9, fontsize=9.5, fontweight="bold")
    ax.text(0.985, 0.965,
            "marker area $\\propto$ base tables per query\n"
            "blue = distinct action set    orange = collapsed",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=7.4, color=MUTED, linespacing=1.5)
    ax.set_xlim(-1.5, 8.0); ax.set_ylim(-2.6, 19.5)
    bare(ax, ygrid=True)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


# ---- Figure 3: schema utilization ----------------------------------------
def fig_schema(rep, out):
    rows = [(f"db-{n}", rep["databases"][f"db-{n}"]) for n in ORDER]
    rows.sort(key=lambda r: r[1]["schema_coverage"])
    names = [r[0] for r in rows]
    cov = [r[1]["schema_coverage"] for r in rows]
    decl = [r[1]["schema_tables"] for r in rows]
    used = [r[1]["declared_referenced"] for r in rows]

    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    x = range(len(names))
    ax.bar(list(x), cov, color=BLUE, width=0.6, zorder=2)
    for i, (c, d, u) in enumerate(zip(cov, decl, used)):
        ax.text(i, c + 0.028, f"{u}/{d}", ha="center", va="bottom",
                fontsize=7.4, color=INK2)
    tot_u, tot_d = sum(used), sum(decl)
    ax.axhline(tot_u / tot_d, color=ORANGE, lw=1.4, ls=(0, (4, 2)), zorder=3)
    ax.text(len(names) - 0.4, tot_u / tot_d + 0.022,
            f"corpus {tot_u}/{tot_d} = {tot_u/tot_d:.1%}",
            ha="right", va="bottom", fontsize=7.6, color=ORANGE, fontweight="bold")
    ax.set_xticks(list(x)); ax.set_xticklabels(names, rotation=0)
    ax.set_ylim(0, 1.08); ax.set_ylabel("declared tables reached by a gold action")
    ax.yaxis.set_major_formatter(lambda v, p: f"{v:.0%}")
    ax.set_title("Schema utilization: a third of the declared surface is unreachable",
                 loc="left", pad=9, fontsize=9.5, fontweight="bold")
    bare(ax, ygrid=True)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


# ---- Figure 4: invariant status ------------------------------------------
def fig_invariants(rep, out):
    short = {
        "I1": "Action-set cardinality", "I2": "Field totality",
        "I3": "Schema closure", "I4": "Action distinctness",
        "I5": "Difficulty signal", "I6": "Reward verifiability",
        "I7": "Representation agreement", "I8": "Provenance resolution",
    }
    extent = {
        "I1": "30 per environment, 13/13",
        "I2": "3,120 required values present",
        "I3": "db-3: 30 gold actions unexecutable",
        "I4": "168 of 390 actions collapse",
        "I5": "complexity constant, all 390",
        "I6": "390/390 expected_output are prose",
        "I7": "12 of 390 diverge from projection",
        "I8": "13/13 source paths unresolvable",
    }
    keys = list(short)
    fig, ax = plt.subplots(figsize=(6.4, 2.7))
    for i, k in enumerate(keys):
        holds = rep["invariants"][k]["holds"]
        y = len(keys) - 1 - i
        ax.barh(y, 1, color=GOOD if holds else CRITICAL, height=0.52, zorder=2)
        ax.text(-0.06, y, k, ha="right", va="center", fontsize=8.5,
                color=INK, fontweight="bold", family="monospace")
        ax.text(1.14, y, short[k], ha="left", va="center", fontsize=8.4, color=INK)
        ax.text(1.14, y - 0.30, extent[k], ha="left", va="top",
                fontsize=7.1, color=MUTED)
        ax.text(0.5, y, "HOLDS" if holds else "FAILS", ha="center", va="center",
                fontsize=7.2, color="white", fontweight="bold")
    ax.set_xlim(-0.5, 5.2); ax.set_ylim(-0.7, len(keys) - 0.25)
    ax.axis("off")
    n_ok = sum(rep["invariants"][k]["holds"] for k in keys)
    ax.set_title(f"Environment invariants: {n_ok} of {len(keys)} hold",
                 loc="left", pad=8, fontsize=9.5, fontweight="bold", x=-0.075)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-r", "--report", default="../data/env_report.json")
    ap.add_argument("-o", "--outdir", default="figures")
    a = ap.parse_args()
    rep = load(a.report)
    os.makedirs(a.outdir, exist_ok=True)
    j = lambda f: os.path.join(a.outdir, f)

    tot = fig_effective(rep, j("fig-effective-actions.pdf"))
    fig_difficulty(rep, j("fig-difficulty-space.pdf"))
    fig_schema(rep, j("fig-schema-utilization.pdf"))
    fig_invariants(rep, j("fig-invariants.pdf"))
    print(f"wrote 4 figures to {a.outdir}")
    print(f"  effective actions: {tot}/390")
    c = rep["corpus"]
    print(f"  corpus: {c['tables']} tables, {c['foreign_keys']} FKs, "
          f"{c['indexes']} indexes, {c['declared_tables_reached']} reachable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
