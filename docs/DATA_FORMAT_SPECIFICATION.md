# 数据沟通备份系统 - 数据格式规范

## 📋 核心设计原则

1. **双向认证**：发送端和接收端必须互相填写对方的主网址
2. **非主网址请求无效**：只有配置的主网址发出的请求才会被处理
3. **严格格式规范**：所有数据传输必须遵循统一的JSON格式
4. **扩展区域支持**：预留extensions字段用于后续功能扩展

## 🔐 主网址认证机制

### 概念说明

```
系统A (发送端)                系统B (接收端)
主网址: https://a.com         主网址: https://b.com

配置：                         配置：
- 发送端启用: ✅               - 接收端启用: ✅
- 接收端主网址列表:            - 发送端主网址:
  ["https://b.com"]              "https://a.com"
```

### 认证流程

**场景1：系统B向系统A请求数据**
```
1. 系统B发送请求到 https://a.com/api/data-sync/sender/data/PT001
2. 系统A检查：
   - 请求来源是否在接收端主网址列表中？
   - 如果 https://b.com 在列表中 → ✅ 允许访问
   - 如果不在列表中 → ❌ 拒绝访问
3. 返回数据或错误
```

**场景2：系统A向系统B发送数据**
```
1. 系统A主动推送数据到 https://b.com/api/data-sync/receiver/receive
2. 系统B检查：
   - 请求来源是否为配置的发送端主网址？
   - 如果是 https://a.com → ✅ 接受数据
   - 如果不是 → ❌ 拒绝数据
3. 保存数据或返回错误
```

## 📦 配置文件格式规范

### 1. 系统配置文件 (data_sync_config.json)

**完整格式定义**：

```json
{
  "system_info": {
    "system_id": "system_a",
    "system_name": "主系统A",
    "main_url": "https://a.example.com",
    "version": "1.0.0",
    "created_at": "2026-02-04T15:00:00+08:00",
    "updated_at": "2026-02-04T15:00:00+08:00"
  },
  
  "sender": {
    "enabled": true,
    "receiver_main_urls": [
      "https://b.example.com",
      "https://c.example.com"
    ],
    "auth_config": {
      "auth_enabled": true,
      "auth_token": "sender-secret-token-12345",
      "token_expires_at": "2027-02-04T15:00:00+08:00"
    },
    "security_config": {
      "ip_whitelist_enabled": false,
      "allowed_ips": [],
      "rate_limit_per_minute": 100,
      "max_request_size_mb": 10
    },
    "extensions": {
      "custom_field_1": "value1",
      "future_feature_config": {}
    }
  },
  
  "receiver": {
    "enabled": false,
    "sender_main_url": "https://remote.example.com",
    "auth_config": {
      "auth_token": "receiver-auth-token-67890",
      "token_expires_at": "2027-02-04T15:00:00+08:00"
    },
    "sync_config": {
      "auto_sync": true,
      "sync_interval_seconds": 300,
      "retry_on_failure": true,
      "max_retry_times": 3,
      "retry_interval_seconds": 60
    },
    "data_config": {
      "save_to_local": true,
      "local_data_path": "/home/user/webapp/data/synced_data",
      "backup_enabled": true,
      "backup_retention_days": 30
    },
    "extensions": {
      "custom_sync_rule": {},
      "future_feature_config": {}
    }
  },
  
  "endpoints": {
    "enabled_codes": [],
    "disabled_codes": [],
    "custom_endpoints": []
  },
  
  "extensions": {
    "system_level_config": {},
    "future_features": {},
    "custom_metadata": {}
  }
}
```

**字段说明**：

#### system_info（系统信息）
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| system_id | string | ✅ | 系统唯一标识（字母数字下划线） |
| system_name | string | ✅ | 系统显示名称 |
| main_url | string | ✅ | **本系统的主网址**（完整URL，含协议） |
| version | string | ✅ | 配置版本号 |
| created_at | string | ✅ | 创建时间（ISO 8601格式，含时区） |
| updated_at | string | ✅ | 更新时间（ISO 8601格式，含时区） |

