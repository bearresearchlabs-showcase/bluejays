"""
Evaluation harness.

Two jobs:

1. `materialize_ground_truth` -- execute every gold action against a loaded
   instance and persist the result relations. This is the single highest-value
   repair to the artifact: it converts the prose `expected_output` field into an
   oracle, making execution-based reward computable (invariant I6).

2. `evaluate` -- run a policy over a task pool and produce a report that is
   honest about what it could and could not score. Accuracy is reported both
   over the nominal task set and over the deduplicated one, because the gap
   between them is large (invariant I4) and reporting only the first inflates.
"""
from __future__ import annotations

import json
import os
import statistics
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from typing import Callable, Iterable, Sequence

from .backends import Backend, NullBackend
from .corpus import BROKEN_SCHEMA_ENVS, Corpus, Task
from .rewards import (ExactMatch, ExecutionMatch, PartialReward,
                      StructureMatch, RewardOutcome)

Policy = Callable[[Task, dict], str]


# ------------------------------------------------------- ground truth

def materialize_ground_truth(corpus: Corpus, backend: Backend, out_path: str,
                             dbs: Sequence[int] | None = None,
                             max_rows: int = 10_000,
                             timeout_s: float = 120.0) -> dict:
    """Execute every gold action; persist result relations as structured truth.

    Writes ``{task_id: {columns, rows, n_rows, elapsed_ms}}`` plus a manifest.
    Tasks whose environment fails schema closure are recorded as unexecutable
    rather than silently omitted.
    """
    if not backend.available:
        raise RuntimeError("materialize_ground_truth needs a live backend")
    truth: dict[str, dict] = {}
    stats = Counter()
    t0 = time.perf_counter()
    for env in corpus:
        if dbs is not None and env.db not in dbs:
            continue
        for task in env.tasks:
            if not task.executable:
                truth[task.task_id] = {"executable": False,
                                       "reason": "schema closure violation (I3)"}
                stats["unexecutable"] += 1
                continue
            res = backend.execute(task.db, task.sql, timeout_s)
            if not res.ok:
                truth[task.task_id] = {"executable": True, "ok": False,
                                       "error": res.error}
                stats["failed"] += 1
                continue
            rows = res.rows[:max_rows]
            truth[task.task_id] = {
                "executable": True, "ok": True,
                "columns": list(res.columns),
                "rows": [list(r) for r in rows],
                "n_rows": res.n_rows,
                "truncated": res.n_rows > max_rows,
                "elapsed_ms": round(res.elapsed_ms, 3),
            }
            stats["ok"] += 1
            if res.n_rows == 0:
                stats["empty"] += 1

    manifest = {
        "generated_s": round(time.perf_counter() - t0, 2),
        "backend": backend.name,
        "counts": dict(stats),
        "note": ("Empty result sets are counted separately: a gold action that "
                 "returns zero rows scores 1.0 against any other zero-row query "
                 "and is therefore a weak reward signal."),
    }
    with open(out_path, "w") as f:
        json.dump({"manifest": manifest, "truth": truth}, f)
    return manifest


def load_ground_truth(corpus: Corpus, path: str) -> int:
    """Attach persisted result relations to tasks. Returns how many were attached."""
    with open(path) as f:
        blob = json.load(f)
    truth = blob.get("truth", blob)
    n = 0
    for env in corpus:
        for i, task in enumerate(env.tasks):
            rec = truth.get(task.task_id)
            if rec and rec.get("ok"):
                env.tasks[i] = task.__class__(**{**{k: getattr(task, k)
                                                    for k in task.__dataclass_fields__},
                                                 "expected_rows": rec["rows"]})
                n += 1
    for env in corpus:                       # invalidate cached derived views
        for attr in ("clusters", "effective_tasks", "entropy",
                     "undeclared_tables", "schema_coverage", "is_clean"):
            env.__dict__.pop(attr, None)
    return n


# ------------------------------------------------------------- evaluate

@dataclass
class TaskResult:
    task_id: str
    db: int
    difficulty: float
    submitted: str
    scores: dict[str, float]
    computable: dict[str, bool]
    steps: int = 1
    error: str | None = None


