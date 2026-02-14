#!/usr/bin/env python3
"""
Integrity checks for database files: CRC-32, CRC-64, SHA-256.
Stores results in db-{N}/metadata/integrity.json.
"""

import hashlib
import json
import struct
from pathlib import Path
from typing import Dict, List, Optional

# Add scripts directory for timestamp_utils
import sys
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    from datetime import datetime
    def get_est_timestamp():
        return datetime.now().strftime('%Y%m%d-%H%M')

try:
    from db_logger import log
except ImportError:
    def log(*a, **k): pass


def crc32_bytes(data: bytes) -> str:
    """Compute CRC-32 (standard, same as binascii.crc32)."""
    import binascii
    crc = binascii.crc32(data) & 0xFFFFFFFF
    return f"0x{crc:08x}"


def crc64_ecma(data: bytes) -> str:
    """Compute CRC-64-ECMA. Uses crcmod if available, else fallback to custom."""
    try:
        import crcmod
        fn = crcmod.predefined.mkCrcFun('crc-64-ecma')
        crc = fn(data)
        return f"0x{crc:016x}"
    except (ImportError, AttributeError):
        # Fallback: use CRC-64-ECMA polynomial via simple implementation
        POLY = 0xC96C5795D7870F42
        table = []
        for i in range(256):
            crc = i
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ POLY
                else:
                    crc >>= 1
            table.append(crc & 0xFFFFFFFFFFFFFFFF)
        crc = 0
        for b in data:
            crc = table[(crc ^ b) & 0xFF] ^ (crc >> 8)
        return f"0x{crc:016x}"


def sha256_hex(data: bytes) -> str:
    """Compute SHA-256 hash."""
    return hashlib.sha256(data).hexdigest()


def compute_file_checksums(filepath: Path) -> Optional[Dict[str, str]]:
    """Compute CRC-32, CRC-64, SHA-256 for a file."""
    if not filepath.exists() or not filepath.is_file():
        return None
    try:
        data = filepath.read_bytes()
    except (OSError, IOError):
        return None
    return {
        "crc32": crc32_bytes(data),
        "crc64": crc64_ecma(data),
        "sha256": sha256_hex(data),
    }


def run_integrity_checks(root_dir: Path, db_nums: List[int]) -> int:
    """
    Run integrity checks for specified databases.
    Writes db-{N}/metadata/integrity.json.
    Returns 0 on success, 1 on failure.
    """
    import time
    start = time.perf_counter()
    log("integrity", "run", status="start", data={"db_nums": db_nums})
    root_dir = root_dir.resolve()
    all_ok = True

    from db_paths import get_data_dir, get_queries_dir

    for db_num in db_nums:
        db_dir = root_dir / "source" / f"db-{db_num}"
        meta_dir = db_dir / "metadata"
        if not db_dir.exists():
            print(f"  db-{db_num}: SKIP (directory not found)")
            continue

        data_dir = get_data_dir(db_dir)
        queries_dir = get_queries_dir(db_dir)
        meta_dir.mkdir(parents=True, exist_ok=True)
        integrity: Dict[str, dict] = {"timestamp": get_est_timestamp()}

        files_to_check = [
            ("schema.sql", data_dir / "schema.sql"),
            ("schema_postgresql.sql", data_dir / "schema_postgresql.sql"),
            ("queries.json", queries_dir / "queries.json"),
            ("data.sql", data_dir / "data.sql"),
        ]

        for name, path in files_to_check:
            if path.exists():
                checksums = compute_file_checksums(path)
                if checksums:
                    integrity[name] = checksums

        # Prefer schema.sql if both exist; otherwise use whichever exists
        if "schema_postgresql.sql" in integrity and "schema.sql" in integrity:
            integrity["schema_primary"] = "schema.sql"
        elif "schema_postgresql.sql" in integrity:
            integrity["schema_primary"] = "schema_postgresql.sql"
        elif "schema.sql" in integrity:
            integrity["schema_primary"] = "schema.sql"

        out_file = meta_dir / "integrity.json"
        out_file.write_text(json.dumps(integrity, indent=2))
        print(f"  db-{db_num}: OK (integrity.json updated)")

    duration_ms = (time.perf_counter() - start) * 1000
    log("integrity", "run", status="ok" if all_ok else "fail", duration_ms=duration_ms, data={"count": len(db_nums)})
    return 0 if all_ok else 1


def verify_integrity(root_dir: Path, db_num: int) -> bool:
    """
    Verify current file checksums against stored integrity.json.
    Returns True if all match, False otherwise.
    """
    root_dir = root_dir.resolve()
    db_dir = root_dir / "source" / f"db-{db_num}"
    integrity_file = db_dir / "metadata" / "integrity.json"

    if not integrity_file.exists():
        return True  # Nothing to verify

    try:
        stored = json.loads(integrity_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False

    path_map = {
        "schema.sql": db_dir / "data" / "schema.sql",
        "schema_postgresql.sql": db_dir / "data" / "schema_postgresql.sql",
        "queries.json": db_dir / "queries" / "queries.json",
        "data.sql": db_dir / "data" / "data.sql",
    }
    for key, val in stored.items():
        if key in ("timestamp", "schema_primary") or not isinstance(val, dict):
            continue
        path = path_map.get(key, db_dir / "data" / key)
        if not path.exists():
            continue
        current = compute_file_checksums(path)
        if not current:
            return False
        for alg in ("crc32", "sha256"):
            if alg in val and current.get(alg) != val[alg]:
                return False
    return True


if __name__ == "__main__":
    root = Path(__file__).parent.parent
    try:
        from db_args import parse_db_args
    except ImportError:
        def parse_db_args(a):
            if not a: return [1]
            if "-a" in a or "--all" in a: return list(range(1, 17))
            out = []
            for x in a:
                x = str(x).strip()
                if x.startswith("db-"): out.append(int(x.split("db-")[1]))
                elif x.isdigit(): out.append(int(x))
            return sorted(set(out)) if out else [1]
    dbs = parse_db_args(sys.argv[1:])
    if not dbs:
        dbs = [1]
    sys.exit(run_integrity_checks(root, dbs))
