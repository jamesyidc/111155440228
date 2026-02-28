# 数据沟通备份系统

## 系统简介

数据沟通备份系统是一个双向数据同步平台，支持发送端（回复方）和接收端（请求方）两种模式，可以实现系统间的数据传输和备份。

### 核心特性

- **双向同步**：发送端和接收端可独立配置和启用
- **数据分类**：30个数据端点，涵盖12个分类（价格、SAR、锚定、交易等）
- **安全认证**：支持令牌认证和IP白名单
- **实时监控**：统计请求数、流量、成功率等
- **灵活配置**：支持自动同步和手动同步

## 系统架构

### 1. 数据源注册中心（data_sync_registry.py）

注册了30个数据端点，每个端点包含：
- **编码**（code）：唯一标识，如 PT001、PB001、AN001
- **分类**（category）：数据分类，如价格追踪、SAR数据、锚定系统
- **API路径**（api_path）：数据接口URL
- **更新间隔**（interval_seconds）：数据更新频率
- **数据文件**（data_file）：JSONL文件路径

**分类列表**：
- `price_tracker` - 价格追踪（2个端点）
- `price_speed` - 价格速度（1个端点）
- `price_baseline` - 价格基准（1个端点）
- `sar_data` - SAR数据（1个端点）
- `sar_bias` - SAR偏离（1个端点）
- `sar_slope` - SAR斜率（1个端点）
- `anchor_profit` - 锚定利润（2个端点）
- `anchor_system` - 锚定系统（2个端点）
- `coin_change` - 币种变化（2个端点）
- `okx_trading` - OKX交易（2个端点）
- `okx_positions` - OKX持仓（1个端点）
- `okx_orders` - OKX订单（1个端点）
- 更多...

### 2. 发送端（data_sync_sender.py）

**职责**：响应数据请求，提供数据

**API接口**：
- `GET /api/data-sync/sender/status` - 获取发送端状态
- `GET /api/data-sync/sender/catalog` - 获取数据目录
- `GET /api/data-sync/sender/data/<code>` - 获取单个端点数据
- `POST /api/data-sync/sender/batch` - 批量获取数据
- `GET /api/data-sync/sender/config` - 获取配置
- `POST /api/data-sync/sender/config` - 更新配置

**配置示例**：
```json
{
  "sender": {
    "enabled": true,
    "auth_token": "your-secret-token",
    "allowed_ips": ["192.168.1.100", "10.0.0.50"],
    "rate_limit": 100
  }
}
```

### 3. 接收端（data_sync_receiver.py）

**职责**：主动请求数据，从远程发送端同步

**API接口**：
- `GET /api/data-sync/receiver/status` - 获取接收端状态
- `POST /api/data-sync/receiver/sync-all` - 全量同步
- `POST /api/data-sync/receiver/sync/<code>` - 同步单个端点
- `POST /api/data-sync/receiver/start-auto-sync` - 启动自动同步
- `POST /api/data-sync/receiver/stop-auto-sync` - 停止自动同步
- `GET /api/data-sync/receiver/config` - 获取配置
- `POST /api/data-sync/receiver/config` - 更新配置

**配置示例**：
```json
{
  "enabled": true,
  "remote_url": "http://remote-server:5000",
  "auth_token": "remote-server-token",
  "sync_interval": 300,
  "auto_sync": true
}
```

### 4. Web管理界面

访问地址：`https://[你的域名]/data-sync-manager`

**功能页面**：

#### 总览（Overview）
- 发送端/接收端状态
- 注册端点总数
- 数据分类数
- 统计数据（请求数、流量等）

#### 发送端（Sender）
- 启用/禁用开关
- 认证令牌配置
- IP白名单配置
- 统计信息（总请求数、成功/失败数、最后请求时间）

#### 接收端（Receiver）
- 启用/禁用开关
- 远程发送端URL配置
- 认证令牌
- 同步间隔设置
- 自动同步控制
- 立即全量同步按钮
- 统计信息（总同步数、成功/失败数、最后同步时间）

#### 数据目录（Catalog）
- 30个数据端点列表
- 搜索功能
- 显示：编码、名称、API路径、方法、描述、更新间隔

