#!/usr/bin/env python3
"""
Generate README.md for database documentation (installation, specs, schema, data dictionary).
Single source of truth: config (template + _doc_config.yaml) + deliverable JSON.
No SCHEMA.md or DATA_DICTIONARY.md — schema and data dictionary come from deliverable JSON only.
Output is MDX-compatible markdown. Validates config against db_documentation.schema.json.

Usage:
    python3 scripts/generate_documentation_readme.py db-1 [db-2 ...]
    python3 scripts/generate_documentation_readme.py --validate db-1
    python3 scripts/generate_documentation_readme.py -a
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
TEMPLATE = ROOT / "template"
SCHEMAS = ROOT / "scripts" / "schemas"


def load_yaml(path: Path) -> dict:
    """Load YAML file."""
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except ImportError:
        raise SystemExit("PyYAML required: pip install pyyaml")
    except Exception as e:
        raise SystemExit(f"Failed to load {path}: {e}")


def load_json(path: Path) -> dict:
    """Load JSON file."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"Failed to load {path}: {e}")


def validate_config(config: dict, schema_path: Path) -> bool:
    """Validate config against JSON schema. Returns True if valid."""
    try:
        import jsonschema
    except ImportError:
        raise SystemExit("jsonschema required: pip install jsonschema")

    schema = load_json(schema_path)
    try:
        jsonschema.validate(instance=config, schema=schema)
        return True
    except jsonschema.ValidationError as e:
        print(f"Validation error: {e.message}", file=sys.stderr)
        if e.path:
            print(f"  at: {'/'.join(str(p) for p in e.path)}", file=sys.stderr)
        return False


def find_deliverable_json(db_dir: Path, db_num: int) -> Path | None:
    """Find db-N_deliverable.json (prefer format output with data_type/constraints)."""
    prefix = f"db{db_num}-"
    deliverable_dir = db_dir / "deliverable"
    candidates = [
        db_dir / "app" / "DOCUMENTATION" / f"db-{db_num}_deliverable.json",
        db_dir / "deliverable" / f"db-{db_num}_deliverable.json",
    ]
    # Prefer web-deployable dbN-*/db-N_deliverable.json (format output) over database_deliverable.json
    if deliverable_dir.exists():
        for item in sorted(deliverable_dir.iterdir()):
            if item.is_dir() and item.name.startswith(prefix):
                candidates.append(item / f"db-{db_num}_deliverable.json")
    candidates.append(db_dir / "deliverable" / "database_deliverable.json")
    for p in candidates:
        if p.exists():
            return p
    return None


def get_config(db_dir: Path, db_num: int) -> dict:
    """Load and merge config: per-db _doc_config.yaml over template."""
    template_path = TEMPLATE / "db_documentation_template.yaml"
    per_db_path = db_dir / "_doc_config.yaml"
    fallback_path = TEMPLATE / "_doc_config.yaml"

    base = {}
    if template_path.exists():
        base = load_yaml(template_path)
    elif fallback_path.exists():
        base = load_yaml(fallback_path)

    if per_db_path.exists():
        override = load_yaml(per_db_path)
        deep_merge(base, override)

    # Substitute db-N with actual id
    db_id = f"db-{db_num}"
    if "database" in base:
        base["database"]["id"] = db_id
        if base["database"].get("name") == "Database Name":
            # Use deliverable name if available
            deliv = find_deliverable_json(db_dir, db_num)
            if deliv:
                data = load_json(deliv)
                if "database" in data and "name" in data["database"]:
                    base["database"]["name"] = data["database"]["name"]

    return base


def deep_merge(base: dict, override: dict) -> None:
    """Merge override into base in-place."""
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            deep_merge(base[k], v)
        else:
            base[k] = v


