from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from celery.result import AsyncResult
from app.worker import celery_app
from app.shared.auth import get_optional_current_user
from app.shared.models import User
from app.shared.task_registry import get_task_owner
from app.config import settings

router = APIRouter()


@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: str, current_user: Optional[User] = Depends(get_optional_current_user)):
    """
    Poll task execution status. Submitting user or guest may read the result.
    """
    try:
        UUID(task_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "INVALID_TASK_ID", "message": "Task ID format is invalid."}
        )

    owner = get_task_owner(task_id)
    user_id_str = str(current_user.id) if current_user else "guest"

    # Enforce task ownership in non-dev environments
    if settings.ENVIRONMENT.lower() not in ("dev", "development") and owner is not None:
        if owner != user_id_str and owner != "guest":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error_code": "FORBIDDEN", "message": "You cannot access this task."},
            )

    try:
        res = AsyncResult(task_id, app=celery_app)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "INVALID_TASK_ID", "message": "Task ID format is invalid."}
        )

    if res.state == "PENDING":
        return {"task_id": task_id, "status": "queued", "message": "Your request is waiting to be processed."}
    elif res.state == "STARTED":
        return {"task_id": task_id, "status": "processing", "message": "Analysis is in progress."}
    elif res.state == "SUCCESS":
        return {"task_id": task_id, "status": "complete", "result": res.result}
    elif res.state == "FAILURE":
        return {
            "task_id": task_id,
            "status": "error",
            "error_code": "TASK_EXECUTION_FAILED",
            "message": "Async processing failed.",
        }
    else:
        return {"task_id": task_id, "status": res.state.lower()}
