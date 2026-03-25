import httpx
import json
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.db.session import get_db
from app.db.models import User, DnsZone, DnsRecord, SystemLog, DetectionStatus
from app.api.deps import get_current_user, require_permission
from app.core.config import get_zdns_config, settings

router = APIRouter(prefix="/sync", tags=["sync"])


async def get_zdns_settings():
    """Get ZDNS settings from config cache with .env fallback"""
    return {
        "base_url": get_zdns_config("zdns_base_url", "https://10.10.250.3:20120/"),
        "username": get_zdns_config("zdns_username", "admin"),
        "password": get_zdns_config("zdns_password", ""),
    }


async def fetch_with_auth(url: str) -> dict:
    """Fetch data from ZDNS API with basic auth"""
    zdns = await get_zdns_settings()
    async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
        response = await client.get(
            url,
            auth=(zdns["username"], zdns["password"]),
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch from ZDNS: {response.text}",
            )
        return response.json()


@router.post("/zones")
async def sync_zones(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("sync:execute")),
):
    """Sync shared zones from ZDNS"""
    try:
        zdns = await get_zdns_settings()
        data = await fetch_with_auth(f"{zdns['base_url']}shared-zones")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to connect to ZDNS: {str(e)}",
        )

    resources = data.get("resources", [])
    display_attrs = data.get("display_attrs", {})
    attrs_map = {attr["id"]: attr["display_name"] for attr in display_attrs.get("attrs", [])}

    synced_count = 0
    for zone_data in resources:
        zone_id = zone_data.get("id") or zone_data.get("name")

        # Check if zone exists
        result = await db.execute(select(DnsZone).where(DnsZone.zone_id == zone_id))
        existing_zone = result.scalar_one_or_none()

        # Map key_* fields
        zone_fields = {
            "zone_id": zone_id,
            "name": zone_data.get("name", ""),
            "views": json.dumps(zone_data.get("views", [])),
            "comment": zone_data.get("comment", ""),
            "default_ttl": zone_data.get("default_ttl", 3600),
            "remark": zone_data.get("key_1", ""),
            "purpose": zone_data.get("key_34", ""),
            "system": zone_data.get("key_35", ""),
            "department": zone_data.get("key_36", ""),
            "owner_id": zone_data.get("key_37", ""),
            "owner_name": zone_data.get("key_41", ""),
            "proxy_type": zone_data.get("key_38", ""),
            "open_scope": zone_data.get("key_39", ""),
            "final_ip": zone_data.get("key_40", ""),
            "updated_at": datetime.utcnow(),
        }

        if existing_zone:
            for field, value in zone_fields.items():
                setattr(existing_zone, field, value)
        else:
            zone = DnsZone(**zone_fields)
            db.add(zone)
            synced_count += 1

    # Log action
    log = SystemLog(
        action="sync_zones",
        level="info",
        user_id=current_user.id,
        details=f"Synced {len(resources)} zones",
    )
    db.add(log)

    await db.commit()

    return {
        "message": "Zones synced successfully",
        "synced_count": synced_count,
        "updated_count": len(resources) - synced_count,
        "total": len(resources),
    }


@router.post("/records/{zone_id}")
async def sync_records(
    zone_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("sync:execute")),
):
    """Sync DNS records for a specific zone"""
    # Find zone in local DB
    result = await db.execute(select(DnsZone).where(DnsZone.zone_id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone {zone_id} not found. Please sync zones first.",
        )

    try:
        zdns = await get_zdns_settings()
        data = await fetch_with_auth(f"{zdns['base_url']}shared-zones/{zone_id}/share-rrs")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to connect to ZDNS: {str(e)}",
        )

    resources = data.get("resources", [])

    # Delete existing records for this zone
    await db.execute(
        DnsRecord.__table__.delete().where(DnsRecord.zone_id == zone.id)
    )

    synced_count = 0
    for record_data in resources:
        record = DnsRecord(
            zone_id=zone.id,
            name=record_data.get("name", ""),
            type=record_data.get("type", "A"),
            klass=record_data.get("klass", "IN"),
            ttl=record_data.get("ttl", 3600),
            rdata=record_data.get("rdata", ""),
            reverse_name=record_data.get("reverse_name", ""),
            is_enable=record_data.get("is_enable", "yes"),
            row_id=record_data.get("row_id"),
            comment=record_data.get("comment"),
            remark=record_data.get("key_1", ""),
            purpose=record_data.get("key_34", ""),
            system=record_data.get("key_35", ""),
            department=record_data.get("key_36", ""),
            owner_id=record_data.get("key_37", ""),
            owner_name=record_data.get("key_41", ""),
            # Reset detection status
            ping_status=DetectionStatus.PENDING.value,
            curl_status=DetectionStatus.PENDING.value,
            playwright_status=DetectionStatus.PENDING.value,
            ai_check_status=DetectionStatus.PENDING.value,
        )
        db.add(record)
        synced_count += 1

    # Log action
    log = SystemLog(
        action="sync_records",
        level="info",
        user_id=current_user.id,
        details=f"Synced {synced_count} records for zone {zone_id}",
    )
    db.add(log)

    await db.commit()

    return {
        "message": "Records synced successfully",
        "zone_id": zone_id,
        "synced_count": synced_count,
    }


