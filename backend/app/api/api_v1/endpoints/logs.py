from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from app.db.session import get_db
from app.db.models import User, SystemLog
from app.schemas import SystemLogResponse, PaginatedResponse
from typing import Union
from app.api.deps import get_current_user, require_permission

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/", response_model=PaginatedResponse)
async def list_logs(
    page: int = 1,
    page_size: int = 50,
    action: Optional[str] = None,
    level: Optional[str] = None,
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List system logs"""
    query = select(SystemLog)
    count_query = select(SystemLog)

    if action:
        query = query.where(SystemLog.action == action)
        count_query = count_query.where(SystemLog.action == action)
    if level:
        query = query.where(SystemLog.level == level)
        count_query = count_query.where(SystemLog.level == level)
    if user_id:
        query = query.where(SystemLog.user_id == user_id)
        count_query = count_query.where(SystemLog.user_id == user_id)

    # Get total count
    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())

    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(desc(SystemLog.created_at))

    result = await db.execute(query)
    logs = result.scalars().all()

    # Convert to Pydantic models
    items = [SystemLogResponse.model_validate(l) for l in logs]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }