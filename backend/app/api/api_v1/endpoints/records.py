from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from typing import List, Optional
from app.db.session import get_db
from app.db.models import User, DnsRecord, DnsZone, SystemLog
from app.schemas import DnsRecordResponse, DnsZoneResponse, RecordFilter, PaginatedResponse
from typing import Union
from app.api.deps import get_current_user, require_permission

router = APIRouter(prefix="/records", tags=["records"])


@router.get("/", response_model=PaginatedResponse)
async def list_records(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    type: Optional[str] = None,
    zone_id: Optional[int] = None,
    ping_status: Optional[str] = None,
    curl_status: Optional[str] = None,
    playwright_status: Optional[str] = None,
    ai_check_status: Optional[str] = None,
    purpose: Optional[str] = None,
    system: Optional[str] = None,
    department: Optional[str] = None,
    owner_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List DNS records with filters"""
    query = select(DnsRecord)
    count_query = select(func.count(DnsRecord.id))

    # Build filters
    filters = []
    if search:
        search_filter = or_(
            DnsRecord.name.ilike(f"%{search}%"),
            DnsRecord.rdata.ilike(f"%{search}%"),
            DnsRecord.remark.ilike(f"%{search}%"),
        )
        filters.append(search_filter)
    if type:
        filters.append(DnsRecord.type == type)
    if zone_id:
        filters.append(DnsRecord.zone_id == zone_id)
    if ping_status:
        filters.append(DnsRecord.ping_status == ping_status)
    if curl_status:
        filters.append(DnsRecord.curl_status == curl_status)
    if playwright_status:
        filters.append(DnsRecord.playwright_status == playwright_status)
    if ai_check_status:
        filters.append(DnsRecord.ai_check_status == ai_check_status)
    if purpose:
        filters.append(DnsRecord.purpose.ilike(f"%{purpose}%"))
    if system:
        filters.append(DnsRecord.system.ilike(f"%{system}%"))
    if department:
        filters.append(DnsRecord.department.ilike(f"%{department}%"))
    if owner_name:
        filters.append(DnsRecord.owner_name.ilike(f"%{owner_name}%"))

    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(DnsRecord.id.desc())

    result = await db.execute(query)
    records = result.scalars().all()

    # Convert to Pydantic models
    items = [DnsRecordResponse.model_validate(r) for r in records]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/{record_id}", response_model=DnsRecordResponse)
async def get_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single DNS record"""
    result = await db.execute(select(DnsRecord).where(DnsRecord.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found",
        )
    return record


# Zones router
zones_router = APIRouter(prefix="/zones", tags=["zones"])


@zones_router.get("/", response_model=List[DnsZoneResponse])
async def list_zones(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all DNS zones"""
    result = await db.execute(select(DnsZone).order_by(DnsZone.name))
    zones = result.scalars().all()
    return [DnsZoneResponse.model_validate(z) for z in zones]


@zones_router.get("/{zone_id}", response_model=DnsZoneResponse)
async def get_zone(
    zone_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single DNS zone"""
    result = await db.execute(select(DnsZone).where(DnsZone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found",
        )
    return DnsZoneResponse.model_validate(zone)