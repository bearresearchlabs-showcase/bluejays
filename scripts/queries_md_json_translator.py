#!/usr/bin/env python3
"""
Byte-for-byte translation: queries.md ↔ queries.json

Treats queries.md as a "form" — submission produces queries.json as API response.
Uses template/queries_format_schema.yaml for XLSX/Word-style structure (sections, styles, content).

Round-trip: md → json (extract with _raw) → md (render from _raw) = identical bytes.

Usage:
    python3 scripts/queries_md_json_translator.py extract [db-1] | -a   # md → json (API response)
    python3 scripts/queries_md_json_translator.py render [db-1] | -a  # json → md (from _raw)
    python3 scripts/queries_md_json_translator.py validate [db-1] | -a # round-trip check
"""

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
TEMPLATE = ROOT / "template"
sys.path.insert(0, str(Path(__file__).parent))

try:
    from db_paths import get_queries_dir
    from timestamp_utils import get_est_timestamp
except ImportError:
    def get_queries_dir(db_dir: Path) -> Path:
        for d in (db_dir / "app" / "QUERIES", db_dir / "QUERIES", db_dir / "queries"):
            if d.exists():
                return d
        return db_dir / "queries"

    def get_est_timestamp() -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")


def _find_queries_dir(db_dir: Path) -> Path:
    return get_queries_dir(db_dir)


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


# 1:1 section keys (must match queries.md ## headers exactly)
_PREAMBLE_SECTIONS = [
    "Database Overview", "Purpose", "Use Case", "Business Value",
    "Schema", "Domain Knowledge", "Query Difficulty Distribution",
]


def _extract_template_format(md_content: str) -> dict:
    """
    Extract from template-format queries.md with byte-for-byte fidelity.
    Returns API-response structure with _raw_json per query for round-trip.
    Sections stored 1:1: meta.sections.{section_name} = {block_type, content}.
    """
    content_bytes = md_content.encode("utf-8")
    checksum = _sha256(content_bytes)

    # Extract title (first # line)
    title_match = re.match(r"^# (.+)$", md_content, re.MULTILINE)
    preamble = {"_title": title_match.group(1) if title_match else f"Database — Query Documentation"}

    # Extract preamble sections — 1:1 structure: key = MD header, value = raw content
    section_pattern = r"^## (Database Overview|Purpose|Use Case|Business Value|Schema|Domain Knowledge|Query Difficulty Distribution)\s*$"
    section_matches = list(re.finditer(section_pattern, md_content, re.MULTILINE))

    sections = {}  # 1:1: same keys as queries.md ## headers
    for i, m in enumerate(section_matches):
        name = m.group(1)
        start = m.end()
        end = section_matches[i + 1].start() if i + 1 < len(section_matches) else md_content.find("\n## Queries\n")
        if end < 0:
            end = len(md_content)
        block = md_content[start:end].strip()
        preamble[name] = block  # backward compat
        # 1:1 structure: infer block_type from code fence (matches qa_anchor section_block_types)
        if block.startswith("```yaml"):
            block_type = "yaml"
        elif block.startswith("```sql"):
            block_type = "sql"
        elif block.startswith("```text"):
            block_type = "text"
        elif block.startswith("```"):
            block_type = "text"  # generic ``` defaults to text
        else:
            block_type = "yaml" if ("db_id:" in block or "domain:" in block) else ("sql" if "CREATE TABLE" in block else "text")
        sections[name] = {"block_type": block_type, "content": block}

    # Extract query blocks with exact _raw_json
    query_headers = list(re.finditer(r"^### Query (\d+) — (.+)$", md_content, re.MULTILINE))
    json_blocks = list(re.finditer(r"```json\s*\n(.*?)```", md_content, re.DOTALL))

    queries = []
    for i, header_match in enumerate(query_headers):
        qnum = int(header_match.group(1))
        header_line = header_match.group(0)
        start_pos = header_match.end()

        # Find the next ```json block after this header
        json_match = None
        for jm in json_blocks:
            if jm.start() > start_pos:
                json_match = jm
                break

        if not json_match:
            continue

        raw_json = json_match.group(1).rstrip()  # Preserve exact content (no trailing newline from ```)
        try:
            parsed = json.loads(raw_json)
        except json.JSONDecodeError:
            parsed = {}

        # Store parsed + _raw for round-trip
        query_data = dict(parsed)
        query_data["_raw_json"] = raw_json
        query_data["_header"] = header_line
        query_data["question_id"] = query_data.get("question_id", qnum)
        query_data["number"] = qnum
        if "sql" not in query_data and "SQL" in query_data:
            query_data["sql"] = query_data["SQL"]
        queries.append(query_data)

    return {
        "status": "success",
        "submission": {
            "source": "queries.md",
            "content_sha256": checksum,
            "byte_count": len(content_bytes),
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "format_version": "1.0",
        },
        "meta": {
            "schema_anchor": "template/qa_anchor.json",
            "format_schema": "template/queries_format_schema.yaml",
            "total_queries": len(queries),
            "preamble": preamble,
            "sections": sections,  # 1:1 structure: keys = MD ## headers, values = {block_type, content}
        },
        "data": {"queries": queries},
        "validation": {"round_trip_ok": None, "checksum_match": None},
    }


