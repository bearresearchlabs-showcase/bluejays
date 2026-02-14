"""Pytest configuration. Sets minimal env for db_check tests that don't need a real DB."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


def _install_tb3_workbench():
    """Install tb3_workbench from ../pluto/tb3_workbench if not importable."""
    try:
        import tb3_workbench  # noqa: F401
        return True
    except ImportError:
        pass
    python = sys.executable
    venv_py = ROOT / ".venv" / "bin" / "python"
    if venv_py.exists():
        python = str(venv_py)
    for path in [ROOT.parent / "pluto" / "tb3_workbench", ROOT.parent / "tb3_workbench"]:
        if path.exists():
            # Prefer uv (venv may not have pip)
            for cmd in [
                ["uv", "pip", "install", "-e", str(path), "-q"],
                [python, "-m", "pip", "install", "-e", str(path), "-q"],
            ]:
                r = subprocess.run(cmd, capture_output=True, timeout=60, cwd=str(ROOT))
                if r.returncode == 0:
                    try:
                        import tb3_workbench  # noqa: F401
                        return True
                    except ImportError:
                        pass
                    break
    return False


def pytest_configure(config):
    """Install workbenches before test collection (so skipif sees tb3_workbench)."""
    _install_tb3_workbench()


@pytest.fixture(scope="session", autouse=True)
def _ensure_minimal_db_env():
    """Set PG_* if missing so db_check format/compliance/integrity can run (they don't connect)."""
    for k, v in [
        ("PG_HOST", "localhost"),
        ("PG_PORT", "5432"),
        ("PG_USER", "postgres"),
        ("PG_PASSWORD", "postgres"),
        ("PG_DATABASE", "postgres"),
    ]:
        if not os.getenv(k):
            os.environ[k] = v