#### sender（发送端配置）
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| enabled | boolean | ✅ | 是否启用发送端 |
| **receiver_main_urls** | **array** | **✅** | **允许访问的接收端主网址列表** |
| auth_config.auth_enabled | boolean | ✅ | 是否启用认证 |
| auth_config.auth_token | string | ❌ | 认证令牌（启用认证时必填） |
| auth_config.token_expires_at | string | ❌ | 令牌过期时间 |
| security_config.ip_whitelist_enabled | boolean | ✅ | 是否启用IP白名单 |
| security_config.allowed_ips | array | ❌ | 允许的IP列表 |
| security_config.rate_limit_per_minute | number | ✅ | 每分钟最大请求数 |
| security_config.max_request_size_mb | number | ✅ | 最大请求大小（MB） |
| **extensions** | **object** | **✅** | **扩展配置区域** |

#### receiver（接收端配置）
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| enabled | boolean | ✅ | 是否启用接收端 |
| **sender_main_url** | **string** | **✅** | **发送端主网址（接收端启用时必填）** |
| auth_config.auth_token | string | ❌ | 访问发送端的认证令牌 |
| auth_config.token_expires_at | string | ❌ | 令牌过期时间 |
| sync_config.auto_sync | boolean | ✅ | 是否启用自动同步 |
| sync_config.sync_interval_seconds | number | ✅ | 同步间隔（秒） |
| sync_config.retry_on_failure | boolean | ✅ | 失败时是否重试 |
| sync_config.max_retry_times | number | ✅ | 最大重试次数 |
| sync_config.retry_interval_seconds | number | ✅ | 重试间隔（秒） |
| data_config.save_to_local | boolean | ✅ | 是否保存到本地 |
| data_config.local_data_path | string | ✅ | 本地数据保存路径 |
| data_config.backup_enabled | boolean | ✅ | 是否启用备份 |
| data_config.backup_retention_days | number | ✅ | 备份保留天数 |
| **extensions** | **object** | **✅** | **扩展配置区域** |

## 📡 数据传输格式规范

### 1. 请求数据格式

#### 1.1 获取单个端点数据
```http
GET /api/data-sync/sender/data/{code}
Host: https://sender.example.com
Authorization: Bearer {auth_token}
X-Request-From: https://receiver.example.com
X-System-ID: system_b
```

**请求头规范**：
| Header | 必填 | 说明 |
|--------|------|------|
| Authorization | ✅ | Bearer令牌认证 |
| X-Request-From | ✅ | 请求方主网址 |
| X-System-ID | ✅ | 请求方系统ID |

#### 1.2 批量获取数据
```http
POST /api/data-sync/sender/batch
Host: https://sender.example.com
Content-Type: application/json
Authorization: Bearer {auth_token}
X-Request-From: https://receiver.example.com
X-System-ID: system_b

{
  "codes": ["PT001", "PB001", "AN001"],
  "params": {
    "limit": 100,
    "date": "2026-02-04"
  },
  "extensions": {}
}
```

**请求体格式**：
```json
{
  "codes": ["string"],
  "params": {
    "key": "value"
  },
  "extensions": {}
}
```

### 2. 响应数据格式

#### 2.1 成功响应（单个端点）
```json
{
  "success": true,
  "code": "PT001",
  "name": "最新价格追踪",
  "category": "price_tracker",
  "timestamp": "2026-02-04T15:30:00+08:00",
  "data_count": 29,
  "data": [
    {
      "coin": "BTC",
      "price": 76395.8,
      "timestamp": "2026-02-04T15:30:00+08:00",
      "extensions": {}
    },
    {
      "coin": "ETH",
      "price": 2267.71,
      "timestamp": "2026-02-04T15:30:00+08:00",
      "extensions": {}
    }
  ],
  "metadata": {
    "api_path": "/api/coin-price-tracker/latest",
    "method": "GET",
    "interval_seconds": 60,
    "data_file": "data/coin_price_jsonl/latest_price.jsonl",
    "last_updated": "2026-02-04T15:30:00+08:00"
  },
  "extensions": {}
}
```

