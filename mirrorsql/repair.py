#!/usr/bin/env python3
"""
repair.py -- schema repairs for the MIRROR-SQL corpus.

Two defects prevent the shipped schemas from loading into the PostgreSQL they
are documented for. Both were found by executing the corpus rather than reading
it, and both are mechanical:

  R1  DIALECT LEAK.  `VARCHAR(16777216)` appears in three schemas. 16,777,216 is
      Snowflake's maximum VARCHAR length; PostgreSQL's is 10,485,760, so every
      CREATE TABLE carrying one is rejected outright. The schemas were authored
      or transpiled against Snowflake and shipped labelled PostgreSQL.
      Repair: rewrite over-long VARCHAR(n) as TEXT, which is what Snowflake's
      VARCHAR(16777216) means in practice.

  R2  UNDECLARED EXTENSION.  Six schemas use the PostGIS `geography` and
      `geometry` types without a CREATE EXTENSION statement, so they fail on any
      database where PostGIS is not already installed.
      Repair: prepend `CREATE EXTENSION IF NOT EXISTS postgis;`. Where PostGIS is
      genuinely unavailable, `postgis_shim()` emits domains over TEXT so the
      structural corpus still loads; the shim is lossy for spatial predicates and
      says so.

Neither repair changes a table, column, key or index -- only the type spelling
and one preamble line. `python -m mirrorsql.repair --check` reports what would
change without writing.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

PG_MAX_VARCHAR = 10_485_760
SNOWFLAKE_MAX_VARCHAR = 16_777_216

DB_IDS = (2, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)

POSTGIS_SHIM = """\
-- MIRROR-SQL portability shim.
-- Emitted only when PostGIS is unavailable. Spatial types degrade to text
-- domains: the corpus loads and every non-spatial query runs, but spatial
-- predicates (ST_*) will not. Install PostGIS for full fidelity.
DO $mirrorsql$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'geography') THEN
        CREATE DOMAIN geography AS TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'geometry') THEN
        CREATE DOMAIN geometry AS TEXT;
    END IF;
END
$mirrorsql$;
"""

POSTGIS_PREAMBLE = "CREATE EXTENSION IF NOT EXISTS postgis;\n"

_VARCHAR = re.compile(r"\bVARCHAR\s*\(\s*(\d+)\s*\)", re.I)
_SPATIAL = re.compile(r"\b(geography|geometry)\s*(\(|,|\s)", re.I)
_HAS_EXT = re.compile(r"CREATE\s+EXTENSION", re.I)


def find_oversized_varchar(ddl: str) -> list[int]:
    """Lengths exceeding PostgreSQL's limit, in file order."""
    return [int(m.group(1)) for m in _VARCHAR.finditer(ddl)
            if int(m.group(1)) > PG_MAX_VARCHAR]


def uses_spatial_types(ddl: str) -> int:
    """Count of PostGIS type mentions outside comments."""
    stripped = re.sub(r"--[^\n]*", " ", ddl)
    return len(_SPATIAL.findall(stripped))


def repair_ddl(ddl: str, shim: bool = False) -> tuple[str, dict]:
    """Apply R1 and R2. Returns (repaired_ddl, what_changed)."""
    changed = {"varchar_to_text": 0, "postgis_preamble": False, "shim": False}

    def _fix(m: re.Match) -> str:
        n = int(m.group(1))
        if n > PG_MAX_VARCHAR:
            changed["varchar_to_text"] += 1
            return "TEXT"
        return m.group(0)

    out = _VARCHAR.sub(_fix, ddl)

    if uses_spatial_types(out) and not _HAS_EXT.search(out):
        header = POSTGIS_SHIM if shim else POSTGIS_PREAMBLE
        out = header + "\n" + out
        changed["postgis_preamble"] = not shim
        changed["shim"] = shim
    return out, changed


def repair_corpus(root: str, out_root: str | None = None, shim: bool = False,
                  check_only: bool = False) -> dict:
    """Repair every schema under `root`. Writes in place unless out_root is given."""
    report: dict[str, dict] = {}
    for n in DB_IDS:
        src = os.path.join(root, f"db-{n}", "DATABASE", "schema.sql")
        if not os.path.exists(src):
            continue
        ddl = open(src, errors="ignore").read()
        over = find_oversized_varchar(ddl)
        spatial = uses_spatial_types(ddl)
        repaired, changed = repair_ddl(ddl, shim=shim)
        report[f"db-{n}"] = {
            "oversized_varchar": len(over),
            "oversized_lengths": sorted(set(over)),
            "spatial_type_uses": spatial,
            "already_declares_extension": bool(_HAS_EXT.search(ddl)),
            **changed,
            "modified": repaired != ddl,
        }
        if check_only or repaired == ddl:
            continue
        dst = src if out_root is None else os.path.join(
            out_root, f"db-{n}", "DATABASE", "schema.sql")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "w") as f:
            f.write(repaired)
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", help="corpus root containing db-N/DATABASE/schema.sql")
    ap.add_argument("-o", "--out", default=None,
                    help="write repaired schemas here instead of in place")
    ap.add_argument("--shim", action="store_true",
                    help="emit portable TEXT domains instead of CREATE EXTENSION postgis")
    ap.add_argument("--check", action="store_true", help="report without writing")
    a = ap.parse_args(argv)

    rep = repair_corpus(a.root, a.out, shim=a.shim, check_only=a.check)
    n_v = sum(r["oversized_varchar"] for r in rep.values())
    n_s = sum(1 for r in rep.values() if r["spatial_type_uses"] and
              not r["already_declares_extension"])
    print(f"{'db':<7}{'VARCHAR>PG_MAX':>16}{'spatial uses':>14}{'repaired':>10}")
    print("-" * 48)
    for k, r in rep.items():
        print(f"{k:<7}{r['oversized_varchar']:>16}{r['spatial_type_uses']:>14}"
              f"{str(r['modified']):>10}")
    print("-" * 48)
    print(f"R1 dialect leak : {n_v} VARCHAR({SNOWFLAKE_MAX_VARCHAR}) -> TEXT")
    print(f"R2 undeclared   : {n_s} schemas needed a PostGIS declaration")
    if a.check:
        print("\n--check: nothing written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
