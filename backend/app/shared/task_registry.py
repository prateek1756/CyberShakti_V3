"""In-process task ownership map so only the submitting user can poll results."""

from __future__ import annotations

from typing import Dict, Optional
from uuid import UUID

_task_owners: Dict[str, str] = {}


def register_task_owner(task_id: str, user_id: UUID) -> None:
    _task_owners[str(task_id)] = str(user_id)


def get_task_owner(task_id: str) -> Optional[str]:
    return _task_owners.get(str(task_id))