def extract_md_to_json(db_num: int) -> dict | None:
    """Extract queries.md → queries.json (API response format)."""
    db_dir = SOURCE / f"db-{db_num}"
    qd = _find_queries_dir(db_dir)
    qm = qd / "queries.md"
    qj = qd / "queries.json"

    if not qm.exists():
        return None

    content = qm.read_text(encoding="utf-8")
    result = _extract_template_format(content)

    # Backward compat: flat structure for consumers; _api_response has full data for round-trip
    flat = {
        "db_id": f"db-{db_num}",
        "source_file": str(qm),
        "extraction_timestamp": get_est_timestamp(),
        "total_queries": result["meta"]["total_queries"],
        "queries": result["data"]["queries"],  # Keep _raw_json for round-trip
    }
    flat["_api_response"] = result

    qj.parent.mkdir(parents=True, exist_ok=True)
    qj.write_text(json.dumps(flat, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def render_json_to_md(db_num: int) -> str | None:
    """Render queries.json → queries.md using _raw_json for byte-for-byte fidelity."""
    db_dir = SOURCE / f"db-{db_num}"
    qd = _find_queries_dir(db_dir)
    qj = qd / "queries.json"
    qm = qd / "queries.md"

    if not qj.exists():
        return None

    data = json.loads(qj.read_text(encoding="utf-8"))
    api = data.get("_api_response", data)
    queries = api.get("data", {}).get("queries", data.get("queries", []))

    if not queries:
        return None

    meta = api.get("meta", {})
    preamble = meta.get("preamble", {})
    # Build md from preamble + queries
    lines = []
    title = preamble.get("_title", f"Database db-{db_num} — Query Documentation")
    lines.append(f"# {title}\n")

    for section_name in [
        "Database Overview", "Purpose", "Use Case", "Business Value",
        "Schema", "Domain Knowledge", "Query Difficulty Distribution",
    ]:
        block = preamble.get(section_name, "")
        if block:
            lines.append(f"## {section_name}\n")
            if block.startswith("```"):
                lines.append(block)
            else:
                # Infer block type
                if "db_id:" in block or "domain:" in block:
                    lines.append("```yaml")
                    lines.append(block.replace("```yaml", "").replace("```", "").strip())
                    lines.append("```")
                elif "CREATE TABLE" in block or "--" in block:
                    lines.append("```sql")
                    lines.append(block.replace("```sql", "").replace("```", "").strip())
                    lines.append("```")
                else:
                    lines.append("```text")
                    lines.append(block.replace("```text", "").replace("```", "").strip())
                    lines.append("```")
            lines.append("")

    lines.append("## Queries\n")

    for q in queries:
        header = q.get("_header")
        raw = q.get("_raw_json")
        if header:
            lines.append(header)
            lines.append("")
        if raw:
            lines.append("```json")
            lines.append(raw)
            lines.append("```")
            lines.append("")
        elif not header:
            # Fallback: generate from parsed
            n = q.get("question_id", q.get("number", 0))
            diff = q.get("difficulty", "moderate")
            cat = q.get("query_category", "aggregation")
            lines.append(f"### Query {n} — {diff} / {cat}")
            lines.append("")
            out = {k: v for k, v in q.items() if not k.startswith("_")}
            lines.append("```json")
            lines.append(json.dumps(out, indent=2, ensure_ascii=False))
            lines.append("```")
            lines.append("")

    return "\n".join(lines)


def _validate_structure_1to1(result: dict) -> list[str]:
    """Validate queries.json has 1:1 structure with queries.md (meta.sections keys)."""
    errs = []
    meta = result.get("meta", {})
    sections = meta.get("sections", {})
    preamble = meta.get("preamble", {})
    for name in _PREAMBLE_SECTIONS:
        if name not in sections and name not in preamble:
            errs.append(f"Missing section: {name}")
        elif name in sections:
            s = sections[name]
            if not isinstance(s, dict) or "block_type" not in s or "content" not in s:
                errs.append(f"Section {name} must have block_type and content")
    return errs


def validate_round_trip(db_num: int) -> dict:
    """Validate byte-for-byte round-trip: md → json → md. Also validates 1:1 structure."""
    db_dir = SOURCE / f"db-{db_num}"
    qd = _find_queries_dir(db_dir)
    qm = qd / "queries.md"
    qj = qd / "queries.json"

    if not qm.exists():
        return {"ok": False, "error": "queries.md not found"}

    original = qm.read_text(encoding="utf-8")
    original_bytes = original.encode("utf-8")

    # Extract
    result = _extract_template_format(original)
    if not result["data"]["queries"]:
        return {"ok": False, "error": "No queries extracted"}

    # Write json
    flat = {
        "db_id": f"db-{db_num}",
        "source_file": str(qm),
        "extraction_timestamp": get_est_timestamp(),
        "total_queries": len(result["data"]["queries"]),
        "queries": result["data"]["queries"],
        "_api_response": result,
    }
    qj.write_text(json.dumps(flat, indent=2, ensure_ascii=False), encoding="utf-8")

    # Render back to md
    rendered = render_json_to_md(db_num)
    if not rendered:
        return {"ok": False, "error": "Failed to render md from json"}

    # Compare (normalize trailing newlines for robustness)
    orig_norm = original.rstrip() + "\n"
    rend_norm = rendered.rstrip() + "\n"
    round_trip_ok = orig_norm == rend_norm

    result["validation"]["round_trip_ok"] = round_trip_ok
    result["validation"]["checksum_match"] = _sha256(rendered.encode("utf-8")) == result["submission"]["content_sha256"] if round_trip_ok else False

    # 1:1 structure validation
    structure_errs = _validate_structure_1to1(result)
    structure_ok = len(structure_errs) == 0
    result["validation"]["structure_1to1_ok"] = structure_ok
    if structure_errs:
        result["validation"]["structure_errors"] = structure_errs

    return {
        "ok": round_trip_ok and structure_ok,
        "db_num": db_num,
        "byte_count": len(original_bytes),
        "checksum": result["submission"]["content_sha256"],
        "round_trip_ok": round_trip_ok,
        "structure_1to1_ok": structure_ok,
        "structure_errors": structure_errs if structure_errs else None,
        "queries_count": len(result["data"]["queries"]),
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="queries.md ↔ queries.json byte-for-byte translator")
    ap.add_argument("command", choices=["extract", "render", "validate"], help="extract (md→json) | render (json→md) | validate (round-trip)")
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ... or empty for all")
    ap.add_argument("-a", "--all", action="store_true", help="All db-1..db-16")
    args = ap.parse_args()

    if args.all or not args.dbs:
        db_nums = list(range(1, 17))
    else:
        db_nums = []
        for a in args.dbs:
            n = str(a).replace("db-", "")
            try:
                db_nums.append(int(n))
            except ValueError:
                pass
        db_nums = sorted(set(db_nums))

    ok_count = 0
    for n in db_nums:
        if args.command == "extract":
            r = extract_md_to_json(n)
            if r:
                print(f"  db-{n}: OK extracted {r['meta']['total_queries']} queries → queries.json (API response)")
                ok_count += 1
            else:
                print(f"  db-{n}: SKIP (no queries.md)")
        elif args.command == "render":
            md = render_json_to_md(n)
            if md:
                qm = _find_queries_dir(SOURCE / f"db-{n}") / "queries.md"
                qm.write_text(md, encoding="utf-8")
                print(f"  db-{n}: OK rendered queries.json → queries.md")
                ok_count += 1
            else:
                print(f"  db-{n}: SKIP (no queries.json or no _raw)")
        else:  # validate
            v = validate_round_trip(n)
            if v.get("ok"):
                print(f"  db-{n}: OK round-trip + 1:1 structure validated ({v['queries_count']} queries)")
                ok_count += 1
            else:
                err = v.get("error", "")
                if v.get("structure_errors"):
                    err = "; ".join(v["structure_errors"]) or "structure mismatch"
                elif not err:
                    err = "round-trip or 1:1 structure mismatch"
                print(f"  db-{n}: FAIL {err}")

    print(f"\nDone: {ok_count}/{len(db_nums)}")
    return 0 if ok_count == len(db_nums) else 1


if __name__ == "__main__":
    sys.exit(main())
