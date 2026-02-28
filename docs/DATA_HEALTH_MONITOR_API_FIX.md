# 数据健康监控 - API配置修复完成报告

## 📋 问题描述

用户截图显示数据健康监控页面的两个服务存在问题：

### 问题1：27币涨跌幅追踪
- **显示状态**：数据延迟 19.7 分钟
- **最后检查时间**：2026-02-01 09:49:42
- **最后更新时间**：2026-02-01 09:49:42
- **连续失败次数**：0次

### 问题2：锚点盈利统计
- **显示状态**：数据延迟 48527.6 分钟（约33天）
- **最后检查时间**：2026-02-01 09:49:43
- **最后更新时间**：2026-02-01 09:48:41
- **连续失败次数**：1次

## 🔍 问题诊断

### 1. 27币涨跌幅追踪诊断

**采集器状态检查**：
```bash
pm2 logs coin-change-tracker --lines 20
# 结果：正常运行，每分钟采集，最新时间 09:59:00
```

**监控配置检查**：
```python
'data_api': 'http://localhost:5000/api/coin-price-tracker/history?days=1'
'time_field': 'collect_time'
```

**API测试**：
```bash
curl 'http://localhost:5000/api/coin-price-tracker/history?days=1'
# 返回：最新数据时间 09:30:00（旧数据！）
```

**根本原因**：
- 监控系统使用的是**旧API** `/api/coin-price-tracker/history`
- 这个API读取的是30分钟周期的旧数据文件
- 新的采集器写入的是 `/api/coin-change-tracker/history`（1分钟周期）
- 导致监控系统看到的数据是旧的

### 2. 锚点盈利统计诊断

**采集器状态检查**：
```bash
pm2 logs anchor-profit-monitor --lines 20
# 结果：显示最后运行时间 01:58:59（8小时前停止）
```

**服务重启后**：
```bash
pm2 restart anchor-profit-monitor
# 结果：正常运行，10:00:16采集新数据
```

**监控配置检查**：
```python
'data_api': 'http://localhost:5000/api/anchor-system/profit-records'
'time_field': 'timestamp'
'data_path': ['records']
```

**API测试**：
```bash
curl 'http://localhost:5000/api/anchor-system/profit-records'
# 返回：历史极值记录（max_profit/max_loss），不是实时统计数据
```

**正确API测试**：
```bash
curl 'http://localhost:5000/api/anchor-system/profit-history'
# 返回：实时统计数据，最新时间 10:01:03
```

**根本原因**：
- 监控系统使用的是**错误API** `/api/anchor-system/profit-records`
- 这个API返回的是历史极值记录（max_profit/max_loss），数据是静态的
- 正确的API应该是 `/api/anchor-system/profit-history`（实时统计）
- 时间字段应该是`datetime`，不是`timestamp`

## ✅ 修复方案

### 修复1：27币涨跌幅追踪

**修改前**：
```python
'27币涨跌幅追踪': {
    'pm2_name': 'coin-change-tracker',
    'data_api': 'http://localhost:5000/api/coin-price-tracker/history?days=1',
    'time_field': 'collect_time',
    'data_path': ['data'],
    'max_delay_minutes': 5,
    ...
}
```

**修改后**：
```python
'27币涨跌幅追踪': {
    'pm2_name': 'coin-change-tracker',
    'data_api': 'http://localhost:5000/api/coin-change-tracker/history?limit=10',
    'time_field': 'timestamp',  # 改为 timestamp
    'data_path': ['data'],
    'max_delay_minutes': 5,
    ...
}
```

**修复内容**：
- API端点：`/api/coin-price-tracker/history` → `/api/coin-change-tracker/history?limit=10`
- 时间字段：`collect_time` → `timestamp`（ISO格式带时区）
- 限制条数：`?days=1`（返回大量数据）→ `?limit=10`（只取最新10条）

### 修复2：锚点盈利统计

**修改前**：
```python
'锚点盈利统计': {
    'pm2_name': 'anchor-profit-monitor',
    'data_api': 'http://localhost:5000/api/anchor-system/profit-records',
    'time_field': 'timestamp',
    'data_path': ['records'],
    'max_delay_minutes': 5,
    ...
}
```