#### 日志（Logs）
- 系统运行日志
- 同步日志
- 错误日志

## 使用指南

### 场景1：作为发送端（数据提供方）

1. 访问管理界面 `/data-sync-manager`
2. 切换到"发送端"标签
3. 启用发送端开关
4. （可选）配置认证令牌和IP白名单
5. 点击"保存配置"

**API测试**：
```bash
# 获取数据目录
curl http://localhost:5000/api/data-sync/sender/catalog

# 获取价格基准数据（PB001）
curl http://localhost:5000/api/data-sync/sender/data/PB001

# 获取锚定利润最新数据（AN001）
curl http://localhost:5000/api/data-sync/sender/data/AN001
```

### 场景2：作为接收端（数据请求方）

1. 访问管理界面 `/data-sync-manager`
2. 切换到"接收端"标签
3. 启用接收端开关
4. 填写远程发送端URL（如：`http://remote-server:5000`）
5. （如果远程需要）填写认证令牌
6. 设置同步间隔（秒）
7. 启用自动同步（可选）
8. 点击"保存配置"
9. 点击"启动自动同步"或"立即全量同步"

**API测试**：
```bash
# 立即全量同步
curl -X POST http://localhost:5000/api/data-sync/receiver/sync-all

# 同步单个端点
curl -X POST http://localhost:5000/api/data-sync/receiver/sync/PB001

# 查看同步状态
curl http://localhost:5000/api/data-sync/receiver/status
```

### 场景3：双向备份

两个系统互相作为对方的备份：

**系统A配置**：
- 发送端：启用（提供数据给系统B）
- 接收端：启用，远程URL指向系统B

**系统B配置**：
- 发送端：启用（提供数据给系统A）
- 接收端：启用，远程URL指向系统A

这样两个系统会互相同步数据，实现双向备份。

## 数据端点编码表

| 编码 | 名称 | API路径 | 分类 | 间隔 |
|------|------|---------|------|------|
| PT001 | 最新价格追踪 | /api/coin-price-tracker/latest | 价格追踪 | 60s |
| PT002 | 价格追踪历史 | /api/coin-price-tracker/history | 价格追踪 | 60s |
| PS001 | 最新价格速度 | /api/price-speed/latest | 价格速度 | 60s |
| PB001 | 价格基准数据 | /api/price-comparison/list | 价格基准 | 600s |
| SAR001 | SAR当前周期 | /api/sar/current-cycle/{coin} | SAR数据 | 60s |
| SAR002 | SAR偏离统计 | /api/sar-bias/stats | SAR偏离 | 3600s |
| SAR003 | SAR斜率数据 | /api/sar-slope/current-cycle/{coin} | SAR斜率 | 60s |
| AN001 | 锚定利润最新 | /api/anchor-profit/latest | 锚定利润 | 300s |
| AN002 | 锚定利润历史 | /api/anchor-profit/history | 锚定利润 | 300s |
| AN003 | 锚定系统状态 | /api/anchor-system/status | 锚定系统 | 60s |
| AN004 | 锚定系统持仓 | /api/anchor-system/current-positions | 锚定系统 | 60s |
| OKX001 | OKX市场行情 | /api/okx-trading/market-tickers | OKX交易 | 5s |
| OKX002 | OKX持仓列表 | /api/okx-trading/positions | OKX持仓 | 10s |
| OKX003 | OKX挂单列表 | /api/okx-trading/pending-orders | OKX订单 | 10s |
| OKX004 | OKX交易日志 | /api/okx-trading/logs | OKX交易 | 60s |
| OKX005 | OKX账户限额 | /api/okx-trading/account-limit | OKX账户 | 300s |
| ES001 | 逃顶信号最新 | /api/escape-signal/latest | 逃顶信号 | 60s |
| ES002 | 逃顶信号统计 | /api/escape-signal/stats | 逃顶统计 | 300s |
| EX001 | 极值追踪最新 | /api/extreme-value/latest | 极值追踪 | 60s |
| PI001 | 恐慌指数最新 | /api/panic/latest | 恐慌指数 | 3600s |
| FG001 | 恐惧贪婪指数 | /api/fear-greed/latest | 恐惧贪婪 | 3600s |
| CC001 | 币种变化最新 | /api/coin-change-tracker/latest | 币种变化 | 60s |
| CC002 | 币种变化基准 | /api/coin-change-tracker/baseline | 币种变化 | 600s |
| LQ001 | 1小时清算数据 | /api/liquidation/1h | 清算数据 | 3600s |
| V1V2001 | V1V2最新数据 | /api/v1v2/latest | V1V2数据 | 60s |
| SYS001 | 数据健康监控 | /api/data-health-monitor/status | 系统健康 | 300s |
| SYS002 | 采集器状态 | /api/collectors/status | 采集器状态 | 60s |
| SR001 | 支撑阻力数据 | /api/support-resistance/latest | 支撑阻力 | 3600s |
| CI001 | 加密指数数据 | /api/crypto-index/latest | 加密指数 | 3600s |
| ME001 | 重大事件监控 | /api/major-events/latest | 重大事件 | 300s |

