"""
Reward functions -- equations (1)-(3) of the paper.

    R_em   exact match on normalized SQL             computable from the artifact alone
    R_ex   execution match on result multisets       needs a backend + materialised truth
    R_pa   partial: structure + result F1 + efficiency

`R_em` is the only regime the shipped artifact supports unaided, and it is a poor
objective: semantically equivalent SQL admits unboundedly many normalizations.
Anything serious wants `R_ex` or `R_pa`, which is why `harness.materialize_ground_truth`
exists.
"""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass
from typing import Protocol

from .backends import Backend, Result
from .corpus import Task, _norm

try:
    import sqlglot
    _SQLGLOT = True
except ImportError:  # pragma: no cover
    _SQLGLOT = False


@dataclass(frozen=True)
class RewardOutcome:
    """A scored submission. `components` is always populated for diagnosis."""

    value: float
    regime: str
    components: dict[str, float]
    detail: str = ""
    computable: bool = True

    def __float__(self) -> float:
        return self.value


class RewardFn(Protocol):
    name: str

    def __call__(self, task: Task, action: str, *,
                 backend: Backend | None = None) -> RewardOutcome: ...


# ------------------------------------------------------------ normalization

def canonical_sql(sql: str) -> str:
    """Stronger normalization than nu: parse and re-emit, so formatting and
    keyword case cannot inflate an exact-match score. Falls back to nu."""
    if _SQLGLOT:
        try:
            return sqlglot.parse_one(sql, dialect="postgres").sql(
                dialect="postgres", normalize=True, pretty=False).lower()
        except Exception:
            pass
    return _norm(sql)


# ------------------------------------------------------------ eq. (1) R_em

class ExactMatch:
    """R_em = 1[nu(a) = nu(a*)].

    Available without a database. Reported for comparability with prior work;
    not recommended as a training objective.
    """

    name = "exact_match"

    def __init__(self, canonical: bool = True):
        self.canonical = canonical

    def __call__(self, task: Task, action: str, *,
                 backend: Backend | None = None) -> RewardOutcome:
        f = canonical_sql if self.canonical else _norm
        hit = float(f(action) == f(task.sql))
        return RewardOutcome(hit, self.name, {"exact": hit},
                             "canonicalised" if self.canonical else "whitespace/case only")


class StructureMatch:
    """R_struct = 1[sim(nu(a), nu(a*)) >= tau] -- the component of R_pa that is
    computable with no database.

    Scored at the same tau that defines the near-duplicate clusters, this is the
    reward under which duplication becomes visible: exact match cannot see it,
    because members of a cluster differ by a literal and are therefore unequal.
    """

    name = "structure_match"

    def __init__(self, tau: float = 0.99, graded: bool = False):
        self.tau = tau
        self.graded = graded

    def __call__(self, task: Task, action: str, *,
                 backend: Backend | None = None) -> RewardOutcome:
        sim = difflib.SequenceMatcher(None, _norm(action), _norm(task.sql)).ratio()
        v = sim if self.graded else float(sim >= self.tau)
        return RewardOutcome(v, self.name, {"similarity": round(sim, 4)},
                             f"tau={self.tau}, graded={self.graded}")


# ------------------------------------------------------------ eq. (2) R_ex

class ExecutionMatch:
    """R_ex = 1[exec(a, I) =_set exec(a*, I)].

    Multiset equality modulo column order. Requires either a materialised
    `task.expected_rows` or a live backend to execute the gold action against.
    """

    name = "execution_match"

    def __init__(self, order_sensitive: bool = False, timeout_s: float = 30.0):
        self.order_sensitive = order_sensitive
        self.timeout_s = timeout_s

    def _gold(self, task: Task, backend: Backend | None) -> Result | None:
        if task.expected_rows is not None:
            return Result(ok=True, columns=(), rows=tuple(map(tuple, task.expected_rows)))
        if backend is not None and backend.available:
            return backend.execute(task.db, task.sql, self.timeout_s)
        return None

    def __call__(self, task: Task, action: str, *,
                 backend: Backend | None = None) -> RewardOutcome:
        if not task.executable:
            return RewardOutcome(
                0.0, self.name, {}, computable=False,
                detail=(f"db-{task.db} violates schema closure (I3): its gold actions "
                        "reference an undeclared base table, so exec(a*) is undefined"))
        if backend is None or not backend.available:
            if task.expected_rows is None:
                return RewardOutcome(
                    0.0, self.name, {}, computable=False,
                    detail="no backend and no materialised ground truth")
        gold = self._gold(task, backend)
        if gold is None or not gold.ok:
            return RewardOutcome(0.0, self.name, {}, computable=False,
                                 detail=f"gold action failed: {gold.error if gold else 'n/a'}")
        got = backend.execute(task.db, action, self.timeout_s) if backend else None
        if got is None:
            return RewardOutcome(0.0, self.name, {}, computable=False,
                                 detail="no backend to execute the candidate")
        if not got.ok:
            return RewardOutcome(0.0, self.name, {"executed": 0.0}, detail=got.error or "")
        if self.order_sensitive:
            hit = float(tuple(got.rows) == tuple(gold.rows))
        else:
            hit = float(got.as_multiset() == gold.as_multiset())
        return RewardOutcome(hit, self.name,
                             {"executed": 1.0, "row_match": hit,
                              "n_rows": float(got.n_rows), "n_gold": float(gold.n_rows)})


