from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def suite_root() -> Path:
    return ROOT / "evals" / "historical_decisions"


@pytest.fixture
def memory_root() -> Path:
    return ROOT / "memory"


@pytest.fixture
def repo_root() -> Path:
    return ROOT
