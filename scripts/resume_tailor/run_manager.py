"""Run directory management — keeps all outputs isolated per invocation."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Package root discovery ──────────────────────────────────────────
# Walk up from this file to find the project root (where pyproject.toml lives)
_PACKAGE_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _PACKAGE_DIR.parent
_PROJECT_ROOT = _SCRIPTS_DIR.parent


def get_data_dir() -> Path:
    """Return the data/ directory (shared across runs)."""
    return _PROJECT_ROOT / "data"


def get_experiences_path() -> Path:
    """Return the path to the experience database.

    Priority: my_experiences.local.json → my_experiences.json
    """
    local = get_data_dir() / "my_experiences.local.json"
    default = get_data_dir() / "my_experiences.json"
    if local.exists():
        return local
    return default


def get_schema_dir() -> Path:
    """Return the schemas/ directory."""
    return _PROJECT_ROOT / "schemas"


class RunManager:
    """Creates and manages an isolated output directory per run."""

    def __init__(self, output_dir: Optional[Path | str] = None):
        self._dir = Path(output_dir) if output_dir else self._create_run_dir()

    @staticmethod
    def _create_run_dir() -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = _PROJECT_ROOT / f"resume_output_{timestamp}"
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    @property
    def dir(self) -> Path:
        return self._dir

    def write(self, filename: str, content: str) -> Path:
        """Write a file into the run directory. Returns the full path."""
        path = self._dir / filename
        path.write_text(content, encoding="utf-8")
        return path

    def write_json(self, filename: str, data: object) -> Path:
        """Write a JSON file into the run directory."""
        import json
        path = self._dir / filename
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path
