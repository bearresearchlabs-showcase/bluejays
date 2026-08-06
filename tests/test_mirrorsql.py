"""Tests for mirrorsql. Run: pytest -q  (set MIRRORSQL_ROOT to the corpus root)."""
import os, sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mirrorsql import (Corpus, MirrorEnv, EnvConfig, SQLiteBackend, NullBackend,
                      ExactMatch, ExecutionMatch, PartialReward, evaluate,
                      gold_policy, empty_policy, normal_query_policy,
                      preference_pair, derived_difficulty, cluster_indices,
                      BROKEN_SCHEMA_ENVS, CLEAN_ENVS, REFERENCE_ENV)

ROOT = os.environ.get("MIRRORSQL_ROOT", "/mnt/user-data/uploads/client/db")


@pytest.fixture(scope="module")
def corpus():
    return Corpus(ROOT)


# ---- corpus invariants (mirror the published audit) ----------------------

def test_corpus_shape(corpus):
    s = corpus.summary()
    assert s["environments"] == 13
    assert s["tasks_nominal"] == 390
    assert s["tables"] == 176

def test_i1_cardinality(corpus):
    assert all(len(e.tasks) == 30 for e in corpus)

def test_i3_schema_closure_violation_is_localised(corpus):
    bad = {e.db for e in corpus if e.undeclared_tables}
    assert bad == set(BROKEN_SCHEMA_ENVS) == {3}
    assert corpus[3].undeclared_tables == frozenset({"orders_order"})
    assert all(not t.executable for t in corpus[3].tasks)

def test_i4_effective_action_space(corpus):
    assert sum(len(e.clusters) for e in corpus) == 222
    assert {e.db for e in corpus if e.is_clean} == set(CLEAN_ENVS)
    assert len(corpus.tasks(dedup=True)) == 222
    assert len(corpus.tasks(dedup=False)) == 390

def test_i5_complexity_is_degenerate_but_derived_is_not(corpus):
    assert {t.complexity for t in corpus.tasks()} == {"moderate"}
    d = [t.difficulty for t in corpus.tasks()]
    assert max(d) - min(d) > 1.0          # the derived measure separates

def test_i6_expected_output_is_prose(corpus):
    assert all(not t.expected_output.lstrip().startswith(("[", "{"))
               for t in corpus.tasks())
    assert all(t.expected_rows is None for t in corpus.tasks())

def test_reference_env_is_clean_and_smallest(corpus):
    assert REFERENCE_ENV in CLEAN_ENVS
    clean = [e for e in corpus if e.is_clean]
    assert min(clean, key=lambda e: len(e.schema.tables)).db == REFERENCE_ENV


# ---- dedup / clustering --------------------------------------------------

def test_cluster_indices_partitions():
    sqls = ["select a from t", "select  A  FROM t", "select b from u"]
    cl = cluster_indices(sqls)
    assert sorted(len(c) for c in cl) == [1, 2]

def test_effective_tasks_pick_hardest_representative(corpus):
    e = corpus[10]
    assert len(e.effective_tasks) == len(e.clusters) < 30
    for members in e.clusters:
        rep = [t for t in e.effective_tasks if t.number in
               {e.tasks[i].number for i in members}]
        assert len(rep) == 1


# ---- rewards -------------------------------------------------------------

def test_exact_match_gold_and_empty(corpus):
    fn, t = ExactMatch(), corpus[8].tasks[0]
    assert fn(t, t.sql).value == 1.0
    assert fn(t, "SELECT 1").value == 0.0

def test_exact_match_is_formatting_invariant(corpus):
    # Indentation and keyword case must not matter. Newlines DO matter: the gold
    # SQL carries `--` line comments, so collapsing them changes the statement.
    fn, t = ExactMatch(), corpus[8].tasks[0]
    reindented = "\n".join("    " + ln.strip() for ln in t.sql.splitlines())
    assert fn(t, reindented).value == 1.0
    assert fn(t, "\n" + t.sql + "\n  ").value == 1.0

def test_execution_match_reports_incomputable_not_zero(corpus):
    out = ExecutionMatch()(corpus[8].tasks[0], "SELECT 1", backend=NullBackend())
    assert out.computable is False and out.value == 0.0
    assert "materialise" in out.detail or "backend" in out.detail

def test_execution_match_refuses_broken_env(corpus):
    out = ExecutionMatch()(corpus[3].tasks[0], "SELECT 1", backend=NullBackend())
    assert out.computable is False and "I3" in out.detail

def test_partial_reward_structure_component(corpus):
    t = corpus[8].tasks[0]
    hi = PartialReward()(t, t.sql, backend=NullBackend())
    lo = PartialReward()(t, "SELECT 1", backend=NullBackend())
    assert hi.value > lo.value

