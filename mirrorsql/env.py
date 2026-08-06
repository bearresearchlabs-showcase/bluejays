"""
MirrorEnv -- a Gymnasium environment implementing the paper's POMDP.

    M = <S, A, Omega, T, O, R, gamma>

    S        s_t = (Sigma_d, I_d, q, h_t)
    A        well-formed SELECT over Sigma_d, plus SUBMIT(a)
    Omega    o_0 = (Sigma_d, q, c);  o_t = Pi_k(r_{t-1})
    T        deterministic: s_{t+1} = s_t with h extended by (a_t, exec(a_t, I_d))
    R        -epsilon per non-terminal step; terminal reward from the chosen regime
    gamma    0.99, horizon H = 8

The instance I_d never appears in an observation except through the image of an
action the agent chose to take. That is the whole point: information about the
data is purchased with steps.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Sequence

import gymnasium as gym
from gymnasium import spaces

from .backends import Backend, NullBackend, Result
from .corpus import Corpus, Task
from .rewards import RewardOutcome, make_reward

SUBMIT_PREFIX = "SUBMIT:"


@dataclass
class EnvConfig:
    horizon: int = 8                 # H
    gamma: float = 0.99              # gamma (recorded; the algorithm applies it)
    step_cost: float = 0.02          # epsilon
    observation_rows: int = 5        # k in Pi_k
    schema_max_chars: int | None = 24_000
    reward: str = "exact_match"      # exact_match | execution_match | partial
    timeout_s: float = 30.0
    dedup: bool = True               # sample from effective (clustered) task set
    executable_only: bool = False    # drop environments failing schema closure
    include_evidence: bool = False   # leak the rationale into o_0 (ablation only)
    max_text: int = 200_000


class MirrorEnv(gym.Env):
    """One episode = one task. `reset` selects a task; `step` takes SQL text.

    Action strings are plain SQL. Prefix with ``SUBMIT:`` to terminate the episode
    with that query as the final answer; an unprefixed query is a probe, which
    costs a step and returns rows.
    """

    metadata = {"render_modes": ["ansi"]}

    def __init__(self, corpus: Corpus, config: EnvConfig | None = None,
                 backend: Backend | None = None,
                 dbs: Sequence[int] | None = None,
                 render_mode: str | None = None):
        super().__init__()
        self.corpus = corpus
        self.cfg = config or EnvConfig()
        self.backend = backend or NullBackend()
        self.render_mode = render_mode

        self._tasks: list[Task] = corpus.tasks(
            dedup=self.cfg.dedup, executable_only=self.cfg.executable_only, dbs=dbs)
        if not self._tasks:
            raise ValueError("task pool is empty after filtering")

        self.action_space = spaces.Text(max_length=self.cfg.max_text)
        self.observation_space = spaces.Dict({
            "schema": spaces.Text(max_length=self.cfg.max_text),
            "question": spaces.Text(max_length=8_192),
            "context": spaces.Text(max_length=8_192),
            "feedback": spaces.Text(max_length=self.cfg.max_text),
            "step": spaces.Discrete(self.cfg.horizon + 1),
            "steps_left": spaces.Discrete(self.cfg.horizon + 1),
        })

        self._reward_fn = make_reward(self.cfg.reward, timeout_s=self.cfg.timeout_s) \
            if self.cfg.reward != "exact_match" else make_reward("exact_match")
        self.task: Task | None = None
        self._t = 0
        self._history: list[tuple[str, Result]] = []

    # ------------------------------------------------------------- pool
    @property
    def tasks(self) -> list[Task]:
        return list(self._tasks)

    def __len__(self) -> int:
        return len(self._tasks)

    # ------------------------------------------------------------ reset
    def reset(self, *, seed: int | None = None,
              options: dict | None = None) -> tuple[dict, dict]:
        super().reset(seed=seed)
        options = options or {}
        if "task" in options:
            self.task = options["task"]
        elif "task_id" in options:
            wanted = options["task_id"]
            match = [t for t in self._tasks if t.task_id == wanted]
            if not match:
                raise KeyError(f"no task {wanted!r} in pool")
            self.task = match[0]
        elif "index" in options:
            self.task = self._tasks[int(options["index"]) % len(self._tasks)]
        else:
            self.task = self._tasks[int(self.np_random.integers(len(self._tasks)))]
        self._t = 0
        self._history = []
        return self._obs(""), self._info()

    # ------------------------------------------------------------- step
    def step(self, action: str) -> tuple[dict, float, bool, bool, dict]:
        assert self.task is not None, "call reset() first"
        self._t += 1
        text = (action or "").strip()
        submitting = text.upper().startswith(SUBMIT_PREFIX)
        sql = text[len(SUBMIT_PREFIX):].strip() if submitting else text

        if submitting:
            outcome = self._reward_fn(self.task, sql, backend=self.backend)
            reward = float(outcome.value) - self.cfg.step_cost
            info = self._info(outcome=outcome, submitted=sql)
            return self._obs("submitted"), reward, True, False, info

        res = self.backend.execute(self.task.db, sql, self.cfg.timeout_s)
        self._history.append((sql, res))
        truncated = self._t >= self.cfg.horizon
        reward = -self.cfg.step_cost
        if truncated:
            # horizon reached without a submission: no terminal reward
            return (self._obs(res.render(self.cfg.observation_rows)), reward,
                    False, True, self._info(probe=res))
        return (self._obs(res.render(self.cfg.observation_rows)), reward,
                False, False, self._info(probe=res))

    # ------------------------------------------------------ observation
    def _obs(self, feedback: str) -> dict:
        t = self.task
        assert t is not None
        env = self.corpus[t.db]
        return {
            "schema": env.schema.render(self.cfg.schema_max_chars),
            "question": t.question,
            "context": (t.description + ("\n\n" + t.evidence
                                         if self.cfg.include_evidence else "")),
            "feedback": feedback,
            "step": self._t,
            "steps_left": max(0, self.cfg.horizon - self._t),
        }

    def _info(self, **extra) -> dict:
        t = self.task
        info: dict[str, Any] = {
            "task_id": t.task_id if t else None,
            "db": t.db if t else None,
            "difficulty": round(t.difficulty, 3) if t else None,
            "features": t.features if t else None,
            "executable": t.executable if t else None,
            "has_preference_pair": t.has_preference_pair if t else None,
            "backend": self.backend.name,
            "reward_regime": self.cfg.reward,
        }
        out = extra.pop("outcome", None)
        if out is not None:
            info["reward"] = {"value": out.value, "regime": out.regime,
                              "components": out.components,
                              "computable": out.computable, "detail": out.detail}
        probe = extra.pop("probe", None)
        if probe is not None:
            info["probe"] = {"ok": probe.ok, "n_rows": probe.n_rows,
                             "elapsed_ms": round(probe.elapsed_ms, 3),
                             "error": probe.error}
        info.update(extra)
        return info

    # ---------------------------------------------------------- render
    def render(self):
        if self.render_mode != "ansi" or self.task is None:
            return None
        lines = [f"[{self.task.task_id}] step {self._t}/{self.cfg.horizon}",
                 f"Q: {self.task.question}"]
        for i, (sql, res) in enumerate(self._history, 1):
            head = re.sub(r"\s+", " ", sql)[:90]
            lines.append(f"  {i}. {head}  ->  "
                         f"{res.n_rows} rows" if res.ok else f"  {i}. {head}  ->  ERROR")
        return "\n".join(lines)

    def close(self):
        self.backend.close()


def make_env(root: str, **kw) -> MirrorEnv:
    """Convenience constructor: `make_env('/path/to/db', reward='exact_match')`."""
    cfg_keys = set(EnvConfig.__dataclass_fields__)
    cfg = EnvConfig(**{k: v for k, v in kw.items() if k in cfg_keys})
    rest = {k: v for k, v in kw.items() if k not in cfg_keys}
    return MirrorEnv(Corpus(root), config=cfg, **rest)
