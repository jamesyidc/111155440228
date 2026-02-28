# 数据备份恢复系统设计文档

**设计日期：** 2026-02-04  
**版本：** v1.0.0  
**原则：** 安全稳定

---

## 🎯 系统概述

### 功能清单
1. **数据全部备份（发送方）** - 将本地数据打包备份
2. **数据全部备份（接收方）** - 从远程发送方备份所有数据
3. **数据全部恢复（发送方）** - 从备份文件恢复本地数据
4. **数据全部恢复（接收方）** - 将备份推送到远程接收方恢复

### 安全机制
- ✅ 登录认证（账号密码）
- ✅ Session管理
- ✅ 操作权限验证
- ✅ 备份加密（可选）
- ✅ 完整性校验
- ✅ 操作日志记录

---

## 🔐 登录认证系统

### 默认凭证
```python
DEFAULT_CREDENTIALS = {
    "username": "admin",
    "password": "Tencent@123"
}
```

### 认证流程
```
1. 用户访问 /data-sync-manager
   ↓
2. 检查 Session
   ↓
3. 未登录 → 跳转登录页 /login
   ↓
4. 输入账号密码
   ↓
5. 验证成功 → 设置 Session → 进入管理界面
   ↓
6. 验证失败 → 显示错误 → 重新输入
```

### Session管理
- **存储方式：** Flask Session（服务器端）
- **有效期：** 24小时
- **密钥：** 随机生成（环境变量）

---

## 💾 备份/恢复架构

### 1. 数据全部备份（发送方）

#### 功能描述
在发送端本地创建完整数据备份，包含所有数据文件和配置。

#### 备份内容
- `data/` 目录下所有数据文件
- 配置文件（`data_sync_config.json`）
- 统计文件（`data_sender_stats.json`）
- 元数据（备份时间、版本、校验和）

#### 备份格式
```
backup_sender_YYYYMMDD_HHMMSS.tar.gz
  ├── metadata.json          # 备份元数据
  ├── config/               
  │   ├── data_sync_config.json
  │   └── data_sender_stats.json
  └── data/                 # 所有数据文件
      ├── anchor_daily/
      ├── coin_price_jsonl/
      ├── sar_jsonl/
      └── ...
```

#### 安全措施
- ✅ 备份前验证磁盘空间
- ✅ 压缩打包（节省空间）
- ✅ SHA-256校验和
- ✅ 存储到独立备份目录
- ✅ 保留最近N个备份

#### API设计
```python
POST /api/data-sync/backup/sender/create
Response:
{
  "success": true,
  "backup_file": "backup_sender_20260204_150000.tar.gz",
  "backup_path": "/home/user/webapp/backups/...",
  "file_size": "45.2 MB",
  "checksum": "sha256:abc123...",
  "timestamp": "2026-02-04T15:00:00+08:00"
}
```

---

### 2. 数据全部备份（接收方）

#### 功能描述
接收端从远程发送端拉取所有数据，并在本地创建备份。

#### 备份流程
```
1. 连接发送端（主网址验证）
   ↓
2. 获取数据目录（所有30个端点）
   ↓
3. 逐个拉取数据（带进度显示）
   ↓
4. 保存到本地临时目录
   ↓
5. 打包压缩
   ↓
6. 生成备份文件
   ↓
7. 更新接收端统计
```

#### 备份格式
```
backup_receiver_YYYYMMDD_HHMMSS.tar.gz
  ├── metadata.json          # 备份元数据
  ├── config/               
  │   ├── data_sync_config.json
  │   └── data_receiver_stats.json
  ├── sender_info.json       # 发送端信息
  └── synced_data/           # 同步的数据
      ├── PT001.json
      ├── PB001.json
      └── ...
```

#### 安全措施
- ✅ 主网址验证
- ✅ 认证令牌验证
- ✅ 分批拉取（避免超时）
- ✅ 失败重试机制
- ✅ 完整性校验

#### API设计
```python
POST /api/data-sync/backup/receiver/create
Body:
{
  "sender_url": "https://sender.com",
  "include_endpoints": ["PT001", "PB001", ...],  # 可选，默认全部
  "auth_token": "token123"  # 可选
}

Response:
{
  "success": true,
  "backup_file": "backup_receiver_20260204_150000.tar.gz",
  "synced_endpoints": 30,
  "total_size": "120.5 MB",
  "checksum": "sha256:def456...",
  "timestamp": "2026-02-04T15:00:00+08:00"
}
```

---

### 3. 数据全部恢复（发送方）

#### 功能描述
从备份文件恢复发送端的数据和配置。

#### 恢复流程
```
1. 选择备份文件
   ↓
2. 验证备份完整性（校验和）
   ↓
3. 解压到临时目录
   ↓
4. 读取 metadata.json
   ↓
5. 备份当前数据（恢复前快照）
   ↓
6. 恢复配置文件
   ↓
7. 恢复数据文件
   ↓
8. 验证恢复结果
   ↓
9. 重启相关服务
```

