import os
from pathlib import Path


def find_project_root() -> Path:
    """
    Walk upward from the current working directory
    until a project root marker is found.

    Root markers:
    - pyproject.toml
    - .git directory

    Fallback: current working directory
    """
    current = Path.cwd().resolve()

    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent

    return current


def resolve_db_url():
    """
    Resolution priority:
    1. TRACEFORGE_DB_URL env variable
    2. Default local SQLite
    """

    env_url = os.getenv("TRACEFORGE_DB_URL")
    if env_url:
        return env_url

    root = find_project_root()
    tf_dir = root / ".traceforge"
    tf_dir.mkdir(exist_ok=True)

    return f"sqlite:///{tf_dir / 'traceforge.db'}"