@router.post("/all")
async def sync_all(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("sync:execute")),
):
    """Sync all zones and records"""
    # First sync zones
    try:
        zdns = await get_zdns_settings()
        zones_data = await fetch_with_auth(f"{zdns['base_url']}shared-zones")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to connect to ZDNS: {str(e)}",
        )

    resources = zones_data.get("resources", [])

    synced_zones = 0
    synced_records = 0

    for zone_data in resources:
        zone_id = zone_data.get("id") or zone_data.get("name")

        result = await db.execute(select(DnsZone).where(DnsZone.zone_id == zone_id))
        existing_zone = result.scalar_one_or_none()

        zone_fields = {
            "zone_id": zone_id,
            "name": zone_data.get("name", ""),
            "views": json.dumps(zone_data.get("views", [])),
            "comment": zone_data.get("comment", ""),
            "default_ttl": zone_data.get("default_ttl", 3600),
            "remark": zone_data.get("key_1", ""),
            "purpose": zone_data.get("key_34", ""),
            "system": zone_data.get("key_35", ""),
            "department": zone_data.get("key_36", ""),
            "owner_id": zone_data.get("key_37", ""),
            "owner_name": zone_data.get("key_41", ""),
            "proxy_type": zone_data.get("key_38", ""),
            "open_scope": zone_data.get("key_39", ""),
            "final_ip": zone_data.get("key_40", ""),
            "updated_at": datetime.utcnow(),
        }

        if existing_zone:
            for field, value in zone_fields.items():
                setattr(existing_zone, field, value)
            zone = existing_zone
        else:
            zone = DnsZone(**zone_fields)
            db.add(zone)
            synced_zones += 1

        await db.commit()

        # Sync records for this zone
        try:
            records_data = await fetch_with_auth(
                f"{zdns['base_url']}shared-zones/{zone_id}/share-rrs"
            )
            records = records_data.get("resources", [])

            # Delete existing records
            if zone.id:
                await db.execute(
                    DnsRecord.__table__.delete().where(DnsRecord.zone_id == zone.id)
                )

            for record_data in records:
                record = DnsRecord(
                    zone_id=zone.id,
                    name=record_data.get("name", ""),
                    type=record_data.get("type", "A"),
                    klass=record_data.get("klass", "IN"),
                    ttl=record_data.get("ttl", 3600),
                    rdata=record_data.get("rdata", ""),
                    reverse_name=record_data.get("reverse_name", ""),
                    is_enable=record_data.get("is_enable", "yes"),
                    row_id=record_data.get("row_id"),
                    comment=record_data.get("comment"),
                    remark=record_data.get("key_1", ""),
                    purpose=record_data.get("key_34", ""),
                    system=record_data.get("key_35", ""),
                    department=record_data.get("key_36", ""),
                    owner_id=record_data.get("key_37", ""),
                    owner_name=record_data.get("key_41", ""),
                    ping_status=DetectionStatus.PENDING.value,
                    curl_status=DetectionStatus.PENDING.value,
                    playwright_status=DetectionStatus.PENDING.value,
                    ai_check_status=DetectionStatus.PENDING.value,
                )
                db.add(record)
                synced_records += 1

            await db.commit()
        except Exception as record_err:
            # Continue with next zone if records sync fails
            pass

    # Log action
    log = SystemLog(
        action="sync_all",
        level="info",
        user_id=current_user.id,
        details=f"Synced {synced_zones} zones and {synced_records} records",
    )
    db.add(log)
    await db.commit()

    return {
        "message": "All data synced successfully",
        "synced_zones": synced_zones,
        "synced_records": synced_records,
    }