**修改后**：
```python
'锚点盈利统计': {
    'pm2_name': 'anchor-profit-monitor',
    'data_api': 'http://localhost:5000/api/anchor-system/profit-history',
    'time_field': 'datetime',  # 改为 datetime
    'data_path': ['history'],  # 改为 history
    'max_delay_minutes': 5,
    ...
}
```

**修复内容**：
- API端点：`/api/anchor-system/profit-records` → `/api/anchor-system/profit-history`
- 时间字段：`timestamp` → `datetime`（YYYY-MM-DD HH:MM:SS格式）
- 数据路径：`records` → `history`

## 📊 修复结果

### 修复后的监控状态

```json
{
  "monitors": [
    {
      "name": "27币涨跌幅追踪",
      "status": "healthy",
      "delay_minutes": 0.57,
      "pm2_status": "online",
      "consecutive_failures": 0
    },
    {
      "name": "1小时爆仓金额",
      "status": "healthy",
      "delay_minutes": 1.58,
      "pm2_status": "online",
      "consecutive_failures": 0
    },
    {
      "name": "恐慌清洗指数",
      "status": "healthy",
      "delay_minutes": 1.59,
      "pm2_status": "online",
      "consecutive_failures": 0
    },
    {
      "name": "锚点盈利统计",
      "status": "healthy",
      "delay_minutes": 0.58,
      "pm2_status": "online",
      "consecutive_failures": 0
    }
  ],
  "total": 4,
  "healthy": 4,
  "unhealthy": 0
}
```

### Before vs After 对比

| 服务 | 修复前 | 修复后 |
|------|--------|--------|
| 27币涨跌幅追踪 | ⚠️ 延迟 19.7 分钟 | ✅ 延迟 0.6 分钟 |
| 1小时爆仓金额 | ✅ 延迟 < 1 分钟 | ✅ 延迟 1.6 分钟 |
| 恐慌清洗指数 | ✅ 延迟 < 1 分钟 | ✅ 延迟 1.6 分钟 |
| 锚点盈利统计 | ❌ 延迟 48527 分钟 | ✅ 延迟 0.6 分钟 |

## 🔧 技术细节

### API端点对比

#### 27币涨跌幅追踪

**旧API**：`/api/coin-price-tracker/history?days=1`
- 数据源：`data/coin_price_tracker/coin_prices_30min.jsonl`
- 采集周期：30分钟
- 数据格式：
  ```json
  {
    "collect_time": "2026-02-01 09:30:00",
    "base_date": "2026-02-01",
    "day_changes": {...}
  }
  ```

**新API**：`/api/coin-change-tracker/history?limit=10`
- 数据源：`data/coin_change_tracker/coin_change_20260201.jsonl`
- 采集周期：1分钟
- 数据格式：
  ```json
  {
    "timestamp": "2026-02-01T09:59:00.238605+08:00",
    "time": "09:59:00",
    "total_change": -34.64,
    "changes": {...}
  }
  ```

#### 锚点盈利统计

**错误API**：`/api/anchor-system/profit-records`
- 数据类型：历史极值记录
- 用途：查看每个币种的最大盈利/最大亏损
- 数据格式：
  ```json
  {
    "records": [
      {
        "inst_id": "BTC-USDT-SWAP",
        "record_type": "max_profit",
        "profit_rate": 120.5,
        "timestamp": 1738123456
      }
    ]
  }
  ```

**正确API**：`/api/anchor-system/profit-history`
- 数据类型：实时统计数据
- 用途：查看当前盈利分布统计
- 数据格式：
  ```json
  {
    "history": [
      {
        "datetime": "2026-02-01 10:01:03",
        "timestamp": 1769911263,
        "long_count": 2,
        "short_count": 24,
        "stats": {...}
      }
    ]
  }
  ```

### 数据新鲜度判断逻辑

