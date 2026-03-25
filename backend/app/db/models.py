from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class LogLevel(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"


class DetectionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.VIEWER.value)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    logs = relationship("SystemLog", back_populates="user")


class DnsZone(Base):
    __tablename__ = "dns_zones"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    views = Column(Text)  # JSON string
    comment = Column(String(500))
    default_ttl = Column(Integer, default=3600)
    # Mapped key_* fields
    remark = Column(String(500))  # key_1
    purpose = Column(String(255))  # key_34
    system = Column(String(255))  # key_35
    department = Column(String(255))  # key_36
    owner_id = Column(String(50))  # key_37
    owner_name = Column(String(100))  # key_41
    proxy_type = Column(String(100))  # key_38
    open_scope = Column(String(255))  # key_39
    final_ip = Column(String(50))  # key_40
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    records = relationship("DnsRecord", back_populates="zone")


class DnsRecord(Base):
    __tablename__ = "dns_records"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("dns_zones.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(10), nullable=False)  # A, CNAME, MX, NS, etc.
    klass = Column(String(10), default="IN")
    ttl = Column(Integer, default=3600)
    rdata = Column(String(500))
    reverse_name = Column(String(255))
    is_enable = Column(String(10), default="yes")
    row_id = Column(Integer)
    comment = Column(Text)
    # Mapped key_* fields
    remark = Column(String(500))  # key_1
    purpose = Column(String(255))  # key_34
    system = Column(String(255))  # key_35
    department = Column(String(255))  # key_36
    owner_id = Column(String(50))  # key_37
    owner_name = Column(String(100))  # key_41
    # Detection results (per record)
    ping_status = Column(String(20), default=DetectionStatus.PENDING.value)
    ping_time = Column(DateTime)
    ping_result = Column(Text)
    curl_status = Column(String(20), default=DetectionStatus.PENDING.value)
    curl_time = Column(DateTime)
    curl_result = Column(Text)
    playwright_status = Column(String(20), default=DetectionStatus.PENDING.value)
    playwright_time = Column(DateTime)
    playwright_screenshot = Column(Text)  # base64
    playwright_result = Column(Text)
    ai_check_status = Column(String(20), default=DetectionStatus.PENDING.value)
    ai_check_time = Column(DateTime)
    ai_check_result = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    zone = relationship("DnsZone", back_populates="records")
    detection_logs = relationship("DetectionLog", back_populates="record")


class DetectionLog(Base):
    __tablename__ = "detection_logs"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("dns_records.id"), nullable=False)
    detection_type = Column(String(20), nullable=False)  # ping, curl, playwright, ai
    status = Column(String(20), nullable=False)
    result = Column(Text)
    screenshot = Column(Text)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    record = relationship("DnsRecord", back_populates="detection_logs")


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    level = Column(String(20), default=LogLevel.INFO.value)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    details = Column(Text)
    ip_address = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="logs")


class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    key = Column(String(100), nullable=False)
    value = Column(Text)
    value_type = Column(String(20), default="string")
    description = Column(String(255))
    is_visible = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())