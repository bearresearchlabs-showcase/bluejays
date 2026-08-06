"""
Corpus loading for MIRROR-SQL.

Everything the environment needs about the artifact lives here: schemas, tasks,
the near-duplicate clustering that defines the *effective* action set, and the
derived difficulty measure that replaces the degenerate `complexity` field.

Nothing in this module executes SQL. See `backends.py` for that.
"""
from __future__ import annotations

import json
import math
import os
import re
import collections
import difflib
from dataclasses import dataclass, field
from functools import cached_property
from typing import Iterator, Sequence

try:
    import sqlglot
    from sqlglot import exp
    _SQLGLOT = True
except ImportError:  # pragma: no cover
    _SQLGLOT = False

DB_IDS: tuple[int, ...] = (2, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
DUP_TAU = 0.99

#: Environments whose gold actions are mutually distinct at DUP_TAU (invariant I4).
CLEAN_ENVS: frozenset[int] = frozenset({6, 7, 8, 9, 15})

#: Environments with a known schema-closure violation (invariant I3). Gold actions
#: here reference a base table the shipped schema does not declare, so any
#: execution-based reward is undefined. See Task.executable.
BROKEN_SCHEMA_ENVS: frozenset[int] = frozenset({3})

#: Recommended single environment: smallest that satisfies every invariant it can.
REFERENCE_ENV = 8


def _norm(sql: str) -> str:
    """Normalization nu used by the distinctness invariant."""
    return re.sub(r"\s+", " ", sql or "").strip().lower()


def _strip_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    return re.sub(r"--[^\n]*", " ", sql)


# --------------------------------------------------------------------- task

@dataclass(frozen=True)
class Task:
    """One episode's specification: a POMDP instance parameterisation."""

    db: int
    number: int
    question: str          # utterance q
    sql: str               # gold action a*
    description: str       # intent context c, part of o_0
    evidence: str          # rationale e, auxiliary supervision
    expected_output: str   # PROSE, not a relation -- see `expected_rows`
    complexity: str        # degenerate: constant "moderate" corpus-wide
    line_number: int
    title: str | None = None
    normal_query: str | None = None   # simplified variant -> preference pair
    expected_rows: list | None = None  # populated by harness.materialize()

    @property
    def task_id(self) -> str:
        return f"db-{self.db}/q{self.number}"

    @property
    def has_preference_pair(self) -> bool:
        return bool(self.normal_query)

    @property
    def executable(self) -> bool:
        """False when the environment violates schema closure (I3)."""
        return self.db not in BROKEN_SCHEMA_ENVS

    @cached_property
    def features(self) -> dict[str, int]:
        """AST features of the gold action. Basis for `difficulty`."""
        return ast_features(self.sql)

    @cached_property
    def difficulty(self) -> float:
        """kappa-hat: the derived replacement for the constant `complexity` tag."""
        return derived_difficulty(self.features)


def ast_features(sql: str) -> dict[str, int]:
    """CTE / join / window / subquery / base-table counts for one query."""
    if _SQLGLOT:
        try:
            t = sqlglot.parse_one(sql, dialect="postgres")
            ctes = {c.alias_or_name.lower() for c in t.find_all(exp.CTE)}
            tables = {x.name.lower() for x in t.find_all(exp.Table) if x.name}
            return {
                "cte": len(list(t.find_all(exp.CTE))),
                "join": len(list(t.find_all(exp.Join))),
                "window": len(list(t.find_all(exp.Window))),
                "subquery": len(list(t.find_all(exp.Subquery))),
                "agg": len(list(t.find_all(exp.AggFunc))),
                "tables": len(tables),
                "base_tables": len(tables - ctes),
            }
        except Exception:
            pass
    return {
        "cte": len(re.findall(r"[a-z_]\w*\s+AS\s*\(", sql, re.I)),
        "join": len(re.findall(r"\bJOIN\b", sql, re.I)),
        "window": len(re.findall(r"\bOVER\s*\(", sql, re.I)),
        "subquery": len(re.findall(r"\(\s*SELECT\b", sql, re.I)),
        "agg": len(re.findall(r"\b(COUNT|SUM|AVG|MIN|MAX)\s*\(", sql, re.I)),
        "tables": len(set(re.findall(r"\b(?:FROM|JOIN)\s+([a-z_]\w*)", sql, re.I))),
        "base_tables": len(set(re.findall(r"\b(?:FROM|JOIN)\s+([a-z_]\w*)", sql, re.I))),
    }


#: Weights for kappa-hat. Log-scaled so a query with 12 CTEs is not 4x one with 3.
DIFFICULTY_WEIGHTS = {"cte": 1.0, "join": 1.0, "window": 0.8,
                      "subquery": 0.8, "base_tables": 1.2}


def derived_difficulty(features: dict[str, int],
                       weights: dict[str, float] | None = None) -> float:
    """kappa-hat(tau) = sum_i w_i * log(1 + f_i).

    Replaces the shipped `complexity` field, which is the constant "moderate"
    across all 390 tasks and therefore induces the trivial partition.
    """
    w = weights or DIFFICULTY_WEIGHTS
    return sum(w[k] * math.log1p(features.get(k, 0)) for k in w)


# ------------------------------------------------------------------ schema

@dataclass(frozen=True)
class Schema:
    """The observable half of environment state: what the agent is told."""

    db: int
    ddl: str

    @cached_property
    def tables(self) -> frozenset[str]:
        return frozenset(
            t.lower() for t in re.findall(
                r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`\"]?(\w+)",
                _strip_comments(self.ddl), re.I))

    @cached_property
    def counts(self) -> dict[str, int]:
        d = _strip_comments(self.ddl)
        return {
            "tables": len(self.tables),
            "foreign_keys": len(re.findall(r"\bREFERENCES\s+[`\"]?\w+", d, re.I)),
            "indexes": len(re.findall(r"CREATE\s+(?:UNIQUE\s+)?INDEX\b", d, re.I)),
            "views": len(re.findall(
                r"CREATE\s+(?:OR\s+REPLACE\s+)?(?:MATERIALIZED\s+)?VIEW\b", d, re.I)),
        }

    def render(self, max_chars: int | None = None) -> str:
        """Schema as presented in o_0. Truncation is explicit, never silent."""
        if max_chars is None or len(self.ddl) <= max_chars:
            return self.ddl
        return self.ddl[:max_chars] + f"\n-- [truncated: {len(self.ddl)-max_chars} chars]"


