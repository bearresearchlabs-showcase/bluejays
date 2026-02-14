"""
Central logging and telemetry for DB check infrastructure.
Writes NDJSON to logs/db_check.log for structured parsing and monitoring.
Session-based logs go to traces/{session_id}/ for rerun.
"""

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from contextlib import contextmanager

# Log path: workspace logs directory
_scripts_dir = Path(__file__).parent
_root_dir = _scripts_dir.parent
_LOG_DIR = _root_dir / "logs"
_TRACES_DIR = _root_dir / "traces"
_LOG_FILE = _LOG_DIR / "db_check.log"
_TELEMETRY_FILE = _LOG_DIR / "telemetry.json"

# Session context (set by init_session)
_session_id: Optional[str] = None
_session_args: Optional[List[str]] = None

# Env keys to redact in config snapshot
_REDACT_KEYS = frozenset({"PG_PASSWORD", "ANTHROPIC_API_KEY", "PASSWORD", "SECRET", "API_KEY", "TOKEN"})


def _ensure_log_dir() -> Path:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    return _LOG_DIR


def _redact_env() -> Dict[str, str]:
    """Env snapshot with secrets redacted."""
    out = {}
    for k, v in os.environ.items():
        if any(r in k.upper() for r in _REDACT_KEYS):
            out[k] = "[REDACTED]"
        else:
            out[k] = str(v)
    return out


def _get_session_dir() -> Optional[Path]:
    """Return traces/{session_id}/ if session active."""
    if not _session_id:
        return None
    return _TRACES_DIR / _session_id


def init_session(session_id: Optional[str] = None, args: Optional[List[str]] = None) -> str:
    """
    Initialize session for trace logging.
    Creates traces/{session_id}/ with config.json.
    Returns session_id (generated if not provided).
    """
    global _session_id, _session_args
    _session_id = session_id or str(uuid.uuid4())
    _session_args = args or []
    d = _TRACES_DIR / _session_id
    d.mkdir(parents=True, exist_ok=True)
    config = {
        "session_id": _session_id,
        "args": _session_args,
        "env": _redact_env(),
        "ts": time.time(),
    }
    (d / "config.json").write_text(json.dumps(config, indent=2, default=str))
    return _session_id


def get_session_id() -> Optional[str]:
    """Return current session_id if set."""
    return _session_id


def _write_ndjson(record: Dict[str, Any]) -> None:
    """Append one NDJSON line to the log file."""
    try:
        _ensure_log_dir()
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
    except (OSError, IOError):
        pass


def _write_session_ndjson(record: Dict[str, Any]) -> None:
    """Append to traces/{session_id}/run.ndjson if session active."""
    d = _get_session_dir()
    if not d:
        return
    try:
        d.mkdir(parents=True, exist_ok=True)
        with open(d / "run.ndjson", "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
    except (OSError, IOError):
        pass


def log(
    component: str,
    action: str,
    status: str = "ok",
    message: str = "",
    data: Optional[Dict[str, Any]] = None,
    duration_ms: Optional[float] = None,
    session_id: Optional[str] = None,
) -> None:
    """
    Write a structured log entry.
    component: e.g. "db_check", "integrity", "pre_commit"
    action: e.g. "validate", "format", "qa_suite"
    status: "ok", "fail", "skip", "warn"
    """
    record = {
        "ts": time.time(),
        "component": component,
        "action": action,
        "status": status,
        "message": message or "",
        "data": data or {},
    }
    if duration_ms is not None:
        record["duration_ms"] = round(duration_ms, 2)
    _write_ndjson(record)
    sid = session_id or _session_id
    if sid:
        record["session_id"] = sid
        _write_session_ndjson(record)


@contextmanager
def log_span(component: str, action: str, data: Optional[Dict[str, Any]] = None, session_id: Optional[str] = None):
    """Context manager to log entry/exit with duration."""
    start = time.perf_counter()
    try:
        log(component, action, status="start", data=data, session_id=session_id)
        yield
        status = "ok"
        msg = ""
    except Exception as e:
        status = "fail"
        msg = str(e)[:200]
        raise
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        log(component, action, status=status, message=msg, duration_ms=duration_ms, session_id=session_id)


def record_telemetry(
    component: str,
    action: str,
    passed: int = 0,
    failed: int = 0,
    skipped: int = 0,
    extra: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
) -> None:
    """
    Record telemetry summary for aggregation.
    Merges into logs/telemetry.json (last run per component/action).
    """
    try:
        _ensure_log_dir()
        payload = {
            "component": component,
            "action": action,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "ts": time.time(),
            **(extra or {}),
        }
        # Append to telemetry log (NDJSON) for history
        with open(_LOG_DIR / "telemetry.ndjson", "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, default=str) + "\n")
        # Also update summary JSON (latest per key)
        summary_path = _LOG_DIR / "telemetry_summary.json"
        summary = {}
        if summary_path.exists():
            try:
                summary = json.loads(summary_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        key = f"{component}:{action}"
        summary[key] = payload
        summary_path.write_text(json.dumps(summary, indent=2))
        # Session telemetry
        sid = session_id or _session_id
        if sid:
            d = _TRACES_DIR / sid
            d.mkdir(parents=True, exist_ok=True)
            telemetry_path = d / "telemetry.json"
            session_summary = {}
            if telemetry_path.exists():
                try:
                    session_summary = json.loads(telemetry_path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    pass
            session_summary[key] = payload
            telemetry_path.write_text(json.dumps(session_summary, indent=2))
    except (OSError, IOError):
        pass


def get_log_path() -> Path:
    return _LOG_FILE


def get_telemetry_path() -> Path:
    return _LOG_DIR / "telemetry_summary.json"