## 安全建议

1. **启用认证**：在生产环境中务必配置认证令牌
2. **IP白名单**：限制只有特定IP可以访问
3. **HTTPS**：使用HTTPS协议传输数据
4. **定期更新令牌**：定期更换认证令牌
5. **监控异常**：关注失败日志和异常请求

## 监控指标

### 发送端指标
- `total_requests`：总请求数
- `successful_requests`：成功请求数
- `failed_requests`：失败请求数
- `total_bytes_sent`：总发送字节数
- `last_request_time`：最后请求时间
- `endpoint_stats`：每个端点的详细统计

### 接收端指标
- `total_syncs`：总同步次数
- `successful_syncs`：成功同步数
- `failed_syncs`：失败同步数
- `total_bytes_received`：总接收字节数
- `last_sync_time`：最后同步时间
- `endpoint_stats`：每个端点的同步统计

## 故障排查

### 问题：发送端无法访问

**可能原因**：
1. 发送端未启用
2. IP不在白名单
3. 认证令牌错误

**解决方法**：
1. 检查发送端状态：`GET /api/data-sync/sender/status`
2. 查看日志：`/home/user/webapp/logs/data_sender.log`
3. 验证配置：检查 `/home/user/webapp/data/data_sync_config.json`

### 问题：接收端同步失败

**可能原因**：
1. 远程URL无法访问
2. 网络问题
3. 数据格式错误

**解决方法**：
1. 测试远程连接：`curl http://remote-server:5000/api/data-sync/sender/catalog`
2. 查看接收端状态：`GET /api/data-sync/receiver/status`
3. 检查错误日志

## 文件位置

- 配置文件：`/home/user/webapp/data/data_sync_config.json`
- 发送端日志：`/home/user/webapp/logs/data_sender.log`
- 接收端日志：`/home/user/webapp/logs/data_receiver.log`
- 发送端统计：`/home/user/webapp/data/data_sender_stats.json`
- 接收端统计：`/home/user/webapp/data/data_receiver_stats.json`
- 同步数据：`/home/user/webapp/data/synced_data/`

## 开发说明

### 添加新的数据端点

1. 在 `data_sync_registry.py` 中注册新端点：

```python
self.register(DataEndpoint(
    code="NEW001",
    category=DataCategory.YOUR_CATEGORY,
    name="新端点名称",
    api_path="/api/your-endpoint",
    method="GET",
    description="端点描述",
    data_file="data/your_data/your_file.jsonl",
    params=None,
    interval_seconds=60
))
```

2. 重启Flask应用：`pm2 restart flask-app`

3. 在管理界面的"数据目录"中确认新端点已注册

### 扩展功能

- **增量同步**：基于时间戳的增量同步
- **数据压缩**：传输大文件时启用gzip压缩
- **断点续传**：大文件传输中断后继续
- **多线程同步**：并发同步多个端点

## 总结

数据沟通备份系统提供了完整的双向数据同步解决方案，支持：

✅ 30个数据端点，12个分类  
✅ 发送端和接收端独立配置  
✅ 安全认证和IP限制  
✅ 实时监控和统计  
✅ Web管理界面  
✅ 自动同步和手动同步  
✅ JSONL数据格式支持  

适用于系统间数据备份、跨机房数据同步、灾难恢复等场景。