def test_preference_pairs_present_where_expected(corpus):
    n = sum(1 for t in corpus.tasks() if preference_pair(t))
    assert n == 150
    for t in corpus.tasks():
        p = preference_pair(t)
        assert p is None or (p[0] != p[1])


# ---- gym -----------------------------------------------------------------

def test_env_reset_and_submit(corpus):
    env = MirrorEnv(corpus, EnvConfig(dedup=True, reward="exact_match"))
    obs, info = env.reset(seed=0, options={"task_id": "db-8/q1"})
    assert set(obs) >= {"schema", "question", "context", "feedback", "steps_left"}
    assert info["task_id"] == "db-8/q1"
    t = [x for x in env.tasks if x.task_id == "db-8/q1"][0]
    obs, r, term, trunc, info = env.step("SUBMIT:" + t.sql)
    assert term and not trunc
    assert r == pytest.approx(1.0 - env.cfg.step_cost)
    assert info["reward"]["value"] == 1.0

def test_env_probe_costs_a_step_and_never_leaks_instance(corpus):
    env = MirrorEnv(corpus, EnvConfig(horizon=3, dedup=True))
    obs, _ = env.reset(seed=1)
    assert obs["feedback"] == ""            # o_0 carries no instance information
    obs, r, term, trunc, info = env.step("SELECT 1")
    assert not term and r == pytest.approx(-env.cfg.step_cost)
    assert obs["steps_left"] == 2

def test_env_truncates_at_horizon(corpus):
    env = MirrorEnv(corpus, EnvConfig(horizon=2, dedup=True))
    env.reset(seed=2)
    env.step("SELECT 1")
    _, _, term, trunc, _ = env.step("SELECT 1")
    assert trunc and not term

def test_env_pool_respects_filters(corpus):
    assert len(MirrorEnv(corpus, EnvConfig(dedup=True))) == 222
    assert len(MirrorEnv(corpus, EnvConfig(dedup=False))) == 390
    e = MirrorEnv(corpus, EnvConfig(dedup=False, executable_only=True))
    assert len(e) == 360 and all(t.db != 3 for t in e.tasks)

def test_env_deterministic_given_seed(corpus):
    a = MirrorEnv(corpus, EnvConfig()); b = MirrorEnv(corpus, EnvConfig())
    assert a.reset(seed=7)[1]["task_id"] == b.reset(seed=7)[1]["task_id"]


# ---- harness -------------------------------------------------------------

def test_gold_policy_scores_one_under_exact_match(corpus):
    rep = evaluate(corpus, gold_policy, dedup=True, regimes=("exact_match",))
    assert rep.n_tasks == 222
    assert rep.overall["exact_match"] == 1.0

def test_empty_policy_scores_zero(corpus):
    rep = evaluate(corpus, empty_policy, dedup=True, limit=40)
    assert rep.overall["exact_match"] == 0.0

def test_normal_query_policy_is_between(corpus):
    rep = evaluate(corpus, normal_query_policy, dedup=True,
                   dbs=[8], regimes=("exact_match",))
    assert 0.0 <= rep.overall["exact_match"] < 1.0

def test_report_states_caveats(corpus):
    rep = evaluate(corpus, gold_policy, dedup=False, limit=60)
    assert any("dedup=False" in c for c in rep.caveats)

def test_report_has_difficulty_breakdown(corpus):
    rep = evaluate(corpus, gold_policy, dedup=True, limit=80)
    assert len(rep.by_difficulty) == 4
    q1 = rep.by_difficulty["Q1 easiest"]["difficulty_range"]
    q4 = rep.by_difficulty["Q4 hardest"]["difficulty_range"]
    assert q4[0] >= q1[1]


# ---- sqlite backend ------------------------------------------------------

def test_sqlite_backend_loads_schemas(corpus):
    b = SQLiteBackend(corpus)
    r = b.execute(8, "SELECT COUNT(*) FROM user_profiles")
    assert r.ok and r.rows == ((0,),)
    b.close()

def test_sqlite_backend_surfaces_schema_closure_violation(corpus):
    b = SQLiteBackend(corpus)
    # The table the gold actions read is absent from the loaded schema...
    probe = b.execute(3, "SELECT * FROM orders_order LIMIT 0")
    assert not probe.ok and "orders_order" in (probe.error or "")
    # ...and the tables that ARE declared load fine, so this is I3, not a load failure.
    assert b.execute(3, "SELECT * FROM table1 LIMIT 0").ok
    # The gold action therefore cannot execute (the specific error may be a
    # dialect complaint raised before name resolution).
    assert not b.execute(3, corpus[3].tasks[0].sql).ok
    b.close()


def test_derived_difficulty_monotone_in_features():
    lo = derived_difficulty({"cte": 1, "join": 0, "window": 0, "subquery": 0, "base_tables": 1})
    hi = derived_difficulty({"cte": 6, "join": 4, "window": 3, "subquery": 2, "base_tables": 9})
    assert hi > lo > 0
