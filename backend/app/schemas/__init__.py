from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    role: str = "viewer"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# DNS Zone schemas
class DnsZoneBase(BaseModel):
    zone_id: str
    name: str
    views: Optional[str] = None
    comment: Optional[str] = None
    default_ttl: int = 3600
    remark: Optional[str] = None
    purpose: Optional[str] = None
    system: Optional[str] = None
    department: Optional[str] = None
    owner_id: Optional[str] = None
    owner_name: Optional[str] = None
    proxy_type: Optional[str] = None
    open_scope: Optional[str] = None
    final_ip: Optional[str] = None


class DnsZoneResponse(DnsZoneBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# DNS Record schemas
class DnsRecordBase(BaseModel):
    name: str
    type: str
    klass: str = "IN"
    ttl: int = 3600
    rdata: Optional[str] = None
    reverse_name: Optional[str] = None
    is_enable: str = "yes"
    row_id: Optional[int] = None
    comment: Optional[str] = None
    remark: Optional[str] = None
    purpose: Optional[str] = None
    system: Optional[str] = None
    department: Optional[str] = None
    owner_id: Optional[str] = None
    owner_name: Optional[str] = None


class DnsRecordResponse(DnsRecordBase):
    id: int
    zone_id: int
    ping_status: str
    ping_time: Optional[datetime] = None
    ping_result: Optional[str] = None
    curl_status: str
    curl_time: Optional[datetime] = None
    curl_result: Optional[str] = None
    playwright_status: str
    playwright_time: Optional[datetime] = None
    playwright_screenshot: Optional[str] = None
    playwright_result: Optional[str] = None
    ai_check_status: str
    ai_check_time: Optional[datetime] = None
    ai_check_result: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Detection Log schemas
class DetectionLogResponse(BaseModel):
    id: int
    record_id: int
    detection_type: str
    status: str
    result: Optional[str] = None
    screenshot: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# System Log schemas
class SystemLogResponse(BaseModel):
    id: int
    action: str
    level: str
    user_id: Optional[int] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Filter schemas
class RecordFilter(BaseModel):
    search: Optional[str] = None
    type: Optional[str] = None
    zone_id: Optional[int] = None
    ping_status: Optional[str] = None
    curl_status: Optional[str] = None
    playwright_status: Optional[str] = None
    ai_check_status: Optional[str] = None
    purpose: Optional[str] = None
    system: Optional[str] = None
    department: Optional[str] = None
    owner_name: Optional[str] = None


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20


from typing import List, TypeVar, Generic

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


# System Config Schemas
class SystemConfigBase(BaseModel):
    category: str
    key: str
    value: Optional[str] = None
    value_type: str = "string"
    description: Optional[str] = None
    is_visible: bool = True


class SystemConfigCreate(SystemConfigBase):
    pass


class SystemConfigUpdate(BaseModel):
    value: Optional[str] = None
    value_type: Optional[str] = None
    description: Optional[str] = None
    is_visible: Optional[bool] = None


class SystemConfigResponse(SystemConfigBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConfigCategoryResponse(BaseModel):
    category: str
    configs: List[SystemConfigResponse]


class ConfigBulkUpdate(BaseModel):
    category: str
    key: str
    value: Optional[str] = None
    value_type: Optional[str] = None
    description: Optional[str] = None
    is_visible: Optional[bool] = None


class ConfigBulkUpdateList(BaseModel):
    configs: List[ConfigBulkUpdate]