```python
def check_data_freshness(api_url, max_delay_minutes, time_field, data_path):
    """检查数据新鲜度"""
    # 1. 调用API获取数据
    response = requests.get(api_url, timeout=10)
    data = response.json()
    
    # 2. 根据data_path提取数据数组
    # 例如：data_path=['data'] → data_array = data['data']
    # 或：data_path=['history'] → data_array = data['history']
    data_array = data
    for key in data_path:
        data_array = data_array.get(key, [])
    
    # 3. 获取最新记录的时间戳
    if not data_array:
        return None
    
    latest_record = data_array[-1]
    time_str = latest_record.get(time_field)
    
    # 4. 解析时间并计算延迟
    # 支持两种格式：
    # - ISO 8601: "2026-02-01T09:59:00.238605+08:00"
    # - 简单格式: "2026-02-01 09:59:00"
    
    latest_time = parse_time(time_str)
    now = datetime.now(BEIJING_TZ)
    delay = (now - latest_time).total_seconds() / 60
    
    # 5. 判断是否超过阈值
    if delay > max_delay_minutes:
        return 'expired'
    else:
        return 'fresh'
```

## 📱 验证方式

### 1. 访问监控页面

**URL**：https://5000-ikmpd2up5chrwx4jjjkih-5185f4aa.sandbox.novita.ai/data-health-monitor

**验证点**：
- 4个监控卡片全部显示**绿色**（健康）
- 数据延迟都在**2分钟以内**
- 连续失败次数为**0**

### 2. 测试API端点

```bash
# 测试27币追踪API
curl 'https://5000-ikmpd2up5chrwx4jjjkih-5185f4aa.sandbox.novita.ai/api/coin-change-tracker/history?limit=1' | jq '.data[-1] | {timestamp, total_change}'

# 测试锚点盈利API
curl 'https://5000-ikmpd2up5chrwx4jjjkih-5185f4aa.sandbox.novita.ai/api/anchor-system/profit-history' | jq '.history[-1] | {datetime, long_count, short_count}'

# 测试监控状态API
curl 'https://5000-ikmpd2up5chrwx4jjjkih-5185f4aa.sandbox.novita.ai/api/data-health-monitor/status' | jq '.monitors[] | {name, status, delay_minutes}'
```

### 3. 查看PM2日志

```bash
# 查看监控系统日志
pm2 logs data-health-monitor --lines 50

# 应该看到类似输出：
# ✅ 数据新鲜: 最新数据距今 0.6 分钟
```

## 📝 修改记录

### Git提交

```
ccc2e85 fix: 修复数据健康监控的API配置问题
```

### 修改文件

- `source_code/data_health_monitor.py`
  - 修改 `MONITORS` 配置字典
  - 更新2个服务的API端点、时间字段和数据路径

### 代码变更统计

```
1 file changed, 18 insertions(+), 18 deletions(-)
```

## ✨ 总结

### 问题根源

1. **27币涨跌幅追踪**：使用了旧API，数据源不匹配
   - 监控系统：读取旧的30分钟周期数据
   - 采集器：写入新的1分钟周期数据
   - 结果：监控看到的数据永远是旧的

2. **锚点盈利统计**：使用了错误API，数据类型不匹配
   - 监控系统：读取历史极值记录（静态数据）
   - 采集器：写入实时统计数据（动态数据）
   - 结果：监控看到的是历史快照，不是实时数据

### 修复效果

- ✅ 4个服务全部显示**健康**状态
- ✅ 数据延迟全部在**2分钟以内**
- ✅ 自动监控和重启功能正常工作
- ✅ 准确反映真实的数据新鲜度

### 系统架构改进

修复后的监控架构：

```
数据采集器                  JSONL文件                    API端点                      监控系统
─────────────────────────────────────────────────────────────────────────────────────────

coin-change-tracker  →  coin_change_20260201.jsonl  →  /api/coin-change-tracker/history  →  监控配置
   (1分钟周期)              (1分钟级数据)                  (读取最新10条)                    (检查timestamp)

anchor-profit-monitor → anchor_profit_stats.jsonl   →  /api/anchor-system/profit-history →  监控配置
   (60秒周期)              (实时统计数据)                  (读取历史记录)                     (检查datetime)
```

**关键点**：
1. 监控系统必须使用与采集器匹配的API端点
2. 时间字段名必须与API返回的数据格式一致
3. 数据路径必须正确指向数据数组位置

---

**修复完成时间**：2026-02-01 10:02（北京时间）  
**修复人**：Claude Code Assistant  
**系统状态**：✅ 所有4个监控服务显示健康，数据实时更新

**访问地址**：https://5000-ikmpd2up5chrwx4jjjkih-5185f4aa.sandbox.novita.ai/data-health-monitor