#### 安全措施
- ✅ 恢复前创建当前快照
- ✅ 校验备份文件完整性
- ✅ 逐步恢复（可回滚）
- ✅ 恢复后验证
- ✅ 操作日志记录

#### API设计
```python
POST /api/data-sync/restore/sender
Body:
{
  "backup_file": "backup_sender_20260204_150000.tar.gz",
  "create_snapshot": true,  # 恢复前创建快照
  "restore_config": true,   # 是否恢复配置
  "restore_data": true      # 是否恢复数据
}

Response:
{
  "success": true,
  "restored_files": 1250,
  "snapshot_created": "snapshot_20260204_151000.tar.gz",
  "timestamp": "2026-02-04T15:10:00+08:00",
  "message": "数据恢复成功"
}
```

---

### 4. 数据全部恢复（接收方）

#### 功能描述
将本地备份的数据推送到远程发送端进行恢复（危险操作，需二次确认）。

#### 恢复流程
```
1. 选择备份文件
   ↓
2. 验证备份完整性
   ↓
3. 解压读取数据
   ↓
4. 连接远程接收端（主网址验证）
   ↓
5. 发送恢复请求（需要接收端确认）
   ↓
6. 分批推送数据
   ↓
7. 验证推送结果
   ↓
8. 更新统计信息
```

#### 安全措施
- ✅ 二次确认（危险操作）
- ✅ 主网址验证
- ✅ 远程端必须授权
- ✅ 分批推送（带进度）
- ✅ 失败回滚机制

#### API设计
```python
POST /api/data-sync/restore/receiver
Body:
{
  "backup_file": "backup_receiver_20260204_150000.tar.gz",
  "target_url": "https://receiver.com",
  "auth_token": "token123",
  "force": false  # 强制恢复（需要特殊权限）
}

Response:
{
  "success": true,
  "pushed_endpoints": 30,
  "failed_endpoints": 0,
  "timestamp": "2026-02-04T15:20:00+08:00",
  "message": "数据恢复成功"
}
```

---

## 📁 目录结构

```
/home/user/webapp/
├── backups/                      # 备份存储目录
│   ├── sender/                  # 发送方备份
│   │   ├── backup_sender_20260204_150000.tar.gz
│   │   ├── backup_sender_20260203_140000.tar.gz
│   │   └── ...
│   ├── receiver/                # 接收方备份
│   │   ├── backup_receiver_20260204_150000.tar.gz
│   │   └── ...
│   └── snapshots/               # 恢复前快照
│       ├── snapshot_20260204_151000.tar.gz
│       └── ...
├── logs/
│   ├── backup_restore.log       # 备份恢复日志
│   └── auth.log                 # 认证日志
└── data/
    ├── auth_users.json          # 用户凭证（加密存储）
    └── ...
```

---

## 🔧 技术实现

### 核心模块

#### 1. 认证模块 (`auth_manager.py`)
```python
class AuthManager:
    def verify_credentials(username, password) -> bool
    def create_session(username) -> str
    def verify_session(session_id) -> bool
    def logout(session_id) -> bool
```

#### 2. 备份模块 (`backup_manager.py`)
```python
class BackupManager:
    def create_sender_backup() -> dict
    def create_receiver_backup(sender_url) -> dict
    def list_backups(backup_type) -> list
    def verify_backup(backup_file) -> bool
```

#### 3. 恢复模块 (`restore_manager.py`)
```python
class RestoreManager:
    def restore_sender(backup_file, options) -> dict
    def restore_receiver(backup_file, target_url) -> dict
    def create_snapshot() -> str
    def rollback_restore(snapshot_file) -> bool
```

---

## 🎨 前端界面设计

### 新增标签页

```
数据沟通备份系统
├── 🏠 首页
├── 📤 发送端
├── 📥 接收端
├── 📋 数据目录
├── 📖 接口文档
├── 💾 备份管理 ⭐ 新增
│   ├── 发送方备份
│   │   ├── 创建备份
│   │   ├── 备份列表
│   │   └── 数据恢复
│   └── 接收方备份
│       ├── 创建备份
│       ├── 备份列表
│       └── 数据恢复
└── 📝 日志
```

### 登录页面

```html
┌────────────────────────────────────┐
│   🔐 数据沟通备份系统               │
│                                    │
│   ┌──────────────────────────┐   │
│   │ 账号: [         ]        │   │
│   │ 密码: [         ]        │   │
│   │                           │   │
│   │   [  登  录  ]           │   │
│   └──────────────────────────┘   │
│                                    │
│   默认账号: admin                  │
│   默认密码: Tencent@123            │
└────────────────────────────────────┘
```

### 备份管理页面