**响应字段规范**：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| success | boolean | ✅ | 请求是否成功 |
| code | string | ✅ | 端点编码 |
| name | string | ✅ | 端点名称 |
| category | string | ✅ | 端点分类 |
| timestamp | string | ✅ | 响应时间戳（ISO 8601） |
| data_count | number | ✅ | 数据条数 |
| data | array | ✅ | 数据数组 |
| metadata | object | ✅ | 元数据信息 |
| **extensions** | **object** | **✅** | **扩展字段** |

#### 2.2 失败响应
```json
{
  "success": false,
  "error_code": "AUTH_FAILED",
  "error_message": "认证失败：请求来源不在允许的主网址列表中",
  "error_details": {
    "request_from": "https://unknown.example.com",
    "allowed_urls": [
      "https://b.example.com",
      "https://c.example.com"
    ]
  },
  "timestamp": "2026-02-04T15:30:00+08:00",
  "extensions": {}
}
```

**错误码规范**：
| 错误码 | 说明 |
|--------|------|
| AUTH_FAILED | 认证失败 |
| INVALID_MAIN_URL | 主网址验证失败 |
| ENDPOINT_NOT_FOUND | 端点不存在 |
| DATA_NOT_AVAILABLE | 数据不可用 |
| RATE_LIMIT_EXCEEDED | 超过频率限制 |
| INVALID_FORMAT | 数据格式错误 |
| SYSTEM_ERROR | 系统错误 |

#### 2.3 批量响应
```json
{
  "success": true,
  "total_requested": 3,
  "successful_count": 2,
  "failed_count": 1,
  "timestamp": "2026-02-04T15:30:00+08:00",
  "results": [
    {
      "code": "PT001",
      "success": true,
      "data_count": 29,
      "data": []
    },
    {
      "code": "PB001",
      "success": true,
      "data_count": 29,
      "data": []
    },
    {
      "code": "INVALID",
      "success": false,
      "error_code": "ENDPOINT_NOT_FOUND",
      "error_message": "端点不存在"
    }
  ],
  "extensions": {}
}
```

### 3. 数据项格式规范

#### 3.1 价格追踪数据（PT001, PT002）
```json
{
  "coin": "BTC",
  "symbol": "BTC-USDT-SWAP",
  "price": 76395.8,
  "timestamp": "2026-02-04T15:30:00+08:00",
  "volume_24h": 12345678.90,
  "change_24h": -2.5,
  "extensions": {}
}
```

#### 3.2 价格基准数据（PB001）
```json
{
  "symbol": "BTC-USDT-SWAP",
  "highest_price": 125370.20986,
  "highest_count": 6933,
  "lowest_price": 71649.95634,
  "lowest_count": 73,
  "last_price": 76395.8,
  "highest_ratio": 60.94,
  "lowest_ratio": 106.62,
  "last_update_time": "2026-02-04T15:11:43+08:00",
  "extensions": {}
}
```

#### 3.3 锚定利润数据（AN001, AN002）
```json
{
  "date": "2026-02-04",
  "total_profit": 1234.56,
  "profit_rate": 5.67,
  "position_count": 10,
  "avg_profit_per_position": 123.45,
  "timestamp": "2026-02-04T15:30:00+08:00",
  "extensions": {}
}
```

#### 3.4 SAR数据（SAR001, SAR002, SAR003）
```json
{
  "coin": "BTC",
  "cycle_id": "cycle_12345",
  "sar_value": 75000.00,
  "price": 76395.8,
  "bias": 1.86,
  "slope": 0.002,
  "direction": "up",
  "timestamp": "2026-02-04T15:30:00+08:00",
  "extensions": {}
}
```

## 🔧 扩展区域使用规范

### extensions字段说明

每个数据对象都包含`extensions`字段，用于：
1. 存储未来新增的功能配置
2. 存储自定义字段
3. 存储临时数据或元数据

**使用原则**：
- ✅ 使用有意义的字段名
- ✅ 使用驼峰命名（camelCase）
- ✅ 文档化所有自定义字段
- ❌ 不要覆盖标准字段
- ❌ 不要存储大量数据

