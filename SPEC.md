# DNS Health Check System - Specification

## Project Overview

- **Project Name**: DNS Health Check System
- **Type**: Full-stack Web Application
- **Core Functionality**: 检测域名状态（ping、curl、playwright截图+AI判断），同步DNS数据，完整的RBAC权限管理
- **Target Users**: 运维人员、域名管理员

## Tech Stack

- **Backend**: FastAPI + async SQLAlchemy + JWT + RBAC
- **Frontend**: Vue 3 + Tailwind CSS + Pinia + Vue I18n
- **Database**: SQLite (default, 可切换 MySQL/PostgreSQL)
- **Detection**: ping, curl, playwright, OpenAI API

## Functionality Specification

### 1. Data Synchronization Module (同步模块)

#### 1.1 Sync Shared Zones
- API: `GET https://10.10.250.3:20120/shared-zones`
- Auth: Basic Auth (username/password from .env)
- Response: List of domains with metadata

#### 1.2 Sync DNS Records
- API: `GET https://10.10.250.3:20120/shared-zones/{zone_id}/share-rrs`
- Response: All DNS records (A, CNAME, MX, NS, etc.)

#### 1.3 Data Mapping
- Map `key_*` fields to meaningful names based on `display_attrs`:
  - key_1 → 备注 (remark)
  - key_34 → 域名用途 (purpose)
  - key_35 → 所属系统 (system)
  - key_36 → 所属单位 (department)
  - key_37 → 责任人 (owner_id)
  - key_38 → 代理类型 (proxy_type)
  - key_39 → 开放范围 (open_scope)
  - key_40 → 最终解析IP (final_ip)
  - key_41 → 责任人姓名 (owner_name)

### 2. Health Detection Module (检测模块)

#### 2.1 Detection Types

| Record Type | Detection Method |
|-------------|------------------|
| A | ping IP + curl domain + playwright screenshot + AI判断 |
| CNAME | 解析到目标域名，再执行A记录检测 |
| MX | telnet/smtp检查邮件服务器端口(25) |
| NS | 检查NS服务器是否可解析 |

#### 2.2 Detection Status Fields
- `ping_status`: pending/running/success/failed/error
- `ping_time`: datetime
- `curl_status`: pending/running/success/failed/error
- `curl_time`: datetime
- `playwright_status`: pending/running/success/failed/error
- `playwright_screenshot`: base64 image
- `playwright_time`: datetime
- `ai_check_status`: pending/running/success/failed/error
- `ai_check_result`: AI判断结果
- `ai_check_time`: datetime

### 3. RBAC Module (权限模块)

#### 3.1 Roles
- Super Admin: 完全权限
- Admin: 用户管理、日志查看
- Operator: 执行检测、查看结果
- Viewer: 只读

#### 3.2 Permissions
- `user:manage` - 用户管理
- `sync:execute` - 执行同步
- `detect:execute` - 执行检测
- `detect:view` - 查看检测结果
- `log:view` - 查看日志

### 4. Logging Module (日志模块)

- System logs: 同步、检测等操作记录
- Login logs: 用户登录记录
- Audit logs: 重要操作审计

## Database Schema

### Tables

```sql
-- Users
users: id, username, password_hash, email, role, is_active, created_at

-- DNS Zones (共享区)
dns_zones: id, zone_id, name, views, comment, default_ttl, remark, purpose, system, department, owner_id, owner_name, proxy_type, open_scope, final_ip, created_at, updated_at

-- DNS Records
dns_records: id, zone_id, name, type, klass, ttl, rdata, reverse_name, is_enable, row_id, comment, purpose, system, department, owner_id, owner_name, remark, created_at, updated_at

-- Detection Results
detection_results: id, record_id, type (ping/curl/playwright/ai), status, result, screenshot, error_message, created_at

-- System Logs
system_logs: id, action, level, user_id, details, ip_address, created_at
```

## API Endpoints

### Auth
- POST /api/v1/auth/login
- POST /api/v1/auth/logout
- GET /api/v1/auth/me

### Users (RBAC)
- GET /api/v1/users/
- POST /api/v1/users/
- PUT /api/v1/users/{id}
- DELETE /api/v1/users/{id}

### Sync
- POST /api/v1/sync/zones - 同步共享区
- POST /api/v1/sync/records/{zone_id} - 同步指定区域的记录
- POST /api/v1/sync/all - 同步所有数据

### Detection
- POST /api/v1/detect/record/{record_id} - 检测单条记录
- POST /api/v1/detect/zone/{zone_id} - 检测整个区域
- POST /api/v1/detect/all - 检测所有记录

### DNS Records
- GET /api/v1/records/ - 列表（支持搜索过滤）
- GET /api/v1/records/{id} - 详情

### Logs
- GET /api/v1/logs/ - 系统日志

## Acceptance Criteria

1. ✅ 成功同步共享区域名数据
2. ✅ 成功同步DNS记录（包括A/CNAME/MX/NS）
3. ✅ ping检测功能正常
4. ✅ curl检测功能正常
5. ✅ playwright截图功能正常
6. ✅ AI判断页面是否正常
7. ✅ 支持key_*字段的搜索过滤
8. ✅ 完整的RBAC权限控制
9. ✅ 操作日志完整记录
10. ✅ 前后端分离，可独立运行