def generate_readme(db_num: int, config: dict, deliverable: dict | None) -> str:
    """Generate README.md from config + deliverable JSON only (single source of truth)."""
    db_id = config["database"]["id"]
    db_name = config["database"].get("name", db_id)
    fm = config.get("frontmatter", {})
    title = fm.get("title") or f"{db_name} — Documentation"
    description = fm.get("description") or "Installation guide, specifications, schema, data dictionary."

    # MDX frontmatter (YAML between ---)
    lines = [
        "---",
        f"title: {title}",
        f"description: {description}",
        f"database: {db_id}",
        "---",
        "",
        f"# {title}",
        "",
        f"**Database:** {db_id}  ",
        f"**Content:** {description}",
        "",
        "---",
        "",
        "## Installation Guide",
        "",
    ]

    # Installation steps
    steps = config.get("installation_guide", {}).get("steps", [])
    for i, step in enumerate(steps, 1):
        lines.append(f"### Step {i}: {step.get('title', '')}")
        lines.append("")
        if step.get("description"):
            lines.append(step["description"].strip())
            lines.append("")
        if step.get("commands"):
            for cmd in step["commands"]:
                lines.append(f"```bash")
                lines.append(cmd.replace("db_name", f"db_{db_num}"))
                lines.append("```")
            lines.append("")
        lines.append("---")
        lines.append("")

    # Specifications
    lines.append("## Specifications")
    lines.append("")
    spec = config.get("specifications", {})
    if spec.get("postgresql_version"):
        lines.append(f"- **PostgreSQL:** {spec['postgresql_version']}")
    if spec.get("extensions"):
        lines.append(f"- **Extensions:** {', '.join(spec['extensions'])}")
    if spec.get("disk_space_mb"):
        lines.append(f"- **Disk:** {spec['disk_space_mb']} MB minimum")
    if spec.get("memory_mb"):
        lines.append(f"- **Memory:** {spec['memory_mb']} MB minimum")
    if spec.get("platforms"):
        lines.append(f"- **Platforms:** {', '.join(spec['platforms'])}")
    if spec.get("notes"):
        lines.append("")
        lines.append(spec["notes"].strip())
    lines.append("")
    lines.append("---")
    lines.append("")

    # Schema Overview (from deliverable JSON only — single source of truth)
    lines.append("## Schema Overview")
    lines.append("")
    if deliverable and "schema" in deliverable:
        sch = deliverable["schema"]
        total = sch.get("total_tables", len(sch.get("tables", [])))
        lines.append(f"**Total tables:** {total}")
        lines.append("")
        for t in sch.get("tables", []):
            desc = t.get("description", "") or "(see data dictionary)"
            lines.append(f"- `{t.get('name', '')}` — {desc}")
        lines.append("")
    else:
        lines.append("See deliverable JSON for schema. Run `/format` to generate.")
        lines.append("")
    lines.append("---")
    lines.append("")

    # Data Dictionary (from deliverable JSON only — single source of truth)
    lines.append("## Data Dictionary")
    lines.append("")
    if deliverable and "schema" in deliverable:
        sch = deliverable["schema"]
        for t in sch.get("tables", []):
            lines.append(f"### `{t.get('name', '')}`")
            lines.append("")
            for col in t.get("columns", []):
                ctype = col.get("data_type", "")
                cconst = col.get("constraints", "")
                cdesc = col.get("description", "")
                extra = f" — {cdesc}" if cdesc else ""
                lines.append(f"- `{col.get('name', '')}` {ctype} {cconst}{extra}")
            lines.append("")
    else:
        lines.append("See deliverable JSON for column-level documentation.")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generated by documentation workflow. MDX-compatible markdown.*")
    lines.append("")
    return "\n".join(lines)


def run(db_num: int, validate_only: bool, output_path: Path | None) -> bool:
    """Generate or validate README for one database."""
    db_dir = SOURCE / f"db-{db_num}"
    if not db_dir.exists():
        print(f"  db-{db_num}: SKIP (no source dir)", file=sys.stderr)
        return False

    schema_path = SCHEMAS / "db_documentation.schema.json"
    if not schema_path.exists():
        print(f"  Schema not found: {schema_path}", file=sys.stderr)
        return False

    config = get_config(db_dir, db_num)
    if not validate_config(config, schema_path):
        print(f"  db-{db_num}: Validation FAILED", file=sys.stderr)
        return False

    if validate_only:
        print(f"  db-{db_num}: OK (valid)")
        return True

    # Single source of truth: config + deliverable JSON (no SCHEMA.md or DATA_DICTIONARY.md)
    deliverable_path = find_deliverable_json(db_dir, db_num)
    deliverable = load_json(deliverable_path) if deliverable_path else None

    content = generate_readme(db_num, config, deliverable)

    out = output_path or (db_dir / "docs" / "README.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print(f"  db-{db_num}: OK -> {out}")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate README.md for database documentation")
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ... or empty for all")
    ap.add_argument("-a", "--all", action="store_true", help="All db-1..db-16")
    ap.add_argument("--validate", action="store_true", help="Validate config only, do not generate")
    ap.add_argument("-o", "--output", type=Path, help="Output path (default: source/db-N/docs/README.md)")
    args = ap.parse_args()

    if args.all or not args.dbs:
        db_nums = list(range(1, 17))
    else:
        db_nums = []
        for a in args.dbs:
            a = str(a).replace("db-", "")
            try:
                db_nums.append(int(a))
            except ValueError:
                pass
        if len(db_nums) == 2 and db_nums[0] < db_nums[1]:
            db_nums = list(range(db_nums[0], db_nums[1] + 1))
        db_nums = sorted(set(db_nums))

    mode = "Validating" if args.validate else "Generating"
    print(f"{mode} documentation for {len(db_nums)} database(s)...")
    out_path = args.output if len(db_nums) == 1 else None
    ok = sum(1 for n in db_nums if run(n, args.validate, out_path))
    print(f"\nDone: {ok}/{len(db_nums)}")
    return 0 if ok == len(db_nums) else 1


if __name__ == "__main__":
    sys.exit(main())