# ---------------------------------------------------------------- corpus

@dataclass
class Environment:
    """One (schema, tasks) pair -- an environment in the paper's sense."""

    db: int
    schema: Schema
    tasks: list[Task]
    meta: dict = field(default_factory=dict)

    @cached_property
    def clusters(self) -> list[list[int]]:
        """Near-duplicate clusters over gold actions at DUP_TAU (invariant I4).

        Returns lists of task indices. len(clusters) is the effective action count.
        """
        return cluster_indices([t.sql for t in self.tasks])

    @cached_property
    def is_clean(self) -> bool:
        return len(self.clusters) == len(self.tasks)

    @cached_property
    def effective_tasks(self) -> list[Task]:
        """One representative per cluster: the hardest task in each.

        Training on `tasks` over-weights whatever behaviour a cluster repeats.
        """
        out = []
        for members in self.clusters:
            out.append(max((self.tasks[i] for i in members),
                           key=lambda t: t.difficulty))
        return sorted(out, key=lambda t: t.number)

    @cached_property
    def entropy(self) -> float:
        n = len(self.tasks)
        if n <= 1:
            return 0.0
        p = [len(c) / n for c in self.clusters]
        return -sum(x * math.log(x) for x in p) / math.log(n)

    @cached_property
    def undeclared_tables(self) -> frozenset[str]:
        """Base tables read by gold actions that the schema does not declare (I3)."""
        used: set[str] = set()
        for t in self.tasks:
            used |= base_tables(t.sql)
        return frozenset(used - self.schema.tables)

    @cached_property
    def schema_coverage(self) -> float:
        used: set[str] = set()
        for t in self.tasks:
            used |= base_tables(t.sql)
        return len(used & self.schema.tables) / len(self.schema.tables) if self.schema.tables else 0.0

    def __len__(self) -> int:
        return len(self.tasks)

    def __repr__(self) -> str:
        return (f"Environment(db-{self.db}, {len(self.tasks)} tasks, "
                f"{len(self.clusters)} effective, {len(self.schema.tables)} tables)")


