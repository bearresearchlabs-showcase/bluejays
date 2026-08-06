"""
SQL execution backends.

The environment is a POMDP over a database instance. Whether that instance is
actually reachable determines which reward regimes are available, so the backend
is explicit rather than assumed: a `NullBackend` is a first-class citizen that
reports honestly that execution reward is unavailable.

Backends
--------
NullBackend      no database. Only exact-match reward. This is what you get from
                 the shipped artifact alone, because expected_output is prose.
SQLiteBackend    schema transpiled from PostgreSQL and loaded into SQLite. Cheap,
                 in-process, good for tests and for schema-closure checking.
PostgresBackend  a real connection. Required to reproduce the gold result sets.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from typing import Any, Sequence

try:
    import sqlglot
    _SQLGLOT = True
except ImportError:  # pragma: no cover
    _SQLGLOT = False


@dataclass(frozen=True)
class Result:
    """The outcome of executing one action against an instance."""

    ok: bool
    columns: tuple[str, ...] = ()
    rows: tuple[tuple, ...] = ()
    error: str | None = None
    elapsed_ms: float = 0.0
    truncated: bool = False

    @property
    def n_rows(self) -> int:
        return len(self.rows)

    def head(self, k: int = 5) -> "Result":
        """Pi_k: the observation the agent actually receives after acting."""
        if len(self.rows) <= k:
            return self
        return Result(ok=self.ok, columns=self.columns, rows=self.rows[:k],
                      error=self.error, elapsed_ms=self.elapsed_ms, truncated=True)

    def as_multiset(self) -> collections_Counter:
        """Order-insensitive row bag, for set-equality reward."""
        import collections
        return collections.Counter(tuple(_canon(v) for v in r) for r in self.rows)

    def render(self, k: int = 5) -> str:
        if not self.ok:
            return f"ERROR: {self.error}"
        h = self.head(k)
        lines = [" | ".join(map(str, self.columns))]
        lines += [" | ".join("NULL" if v is None else str(v) for v in r) for r in h.rows]
        if h.truncated:
            lines.append(f"... ({self.n_rows} rows total)")
        elif not h.rows:
            lines.append("(0 rows)")
        return "\n".join(lines)


# a tiny alias so the type hint above reads cleanly without importing at module top
collections_Counter = Any


def _canon(v):
    """Canonicalise a cell so float noise and Decimal/str drift do not defeat equality."""
    from decimal import Decimal
    if isinstance(v, (int,)) and not isinstance(v, bool):
        return v
    if isinstance(v, Decimal):
        v = float(v)
    if isinstance(v, float):
        return round(v, 6)
    return v


class Backend:
    """Interface. `available` gates which reward regimes the env will offer."""

    available: bool = False
    name: str = "abstract"

    def execute(self, db: int, sql: str, timeout_s: float = 30.0) -> Result:
        raise NotImplementedError

    def close(self) -> None:
        pass


class NullBackend(Backend):
    """No instance. Every execution fails loudly rather than silently scoring 0."""

    available = False
    name = "null"

    def execute(self, db: int, sql: str, timeout_s: float = 30.0) -> Result:
        return Result(ok=False, error=(
            "no execution backend configured; execution-based reward is unavailable. "
            "The shipped expected_output field is prose, not a result relation "
            "(invariant I6), so ground truth must be materialised first: "
            "see mirrorsql.harness.materialize_ground_truth"))


class SQLiteBackend(Backend):
    """In-process SQLite, schema transpiled from PostgreSQL.

    Loads DDL only by default. Pass `data_sql` per database to load rows; the
    shipped data_large.sql files are ~1 GiB each and are not loaded implicitly.
    """

    name = "sqlite"

    def __init__(self, corpus, data_sql: dict[int, str] | None = None,
                 strict: bool = False):
        self.available = True
        self.corpus = corpus
        self._conn: dict[int, sqlite3.Connection] = {}
        self._skipped: dict[int, int] = {}
        self.strict = strict
        self.data_sql = data_sql or {}

    # -- DDL translation -------------------------------------------------
    @staticmethod
    def _translate(ddl: str) -> list[str]:
        """Split DDL into loadable statements.

        Leading `--` comment lines are stripped from each chunk first: schema
        files document every table, so a naive split leaves each CREATE behind a
        comment block and a startswith('--') test would drop the whole schema.
        """
        stmts: list[str] = []
        for raw in re.split(r";\s*\n", ddl):
            s = re.sub(r"\A(?:\s*--[^\n]*\n)+", "", raw).strip()
            if not s:
                continue
            if not re.match(r"CREATE\s+(TABLE|UNIQUE\s+INDEX|INDEX|VIEW)", s, re.I):
                continue
            if _SQLGLOT:
                try:
                    out = sqlglot.transpile(s, read="postgres", write="sqlite")
                    if out:
                        stmts.append(out[0])
                        continue
                except Exception:
                    pass
            stmts.append(s)
        return stmts

    def _get(self, db: int) -> sqlite3.Connection:
        if db in self._conn:
            return self._conn[db]
        conn = sqlite3.connect(":memory:")
        skipped = 0
        for stmt in self._translate(self.corpus[db].schema.ddl):
            try:
                conn.execute(stmt)
            except Exception:
                skipped += 1
                if self.strict:
                    raise
        if db in self.data_sql:
            with open(self.data_sql[db], errors="ignore") as f:
                buf = ""
                for line in f:
                    buf += line
                    if line.rstrip().endswith(";"):
                        try:
                            conn.execute(buf)
                        except Exception:
                            skipped += 1
                        buf = ""
        conn.commit()
        self._skipped[db] = skipped
        self._conn[db] = conn
        return conn

    def execute(self, db: int, sql: str, timeout_s: float = 30.0) -> Result:
        import time
        stmt = sql
        if _SQLGLOT:
            try:
                out = sqlglot.transpile(sql, read="postgres", write="sqlite")
                if out:
                    stmt = out[0]
            except Exception:
                pass
        conn = self._get(db)
        t0 = time.perf_counter()
        try:
            cur = conn.execute(stmt)
            rows = tuple(tuple(r) for r in cur.fetchall())
            cols = tuple(d[0] for d in (cur.description or ()))
            return Result(ok=True, columns=cols, rows=rows,
                          elapsed_ms=(time.perf_counter() - t0) * 1000)
        except Exception as e:
            return Result(ok=False, error=f"{type(e).__name__}: {e}",
                          elapsed_ms=(time.perf_counter() - t0) * 1000)

    def skipped_statements(self, db: int) -> int:
        """DDL statements SQLite could not accept. High counts mean low fidelity."""
        self._get(db)
        return self._skipped.get(db, 0)

    def close(self) -> None:
        for c in self._conn.values():
            c.close()
        self._conn.clear()


class PostgresBackend(Backend):
    """Real PostgreSQL. The only backend that reproduces the gold result sets."""

    name = "postgres"

    def __init__(self, dsn_for_db, connect=None):
        """dsn_for_db: int -> DSN string, or a dict {db: dsn}."""
        self.available = True
        if isinstance(dsn_for_db, dict):
            self._dsn = dsn_for_db.get
        else:
            self._dsn = dsn_for_db
        self._conn: dict[int, Any] = {}
        if connect is None:
            try:
                import psycopg
                connect = psycopg.connect
            except ImportError:  # pragma: no cover
                try:
                    import psycopg2
                    connect = psycopg2.connect
                except ImportError:
                    raise ImportError("PostgresBackend needs psycopg or psycopg2")
        self._connect = connect

    def _get(self, db: int):
        if db not in self._conn:
            self._conn[db] = self._connect(self._dsn(db))
        return self._conn[db]

    def execute(self, db: int, sql: str, timeout_s: float = 30.0) -> Result:
        import time
        conn = self._get(db)
        t0 = time.perf_counter()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SET LOCAL statement_timeout = {int(timeout_s * 1000)}")
                cur.execute(sql)
                rows = tuple(tuple(r) for r in cur.fetchall())
                cols = tuple(d[0] for d in (cur.description or ()))
            conn.rollback()
            return Result(ok=True, columns=cols, rows=rows,
                          elapsed_ms=(time.perf_counter() - t0) * 1000)
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            return Result(ok=False, error=f"{type(e).__name__}: {e}",
                          elapsed_ms=(time.perf_counter() - t0) * 1000)

    def close(self) -> None:
        for c in self._conn.values():
            try:
                c.close()
            except Exception:
                pass
        self._conn.clear()
