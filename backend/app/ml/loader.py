"""Load serialized ML artefacts from ml/artefacts. Missing files are not treated as trained models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

ARTEFACT_DIR = Path(__file__).resolve().parent / "models"


def artefact_path(name: str) -> Path:
    return ARTEFACT_DIR / name


def load_json(name: str) -> Optional[dict]:
    path = artefact_path(name)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_joblib(name: str) -> Any:
    path = artefact_path(name)
    if not path.is_file():
        return None
    import joblib

    return joblib.load(path)
