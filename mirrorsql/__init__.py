"""
mirrorsql -- a Gymnasium environment and evaluation harness for the MIRROR-SQL
text-to-SQL reinforcement-learning corpus.

    from mirrorsql import Corpus, MirrorEnv, EnvConfig, evaluate

The package is written against the invariant audit published with the corpus:
where the artifact cannot support a reward regime it says so rather than
returning a plausible zero. See `corpus.BROKEN_SCHEMA_ENVS` (I3),
`Environment.clusters` (I4), `Task.difficulty` (I5) and
`harness.materialize_ground_truth` (I6).
"""
from .corpus import (Corpus, Environment, Schema, Task, DB_IDS, CLEAN_ENVS,
                     BROKEN_SCHEMA_ENVS, REFERENCE_ENV, DUP_TAU,
                     ast_features, derived_difficulty, cluster_indices, base_tables)
from .backends import Backend, NullBackend, SQLiteBackend, PostgresBackend, Result
from .rewards import (ExactMatch, ExecutionMatch, PartialReward, StructureMatch,
                      RewardOutcome,
                      make_reward, preference_pair, canonical_sql)
from .env import MirrorEnv, EnvConfig, make_env
from .harness import (evaluate, Report, TaskResult, materialize_ground_truth,
                      load_ground_truth, gold_policy, normal_query_policy, empty_policy,
                      majority_cluster_policy, duplication_inflation)

# deprecated: old name for MirrorEnv, kept for backwards compatibility
DB13Env = MirrorEnv

__version__ = "1.0.0"
__all__ = [
    "Corpus", "Environment", "Schema", "Task", "DB_IDS", "CLEAN_ENVS",
    "BROKEN_SCHEMA_ENVS", "REFERENCE_ENV", "DUP_TAU", "ast_features",
    "derived_difficulty", "cluster_indices", "base_tables",
    "Backend", "NullBackend", "SQLiteBackend", "PostgresBackend", "Result",
    "ExactMatch", "ExecutionMatch", "PartialReward", "StructureMatch", "RewardOutcome",
    "make_reward", "preference_pair", "canonical_sql",
    "MirrorEnv", "DB13Env", "EnvConfig", "make_env",
    "evaluate", "Report", "TaskResult", "materialize_ground_truth",
    "load_ground_truth", "gold_policy", "normal_query_policy", "empty_policy",
    "majority_cluster_policy", "duplication_inflation",
]