**示例**：
```json
{
  "extensions": {
    "customFeature1": {
      "enabled": true,
      "config": {
        "param1": "value1"
      }
    },
    "futureFeature": {},
    "metadata": {
      "source": "system_a",
      "version": "1.0.0"
    }
  }
}
```

## 📐 时间格式规范

**统一使用ISO 8601格式，包含时区**：

```
格式：YYYY-MM-DDTHH:mm:ss+08:00

示例：
2026-02-04T15:30:00+08:00  ✅ 正确
2026-02-04 15:30:00        ❌ 错误（缺少T和时区）
2026-02-04T15:30:00Z       ⚠️  可用（UTC时间）
```

**Python生成示例**：
```python
from datetime import datetime
import pytz

# 生成带时区的时间戳
beijing_tz = pytz.timezone('Asia/Shanghai')
timestamp = datetime.now(beijing_tz).strftime('%Y-%m-%dT%H:%M:%S%z')
# 输出：2026-02-04T15:30:00+0800

# 添加冒号分隔时区
timestamp = datetime.now(beijing_tz).isoformat()
# 输出：2026-02-04T15:30:00+08:00
```

## 🔒 安全规范

### 1. 主网址验证
```python
def validate_main_url(request_url, allowed_urls):
    """
    验证请求来源主网址
    
    Args:
        request_url: 请求来源URL
        allowed_urls: 允许的主网址列表
    
    Returns:
        bool: 是否通过验证
    """
    from urllib.parse import urlparse
    
    # 解析请求URL
    parsed = urlparse(request_url)
    request_main = f"{parsed.scheme}://{parsed.netloc}"
    
    # 检查是否在允许列表中
    return request_main in allowed_urls
```

### 2. 认证令牌
- 长度：至少32字符
- 组成：字母、数字、连字符
- 存储：加密存储，不可明文
- 传输：仅通过HTTPS
- 过期：建议设置过期时间

### 3. 请求频率限制
- 默认：100次/分钟
- 建议：根据业务调整
- 超限：返回429状态码

## 📊 完整示例

### 系统A配置（作为发送端）
```json
{
  "system_info": {
    "system_id": "trading_system_a",
    "system_name": "交易系统A",
    "main_url": "https://trading-a.example.com",
    "version": "1.0.0"
  },
  "sender": {
    "enabled": true,
    "receiver_main_urls": [
      "https://backup-b.example.com",
      "https://monitor-c.example.com"
    ],
    "auth_config": {
      "auth_enabled": true,
      "auth_token": "sender-token-abc123def456"
    },
    "extensions": {
      "max_data_age_hours": 24
    }
  },
  "receiver": {
    "enabled": false,
    "sender_main_url": "",
    "extensions": {}
  }
}
```

### 系统B配置（作为接收端）
```json
{
  "system_info": {
    "system_id": "backup_system_b",
    "system_name": "备份系统B",
    "main_url": "https://backup-b.example.com",
    "version": "1.0.0"
  },
  "sender": {
    "enabled": false,
    "receiver_main_urls": [],
    "extensions": {}
  },
  "receiver": {
    "enabled": true,
    "sender_main_url": "https://trading-a.example.com",
    "auth_config": {
      "auth_token": "sender-token-abc123def456"
    },
    "sync_config": {
      "auto_sync": true,
      "sync_interval_seconds": 300
    },
    "extensions": {
      "priority_endpoints": ["PT001", "PB001"]
    }
  }
}
```

## 🎯 最佳实践

1. **总是填写主网址**：确保配置正确的主网址，包含协议（https://）
2. **定期更新令牌**：建议每3-6个月更换认证令牌
3. **记录所有扩展字段**：在extensions中添加的字段要有文档说明
4. **验证数据格式**：接收数据后验证必填字段和数据类型
5. **错误处理**：记录所有认证失败和格式错误
6. **监控日志**：定期检查非主网址的访问尝试

## 📝 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 1.0.0 | 2026-02-04 | 初始版本，定义核心格式规范 |

---

**重要提示**：
- ⚠️ 所有数据传输必须严格遵循本规范
- ⚠️ 非主网址的请求将被拒绝
- ⚠️ 扩展字段必须在extensions对象内
- ⚠️ 时间戳必须包含时区信息