@dataclass
class Report:
    n_tasks: int
    regimes: list[str]
    overall: dict[str, float] = field(default_factory=dict)
    by_db: dict[str, dict] = field(default_factory=dict)
    by_difficulty: dict[str, dict] = field(default_factory=dict)
    coverage: dict[str, float] = field(default_factory=dict)
    caveats: list[str] = field(default_factory=list)
    results: list[TaskResult] = field(default_factory=list)

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump({k: v for k, v in asdict(self).items()}, f, indent=2)

    def summary(self) -> str:
        L = [f"tasks scored: {self.n_tasks}"]
        for r in self.regimes:
            cov = self.coverage.get(r, 0.0)
            L.append(f"  {r:<16} {self.overall.get(r, 0.0):.3f}   "
                     f"(computable on {cov:.0%} of tasks)")
        if self.by_difficulty:
            L.append("  by difficulty quartile:")
            for q, d in self.by_difficulty.items():
                main = self.regimes[0]
                L.append(f"    {q}: n={d['n']:<4} {main}={d.get(main, 0.0):.3f}")
        for c in self.caveats:
            L.append(f"  ! {c}")
        return "\n".join(L)


def evaluate(corpus: Corpus, policy: Policy, *,
             backend: Backend | None = None,
             dedup: bool = True,
             executable_only: bool = False,
             dbs: Sequence[int] | None = None,
             regimes: Sequence[str] = ("exact_match",),
             limit: int | None = None,
             progress: bool = False) -> Report:
    """Score a policy over the corpus.

    `policy(task, obs) -> sql`. The observation dict mirrors MirrorEnv's o_0, so a
    policy written for the gym runs here unchanged.
    """
    backend = backend or NullBackend()
    fns = {}
    for r in regimes:
        fns[r] = {"exact_match": ExactMatch, "execution_match": ExecutionMatch,
                  "partial": PartialReward, "structure_match": StructureMatch}[r]()

    tasks = corpus.tasks(dedup=dedup, executable_only=executable_only, dbs=dbs)
    if limit:
        tasks = tasks[:limit]

    results: list[TaskResult] = []
    for i, task in enumerate(tasks):
        if progress and i % 25 == 0:
            print(f"  {i}/{len(tasks)}", flush=True)
        obs = {"schema": corpus[task.db].schema.ddl, "question": task.question,
               "context": task.description, "feedback": "", "step": 0,
               "steps_left": 1}
        try:
            sql = policy(task, obs)
            err = None
        except Exception as e:                       # a policy crash is a zero, not a stop
            sql, err = "", f"{type(e).__name__}: {e}"
        scores, computable = {}, {}
        for name, fn in fns.items():
            out: RewardOutcome = fn(task, sql, backend=backend)
            scores[name] = float(out.value)
            computable[name] = bool(out.computable)
        results.append(TaskResult(task.task_id, task.db, round(task.difficulty, 3),
                                  sql, scores, computable, error=err))

    return _aggregate(results, list(regimes), corpus, dedup, backend)