# ------------------------------------------------------------ eq. (3) R_pa

class PartialReward:
    """R_pa = l1*sim_struct + l2*F1(rows) + l3*eff.

    Structure similarity uses the canonicalised ASTs; F1 is over result-row
    multisets; efficiency compares candidate to gold latency, clipped to [0,1].
    Following the partial-reward design of Reasoning-SQL (arXiv:2503.23157).
    """

    name = "partial"

    def __init__(self, l_struct: float = 0.3, l_rows: float = 0.6,
                 l_eff: float = 0.1, timeout_s: float = 30.0):
        tot = l_struct + l_rows + l_eff
        self.l = (l_struct / tot, l_rows / tot, l_eff / tot)
        self.timeout_s = timeout_s
        self._ex = ExecutionMatch(timeout_s=timeout_s)

    @staticmethod
    def _struct(a: str, b: str) -> float:
        return difflib.SequenceMatcher(None, canonical_sql(a), canonical_sql(b)).ratio()

    @staticmethod
    def _f1(got: Result, gold: Result) -> float:
        g, t = got.as_multiset(), gold.as_multiset()
        inter = sum((g & t).values())
        if not inter:
            return 0.0
        p = inter / max(1, sum(g.values()))
        r = inter / max(1, sum(t.values()))
        return 2 * p * r / (p + r)

    def __call__(self, task: Task, action: str, *,
                 backend: Backend | None = None) -> RewardOutcome:
        struct = self._struct(action, task.sql)
        comp = {"struct": struct}
        if not task.executable or backend is None or not backend.available:
            # degrade gracefully but say so: structure-only is not R_pa
            return RewardOutcome(
                self.l[0] * struct / max(self.l[0], 1e-9) * self.l[0], self.name,
                comp, computable=False,
                detail="structure component only; no executable instance available")
        gold = self._ex._gold(task, backend)
        got = backend.execute(task.db, action, self.timeout_s)
        if gold is None or not gold.ok:
            return RewardOutcome(self.l[0] * struct, self.name, comp, computable=False,
                                 detail="gold action did not execute")
        if not got.ok:
            comp.update({"f1": 0.0, "eff": 0.0})
            return RewardOutcome(self.l[0] * struct, self.name, comp,
                                 detail=got.error or "candidate failed")
        f1 = self._f1(got, gold)
        eff = 1.0 if got.elapsed_ms <= gold.elapsed_ms else max(
            0.0, min(1.0, gold.elapsed_ms / max(got.elapsed_ms, 1e-6)))
        comp.update({"f1": f1, "eff": eff})
        v = self.l[0] * struct + self.l[1] * f1 + self.l[2] * eff
        return RewardOutcome(v, self.name, comp)


# ------------------------------------------------------- preference pairs

def preference_pair(task: Task) -> tuple[str, str] | None:
    """(rejected, chosen) = (normal_query, sql) with intent held constant.

    Present for 150 of 390 tasks. Because both members answer the same utterance,
    the interpretation confound of rollout-sampled pairs is removed by construction.
    """
    if not task.normal_query:
        return None
    return (task.normal_query, task.sql)


REGISTRY: dict[str, type] = {
    "exact_match": ExactMatch,
    "structure_match": StructureMatch,
    "execution_match": ExecutionMatch,
    "partial": PartialReward,
}


def make_reward(name: str = "exact_match", **kw):
    if name not in REGISTRY:
        raise KeyError(f"unknown reward {name!r}; choose from {sorted(REGISTRY)}")
    return REGISTRY[name](**kw)