def base_tables(sql: str) -> set[str]:
    """Physical tables a query reads, excluding CTE and derived-table names."""
    if _SQLGLOT:
        try:
            t = sqlglot.parse_one(sql, dialect="postgres")
            ctes = {c.alias_or_name.lower() for c in t.find_all(exp.CTE)}
            return {x.name.lower() for x in t.find_all(exp.Table)
                    if x.name and x.name.lower() not in ctes}
        except Exception:
            return set()
    ctes = {c.lower() for c in re.findall(r"([a-z_]\w*)\s+AS\s*\(", sql, re.I)}
    return {t.lower() for t in
            re.findall(r"\b(?:FROM|JOIN)\s+([a-z_]\w*)", sql, re.I)} - ctes


def cluster_indices(sqls: Sequence[str], tau: float = DUP_TAU) -> list[list[int]]:
    """Union-find over pairwise Ratcliff/Obershelp similarity of normalized SQL."""
    norm = [_norm(s) for s in sqls]
    k = len(norm)
    parent = list(range(k))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(k):
        for j in range(i + 1, k):
            if difflib.SequenceMatcher(None, norm[i], norm[j]).ratio() >= tau:
                a, b = find(i), find(j)
                if a != b:
                    parent[a] = b
    groups: dict[int, list[int]] = collections.defaultdict(list)
    for i in range(k):
        groups[find(i)].append(i)
    return [sorted(v) for v in groups.values()]


class Corpus:
    """The thirteen environments, loaded from a package root."""

    def __init__(self, root: str, dbs: Sequence[int] = DB_IDS):
        self.root = os.path.abspath(root)
        self.envs: dict[int, Environment] = {}
        for n in dbs:
            base = os.path.join(self.root, f"db-{n}")
            qpath = os.path.join(base, "QUERIES", "queries.json")
            spath = os.path.join(base, "DATABASE", "schema.sql")
            if not (os.path.exists(qpath) and os.path.exists(spath)):
                continue
            with open(qpath) as f:
                raw = json.load(f)
            with open(spath, errors="ignore") as f:
                ddl = f.read()
            tasks = [
                Task(db=n, number=q["number"], question=q["question"], sql=q["sql"],
                     description=q.get("description", ""), evidence=q.get("evidence", ""),
                     expected_output=q.get("expected_output", ""),
                     complexity=q.get("complexity", ""), line_number=q.get("line_number", 0),
                     title=q.get("title"), normal_query=q.get("normal_query"))
                for q in raw["queries"]
            ]
            self.envs[n] = Environment(
                db=n, schema=Schema(db=n, ddl=ddl), tasks=tasks,
                meta={k: v for k, v in raw.items() if k != "queries"})
        if not self.envs:
            raise FileNotFoundError(
                f"no environments found under {self.root!r}; expected db-N/QUERIES/queries.json")

    # -- access ----------------------------------------------------------
    def __getitem__(self, db: int) -> Environment:
        return self.envs[db]

    def __iter__(self) -> Iterator[Environment]:
        return iter(self.envs.values())

    def __len__(self) -> int:
        return len(self.envs)

    @property
    def db_ids(self) -> list[int]:
        return sorted(self.envs)

    def tasks(self, dedup: bool = False, executable_only: bool = False,
              dbs: Sequence[int] | None = None) -> list[Task]:
        """Flat task list.

        dedup            keep one representative per near-duplicate cluster (I4)
        executable_only  drop environments with a schema-closure violation (I3)
        """
        out: list[Task] = []
        for e in self:
            if dbs is not None and e.db not in dbs:
                continue
            if executable_only and e.db in BROKEN_SCHEMA_ENVS:
                continue
            out.extend(e.effective_tasks if dedup else e.tasks)
        return out

    def summary(self) -> dict:
        nominal = sum(len(e.tasks) for e in self)
        effective = sum(len(e.clusters) for e in self)
        return {
            "environments": len(self),
            "tasks_nominal": nominal,
            "tasks_effective": effective,
            "effective_ratio": round(effective / nominal, 3) if nominal else 0.0,
            "tables": sum(e.schema.counts["tables"] for e in self),
            "foreign_keys": sum(e.schema.counts["foreign_keys"] for e in self),
            "indexes": sum(e.schema.counts["indexes"] for e in self),
            "clean_environments": sorted(e.db for e in self if e.is_clean),
            "schema_closure_violations": {
                f"db-{e.db}": sorted(e.undeclared_tables)
                for e in self if e.undeclared_tables},
            "complexity_values": sorted({t.complexity for t in self.tasks()}),
            "preference_pairs": sum(1 for t in self.tasks() if t.has_preference_pair),
        }