def _aggregate(results: list[TaskResult], regimes: list[str],
               corpus: Corpus, dedup: bool, backend: Backend) -> Report:
    rep = Report(n_tasks=len(results), regimes=regimes, results=results)
    if not results:
        return rep

    for r in regimes:
        usable = [x.scores[r] for x in results if x.computable[r]]
        rep.overall[r] = round(statistics.fmean(usable), 4) if usable else 0.0
        rep.coverage[r] = round(len(usable) / len(results), 4)

    by_db: dict[int, list[TaskResult]] = defaultdict(list)
    for x in results:
        by_db[x.db].append(x)
    for db, xs in sorted(by_db.items()):
        d = {"n": len(xs)}
        for r in regimes:
            u = [x.scores[r] for x in xs if x.computable[r]]
            d[r] = round(statistics.fmean(u), 4) if u else 0.0
        rep.by_db[f"db-{db}"] = d

    order = sorted(results, key=lambda x: x.difficulty)
    q = max(1, len(order) // 4)
    for i, label in enumerate(("Q1 easiest", "Q2", "Q3", "Q4 hardest")):
        chunk = order[i * q:(i + 1) * q] if i < 3 else order[3 * q:]
        if not chunk:
            continue
        d = {"n": len(chunk),
             "difficulty_range": [round(chunk[0].difficulty, 2),
                                  round(chunk[-1].difficulty, 2)]}
        for r in regimes:
            u = [x.scores[r] for x in chunk if x.computable[r]]
            d[r] = round(statistics.fmean(u), 4) if u else 0.0
        rep.by_difficulty[label] = d

    # -- caveats: state what the numbers do not mean -----------------------
    if not dedup:
        rep.caveats.append(
            "dedup=False: near-duplicate gold actions are scored repeatedly, which "
            "inflates accuracy on the eight affected environments (invariant I4).")
    if any(db in BROKEN_SCHEMA_ENVS for db in by_db):
        rep.caveats.append(
            f"pool includes db-{sorted(BROKEN_SCHEMA_ENVS)}, whose gold actions "
            "reference an undeclared base table (invariant I3); execution-based "
            "scores there are not computable.")
    for r in regimes:
        if rep.coverage[r] < 1.0:
            rep.caveats.append(
                f"{r} was computable on only {rep.coverage[r]:.0%} of tasks; the "
                "reported mean is over that subset, not the whole pool.")
    if not backend.available and "exact_match" in regimes:
        rep.caveats.append(
            "no execution backend: exact_match under-credits correct paraphrases and "
            "is a lower bound on true accuracy.")
    if any(x.error for x in results):
        rep.caveats.append(
            f"{sum(1 for x in results if x.error)} policy invocations raised; scored 0.")
    return rep


# --------------------------------------------------------------- policies

def gold_policy(task: Task, obs: dict) -> str:
    """Upper bound. Should score 1.0 under every computable regime."""
    return task.sql


def normal_query_policy(task: Task, obs: dict) -> str:
    """The simplified variant where present -- a calibrated weak baseline."""
    return task.normal_query or task.sql


def empty_policy(task: Task, obs: dict) -> str:
    """Lower bound. Any regime scoring this above 0 has a bug."""
    return "SELECT 1"


def majority_cluster_policy(corpus: Corpus) -> Policy:
    """A policy that has memorised exactly ONE query per environment: the gold
    action of the largest near-duplicate cluster.

    It knows 13 queries. Scored on the nominal 390-task pool it looks competent,
    because the duplicated behaviour is counted once per duplicate; scored on the
    222-task deduplicated pool it collapses. The gap is a direct measure of how
    much invariant I4 inflates a reported accuracy.
    """
    memo: dict[int, str] = {}
    for env in corpus:
        biggest = max(env.clusters, key=len)
        memo[env.db] = env.tasks[biggest[0]].sql

    def policy(task: Task, obs: dict) -> str:
        return memo.get(task.db, "SELECT 1")

    policy.__name__ = "majority_cluster_policy"
    return policy


def duplication_inflation(corpus: Corpus) -> dict:
    """Measure I4's effect on reported accuracy, with no model in the loop.

    Returns the memorise-one-query-per-environment score on both pools.
    """
    pol = majority_cluster_policy(corpus)
    out: dict = {"queries_memorised": len(corpus)}
    for regime in ("exact_match", "structure_match"):
        nominal = evaluate(corpus, pol, dedup=False, regimes=(regime,))
        dedup = evaluate(corpus, pol, dedup=True, regimes=(regime,))
        n, d = nominal.overall[regime], dedup.overall[regime]
        out[regime] = {
            "nominal_pool": nominal.n_tasks, "nominal_accuracy": n,
            "dedup_pool": dedup.n_tasks, "dedup_accuracy": d,
            "absolute_inflation": round(n - d, 4),
            "relative_inflation": round(n / d, 2) if d else float("inf"),
        }
    out["note"] = (
        "Exact match cannot see duplication: cluster members differ by a literal "
        "and are therefore unequal, so the memorised query scores only on itself. "
        "Under structure_match at the same tau that defines the clusters, the same "
        "13-query policy is credited for every duplicate.")
    return out
