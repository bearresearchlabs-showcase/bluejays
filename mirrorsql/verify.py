#!/usr/bin/env python3
"""
mirrorsql.verify — environment invariant checker for the MIRROR-SQL text-to-SQL RL corpus.

Checks the invariants I1-I8 defined in the accompanying paper against the shipped
package and emits a machine-readable report. Every number in the paper is produced
by this script; nothing is transcribed by hand.

Usage:  python3 -m mirrorsql.verify <package_root> [-o report.json]

<package_root> contains db-N/{DATABASE/schema.sql, QUERIES/queries.json}.
Requires: sqlglot (pip install sqlglot). Falls back to regex if unavailable,
with reduced precision on I3 (reported in the output).
"""
import json, os, re, sys, math, argparse, collections, difflib

DBS = [2, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
REQUIRED = ["number", "question", "sql", "description", "evidence",
            "expected_output", "complexity", "line_number"]
DUP_TAU = 0.99          # near-duplicate similarity threshold
N_EXPECTED = 30         # |A_d| per database

try:
    import sqlglot
    from sqlglot import exp
    HAVE_SQLGLOT = True
except ImportError:
    HAVE_SQLGLOT = False


# ---------------------------------------------------------------- primitives

def norm(s):
    """Whitespace- and case-normalized SQL, for similarity comparison."""
    return re.sub(r"\s+", " ", s or "").strip().lower()


def load_queries(root, n):
    with open(os.path.join(root, f"db-{n}", "QUERIES", "queries.json")) as f:
        return json.load(f)


def read_schema(root, n):
    with open(os.path.join(root, f"db-{n}", "DATABASE", "schema.sql"),
              errors="ignore") as f:
        return f.read()


def strip_sql_comments(sql):
    """Remove -- line comments and /* */ blocks. Counting DDL without this
    matches prose: '-- References foo' and '-- Create indexes for performance'."""
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    return re.sub(r"--[^\n]*", " ", sql)


def schema_counts(sql):
    """Table, FK and index counts over comment-stripped DDL.
    An FK is one REFERENCES clause (inline or table-level), 1:1 with the constraint."""
    d = strip_sql_comments(sql)
    return {
        "tables": len(re.findall(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"]?\w+", d, re.I)),
        "fks": len(re.findall(r"\bREFERENCES\s+[`\"]?\w+", d, re.I)),
        "indexes": len(re.findall(r"CREATE\s+(?:UNIQUE\s+)?INDEX\b", d, re.I)),
        "views": len(re.findall(r"CREATE\s+(?:OR\s+REPLACE\s+)?(?:MATERIALIZED\s+)?VIEW\b", d, re.I)),
    }


def schema_tables(sql):
    """Every relation a query may legally read: base tables AND views.

    Views count. db-3 anonymises its base tables to table1/2/3 and exposes a
    compatibility VIEW under the original name; an earlier version of this
    checker collected only CREATE TABLE and therefore reported all thirty of
    db-3's gold actions as unexecutable. They execute.
    """
    d = strip_sql_comments(sql)
    rel = set(re.findall(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"]?(\w+)", d, re.I))
    rel |= set(re.findall(
        r"CREATE\s+(?:OR\s+REPLACE\s+)?(?:MATERIALIZED\s+)?VIEW\s+"
        r"(?:IF\s+NOT\s+EXISTS\s+)?[`\"]?(\w+)", d, re.I))
    return {t.lower() for t in rel}


def base_tables(query_sql):
    """
    Physical tables a query reads, excluding CTE names and derived-table aliases.
    sqlglot path is authoritative; the regex path over-reports and is flagged.
    """
    if HAVE_SQLGLOT:
        try:
            tree = sqlglot.parse_one(query_sql, dialect="postgres")
        except Exception:
            return None, "parse_error"
        ctes = {c.alias_or_name.lower() for c in tree.find_all(exp.CTE)}
        out = set()
        for t in tree.find_all(exp.Table):
            name = (t.name or "").lower()
            if name and name not in ctes:
                out.add(name)
        return out, "sqlglot"
    ctes = {c.lower() for c in re.findall(r"([a-z_]\w*)\s+AS\s*\(", query_sql, re.I)}
    refs = {t.lower() for t in re.findall(r"\b(?:FROM|JOIN)\s+([a-z_]\w*)", query_sql, re.I)}
    return refs - ctes, "regex"


def difficulty(query_sql):
    """Derived difficulty features — the replacement for the degenerate `complexity` field."""
    if HAVE_SQLGLOT:
        try:
            t = sqlglot.parse_one(query_sql, dialect="postgres")
            return {
                "cte": len(list(t.find_all(exp.CTE))),
                "join": len(list(t.find_all(exp.Join))),
                "window": len(list(t.find_all(exp.Window))),
                "subquery": len(list(t.find_all(exp.Subquery))),
                "agg": len([f for f in t.find_all(exp.AggFunc)]),
                "tables": len({x.name.lower() for x in t.find_all(exp.Table) if x.name}),
            }
        except Exception:
            pass
    return {
        "cte": len(re.findall(r"[a-z_]\w*\s+AS\s*\(", query_sql, re.I)),
        "join": len(re.findall(r"\bJOIN\b", query_sql, re.I)),
        "window": len(re.findall(r"\bOVER\s*\(", query_sql, re.I)),
        "subquery": len(re.findall(r"\(\s*SELECT\b", query_sql, re.I)),
        "agg": len(re.findall(r"\b(COUNT|SUM|AVG|MIN|MAX|STDDEV|PERCENTILE_CONT)\s*\(",
                              query_sql, re.I)),
        "tables": len({t.lower() for t in
                       re.findall(r"\b(?:FROM|JOIN)\s+([a-z_]\w*)", query_sql, re.I)}),
    }


def cluster(sqls, tau=DUP_TAU):
    """Union-find over pairwise normalized similarity. Returns cluster sizes."""
    k = len(sqls)
    parent = list(range(k))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(k):
        for j in range(i + 1, k):
            if difflib.SequenceMatcher(None, sqls[i], sqls[j]).ratio() >= tau:
                a, b = find(i), find(j)
                if a != b:
                    parent[a] = b
    return sorted(collections.Counter(find(i) for i in range(k)).values(), reverse=True)


def norm_entropy(sizes, k):
    p = [s / k for s in sizes]
    return -sum(x * math.log(x) for x in p) / math.log(k) if k > 1 else 0.0


# ---------------------------------------------------------------- invariants

def check(root):
    rep = {"parser": "sqlglot" if HAVE_SQLGLOT else "regex",
           "tau": DUP_TAU, "databases": {}, "invariants": {}}
    I = collections.defaultdict(list)   # invariant -> list of (db, detail) violations

    for n in DBS:
        raw = load_queries(root, n)
        Q = raw["queries"]
        sch = read_schema(root, n)
        declared = schema_tables(sch)
        counts = schema_counts(sch)
        d = {"n_queries": len(Q), "schema_tables": len(declared),
             "fks": counts["fks"], "indexes": counts["indexes"], "views": counts["views"]}

        # I1 — cardinality: |A_d| = 30
        if len(Q) != N_EXPECTED:
            I["I1"].append((n, f"|A|={len(Q)}"))

        # I2 — field totality: every required key present and non-empty
        missing = [(q.get("number"), k) for q in Q for k in REQUIRED
                   if not str(q.get(k, "")).strip()]
        if missing:
            I["I2"].append((n, f"{len(missing)} empty required fields"))

        # I3 — schema closure: every base table referenced by a gold query is declared
        referenced, mode, unparsed = set(), rep["parser"], 0
        for q in Q:
            tabs, how = base_tables(q["sql"])
            if tabs is None:
                unparsed += 1
                continue
            referenced |= tabs
        undefined = sorted(referenced - declared)
        d["referenced_tables"] = len(referenced)
        d["undefined_tables"] = undefined
        d["unparsed"] = unparsed
        d["declared_referenced"] = len(referenced & declared)
        d["schema_coverage"] = round(len(referenced & declared) / len(declared), 3) if declared else 0.0
        if undefined:
            I["I3"].append((n, f"{len(undefined)} undefined: {undefined[:6]}"))

        # I4 — action distinctness: no two gold queries within tau
        sizes = cluster([norm(q["sql"]) for q in Q])
        d["clusters"] = len(sizes)
        d["largest_cluster"] = sizes[0]
        d["effective_ratio"] = round(len(sizes) / len(Q), 3)
        d["entropy"] = round(norm_entropy(sizes, len(Q)), 3)
        if len(sizes) != len(Q):
            I["I4"].append((n, f"{len(Q)-len(sizes)} collapsed; largest={sizes[0]}"))

        # I5 — difficulty signal: complexity must not be constant across the corpus
        d["complexity_values"] = sorted({q.get("complexity") for q in Q})

        # I6 — reward verifiability: expected_output must be structured, not prose
        prose = sum(1 for q in Q if not re.match(r"^\s*[\[{|]", str(q.get("expected_output", ""))))
        d["prose_expected_output"] = prose
        if prose:
            I["I6"].append((n, f"{prose}/{len(Q)} expected_output are prose"))

        # I7 — representation agreement: json description present in queries.md
        mdp = os.path.join(root, f"db-{n}", "QUERIES", "queries.md")
        if os.path.exists(mdp):
            md = open(mdp, errors="ignore").read()
            md_desc = set()
            for block in re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", md, re.S):
                try:
                    md_desc.add((json.loads(block).get("description") or "").strip())
                except Exception:
                    pass
            agree = sum(1 for q in Q
                        if (q.get("description") or "").strip() in md_desc
                        or (q.get("description") or "")[:80].strip() in md)
            d["md_agreement"] = f"{agree}/{len(Q)}"
            if agree != len(Q):
                I["I7"].append((n, f"{len(Q)-agree} descriptions absent from queries.md"))
        else:
            d["md_agreement"] = "no queries.md"

        # difficulty features
        feats = [difficulty(q["sql"]) for q in Q]
        d["difficulty_mean"] = {k: round(sum(f[k] for f in feats) / len(feats), 2)
                                for k in feats[0]}
        rep["databases"][f"db-{n}"] = d

    # I5 is corpus-level
    allc = {v for d in rep["databases"].values() for v in d["complexity_values"]}
    if len(allc) < 2:
        I["I5"].append(("corpus", f"complexity constant at {allc}"))

    # I8 — provenance: source_file must resolve
    for n in DBS:
        sf = load_queries(root, n).get("source_file")
        if sf and not os.path.exists(sf):
            I["I8"].append((n, "source_file does not resolve"))

    names = {
        "I1": "Action-set cardinality |A_d| = 30",
        "I2": "Field totality — all required keys present and non-empty",
        "I3": "Schema closure — every referenced base table is declared",
        "I4": "Action distinctness — no gold pair within tau",
        "I5": "Difficulty signal — complexity is non-constant",
        "I6": "Reward verifiability — expected_output is structured",
        "I7": "Representation agreement — json description appears in queries.md",
        "I8": "Provenance resolution — source_file resolves",
    }
    for k, label in names.items():
        rep["invariants"][k] = {
            "statement": label,
            "holds": not I[k],
            "violations": [{"db": str(a), "detail": b} for a, b in I[k]],
        }

    tot = sum(v["n_queries"] for v in rep["databases"].values())
    cl = sum(v["clusters"] for v in rep["databases"].values())
    rep["corpus"] = {
        "databases": len(DBS), "queries": tot,
        "tables": sum(v["schema_tables"] for v in rep["databases"].values()),
        "foreign_keys": sum(v["fks"] for v in rep["databases"].values()),
        "indexes": sum(v["indexes"] for v in rep["databases"].values()),
        "declared_tables_reached": sum(v["declared_referenced"] for v in rep["databases"].values()),
        "effective_actions": cl,
        "effective_ratio": round(cl / tot, 3),
        "invariants_holding": sum(1 for v in rep["invariants"].values() if v["holds"]),
        "invariants_total": len(names),
    }
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("-o", "--out", default="env_report.json")
    a = ap.parse_args()
    rep = check(a.root)
    with open(a.out, "w") as f:
        json.dump(rep, f, indent=2)

    c = rep["corpus"]
    print(f"parser: {rep['parser']}   tau: {rep['tau']}")
    print(f"corpus: {c['databases']} databases, {c['queries']} gold queries, "
          f"{c['effective_actions']} effective ({c['effective_ratio']:.0%})")
    print(f"invariants: {c['invariants_holding']}/{c['invariants_total']} hold\n")
    for k, v in rep["invariants"].items():
        mark = "PASS" if v["holds"] else "FAIL"
        print(f"  [{mark}] {k}  {v['statement']}")
        for viol in v["violations"][:4]:
            print(f"           db-{viol['db']}: {viol['detail']}")
        if len(v["violations"]) > 4:
            print(f"           ... and {len(v['violations'])-4} more")
    print(f"\nwrote {a.out}")
    return 0 if c["invariants_holding"] == c["invariants_total"] else 1


if __name__ == "__main__":
    sys.exit(main())