```html
┌────────────────────────────────────────────────────┐
│ 💾 备份管理                                        │
├────────────────────────────────────────────────────┤
│                                                    │
│ 【发送方备份】                                      │
│                                                    │
│ [创建新备份]                                       │
│                                                    │
│ 备份列表:                                          │
│ ┌──────────────────────────────────────────────┐ │
│ │ 📦 backup_sender_20260204_150000.tar.gz     │ │
│ │    大小: 45.2 MB | 时间: 2026-02-04 15:00   │ │
│ │    [下载] [恢复] [删除]                      │ │
│ └──────────────────────────────────────────────┘ │
│                                                    │
│ 【接收方备份】                                      │
│                                                    │
│ [从发送端拉取备份]                                 │
│                                                    │
│ 备份列表:                                          │
│ ┌──────────────────────────────────────────────┐ │
│ │ 📦 backup_receiver_20260204_150000.tar.gz   │ │
│ │    大小: 120.5 MB | 时间: 2026-02-04 15:00  │ │
│ │    端点数: 30 | 发送端: https://sender.com  │ │
│ │    [下载] [恢复到远程] [删除]               │ │
│ └──────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘
```

---

## 🔒 安全策略

### 1. 认证安全
- ✅ 密码加密存储（bcrypt）
- ✅ Session超时机制
- ✅ 登录失败次数限制
- ✅ 操作日志记录

### 2. 备份安全
- ✅ 备份文件权限限制（600）
- ✅ 备份目录隔离
- ✅ 完整性校验（SHA-256）
- ✅ 可选加密存储

### 3. 恢复安全
- ✅ 恢复前确认
- ✅ 自动快照
- ✅ 回滚机制
- ✅ 操作审计

### 4. 网络安全
- ✅ HTTPS传输
- ✅ 主网址验证
- ✅ 令牌认证
- ✅ 请求限流

---

## 📊 数据流图

### 发送方备份流程
```
[发送端数据] → [打包压缩] → [生成校验和] → [存储备份文件]
                    ↓
              [更新备份列表]
                    ↓
              [返回备份信息]
```

### 接收方备份流程
```
[接收端] → [连接发送端] → [拉取数据] → [本地存储] → [打包备份]
              ↓                ↓
        [主网址验证]      [进度显示]
```

### 发送方恢复流程
```
[选择备份] → [验证完整性] → [创建快照] → [解压恢复] → [验证结果]
                                 ↓
                         [失败时回滚]
```

### 接收方恢复流程
```
[选择备份] → [验证完整性] → [连接接收端] → [推送数据] → [验证结果]
                                 ↓
                         [主网址验证]
```

---

## ⚠️ 注意事项

### 危险操作
1. **数据恢复**：会覆盖现有数据，需二次确认
2. **远程恢复**：会修改远程系统数据，需特殊权限
3. **删除备份**：不可逆操作，需确认

### 容量规划
- 单次备份大小：50-150 MB（估算）
- 建议保留备份数：最近10个
- 磁盘空间要求：至少5 GB

### 性能考虑
- 备份时间：2-5分钟（取决于数据量）
- 恢复时间：3-8分钟（取决于数据量）
- 网络传输：考虑带宽限制

---

## 🧪 测试计划

### 功能测试
- [ ] 登录认证
- [ ] Session管理
- [ ] 发送方备份创建
- [ ] 接收方备份创建
- [ ] 发送方数据恢复
- [ ] 接收方数据恢复
- [ ] 备份列表查询
- [ ] 备份文件下载
- [ ] 备份文件删除

### 安全测试
- [ ] 未授权访问拦截
- [ ] Session过期处理
- [ ] 备份文件完整性
- [ ] 恢复回滚机制
- [ ] 主网址验证

### 性能测试
- [ ] 大文件备份
- [ ] 并发备份请求
- [ ] 网络传输稳定性
- [ ] 磁盘IO性能

---

## 📝 开发清单

### Phase 1: 认证系统
- [ ] `auth_manager.py` - 认证管理器
- [ ] `/login` 路由 - 登录页面
- [ ] `/logout` 路由 - 登出
- [ ] Session中间件
- [ ] 登录页面模板

### Phase 2: 备份功能
- [ ] `backup_manager.py` - 备份管理器
- [ ] 发送方备份API
- [ ] 接收方备份API
- [ ] 备份列表API
- [ ] 前端备份界面

### Phase 3: 恢复功能
- [ ] `restore_manager.py` - 恢复管理器
- [ ] 发送方恢复API
- [ ] 接收方恢复API
- [ ] 快照机制
- [ ] 前端恢复界面

### Phase 4: 测试与文档
- [ ] 单元测试
- [ ] 集成测试
- [ ] 用户手册
- [ ] API文档

---

**设计完成时间：** 2026-02-04  
**下一步：** 开始实现认证系统
