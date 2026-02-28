# Panic Paged V2 - 完整系统架构文档

## 📌 系统概述

**Panic Paged V2** 是一个完整的后端驱动的恐慌指数监控系统，具有独立的数据采集器、API服务和翻页功能。

### 核心特性

- ✅ **独立采集器**: 24h和1h数据分别采集，PM2管理
- ✅ **独立存储**: JSONL文件按日按类型分开保存
- ✅ **完整API**: RESTful API提供数据查询
- ✅ **翻页查看**: 前端可查看任意历史日期
- ✅ **深色主题**: 舒适的视觉体验

---

## 🏗️ 系统架构

```
panic_paged_v2/
├── data/                          # 数据目录
│   ├── panic_24h_20260210.jsonl   # 24小时数据（按日）
│   ├── panic_24h_20260211.jsonl
│   ├── panic_1h_20260210.jsonl    # 1小时数据（按日）
│   └── panic_1h_20260211.jsonl
├── collector_24h.py               # 24小时数据采集器
├── collector_1h.py                # 1小时数据采集器
├── data_manager.py                # 数据管理器
├── api_routes.py                  # API路由定义
└── ecosystem.config.json          # PM2配置文件
```

---

## 📊 数据格式规范

### 24小时数据 (panic_24h_YYYYMMDD.jsonl)

**文件名格式**: `panic_24h_20260211.jsonl`

**每行记录格式**:
```json
{
  "timestamp": 1770792843198,
  "beijing_time": "2026-02-11 14:54:03",
  "liquidation_24h": 16642.09,
  "liquidation_count_24h": 7.08,
  "open_interest": 56.27,
  "panic_index": 0.1258,
  "panic_level": "中等恐慌"
}
```

**字段说明**:

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| timestamp | int | 毫秒 | Unix时间戳 |
| beijing_time | string | - | 北京时间 YYYY-MM-DD HH:mm:ss |
| liquidation_24h | float | 万美元 | 24小时爆仓金额 |
| liquidation_count_24h | float | 万人 | 24小时爆仓人数 |
| open_interest | float | 亿美元 | 全网持仓量 |
| panic_index | float | - | 恐慌指数 (0-1) |
| panic_level | string | - | 恐慌等级（低/中等/高恐慌） |

---

### 1小时数据 (panic_1h_YYYYMMDD.jsonl)

**文件名格式**: `panic_1h_20260211.jsonl`

**每行记录格式**:
```json
{
  "timestamp": 1770792843198,
  "beijing_time": "2026-02-11 14:54:03",
  "liquidation_1h": 3996.87
}
```

**字段说明**:

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| timestamp | int | 毫秒 | Unix时间戳 |
| beijing_time | string | - | 北京时间 YYYY-MM-DD HH:mm:ss |
| liquidation_1h | float | 万美元 | 1小时爆仓金额 |

---

## 🔄 数据采集器

### collector_24h.py

**功能**: 采集24小时爆仓数据

**采集频率**: 每60秒

**数据源**: `https://history.btc126.com/baocang/`

**保存位置**: `data/panic_24h_YYYYMMDD.jsonl`

**启动命令**:
```bash
cd /home/user/webapp/panic_paged_v2
python3 collector_24h.py
```

**PM2启动**:
```bash
pm2 start collector_24h.py --name panic-paged-v2-collector-24h --interpreter python3
```

---

### collector_1h.py

**功能**: 采集1小时爆仓数据

**采集频率**: 每60秒

**数据源**: `https://history.btc126.com/baocang/`

**保存位置**: `data/panic_1h_YYYYMMDD.jsonl`

**启动命令**:
```bash
cd /home/user/webapp/panic_paged_v2
python3 collector_1h.py
```

**PM2启动**:
```bash
pm2 start collector_1h.py --name panic-paged-v2-collector-1h --interpreter python3
```

---

### PM2统一管理

**使用ecosystem配置启动**:
```bash
cd /home/user/webapp/panic_paged_v2
pm2 start ecosystem.config.json
pm2 save
```

**查看运行状态**:
```bash
pm2 status
pm2 logs panic-paged-v2-collector-24h
pm2 logs panic-paged-v2-collector-1h
```

**停止采集器**:
```bash
pm2 stop panic-paged-v2-collector-24h
pm2 stop panic-paged-v2-collector-1h
```

**重启采集器**:
```bash
pm2 restart panic-paged-v2-collector-24h
pm2 restart panic-paged-v2-collector-1h
```

---

## 🌐 API接口文档

### 基础URL

`http://localhost:5000/api/panic-paged/`

### 接口列表

#### 1. 获取最新24小时数据

**接口**: `GET /api/panic-paged/24h/latest`

**返回**:
```json
{
  "success": true,
  "data": {
    "timestamp": 1770792843198,
    "beijing_time": "2026-02-11 14:54:03",
    "liquidation_24h": 16642.09,
    "liquidation_count_24h": 7.08,
    "open_interest": 56.27,
    "panic_index": 0.1258,
    "panic_level": "中等恐慌"
  }
}
```

---

#### 2. 获取最新1小时数据

**接口**: `GET /api/panic-paged/1h/latest`

**返回**:
```json
{
  "success": true,
  "data": {
    "timestamp": 1770792843198,
    "beijing_time": "2026-02-11 14:54:03",
    "liquidation_1h": 3996.87
  }
}
```

---

#### 3. 获取指定日期的24小时数据

**接口**: `GET /api/panic-paged/24h/by-date?date=2026-02-11`

**参数**:
- `date`: 日期字符串，格式 `YYYY-MM-DD`

**返回**:
```json
{
  "success": true,
  "date": "2026-02-11",
  "count": 42,
  "data": [
    {
      "timestamp": 1770792843198,
      "beijing_time": "2026-02-11 14:54:03",
      "liquidation_24h": 16642.09,
      "liquidation_count_24h": 7.08,
      "open_interest": 56.27,
      "panic_index": 0.1258,
      "panic_level": "中等恐慌"
    },
    ...
  ]
}
```

---

#### 4. 获取指定日期的1小时数据

**接口**: `GET /api/panic-paged/1h/by-date?date=2026-02-11`

**参数**:
- `date`: 日期字符串，格式 `YYYY-MM-DD`

**返回**:
```json
{
  "success": true,
  "date": "2026-02-11",
  "count": 42,
  "data": [
    {
      "timestamp": 1770792843198,
      "beijing_time": "2026-02-11 14:54:03",
      "liquidation_1h": 3996.87
    },
    ...
  ]
}
```

---

#### 5. 获取可用日期列表

**接口**: `GET /api/panic-paged/available-dates`

**返回**:
```json
{
  "success": true,
  "dates_24h": ["2026-02-01", "2026-02-02", "2026-02-11"],
  "dates_1h": ["2026-02-01", "2026-02-02", "2026-02-11"]
}
```

---

#### 6. 获取日期范围的24小时数据

**接口**: `GET /api/panic-paged/24h/date-range?start_date=2026-02-10&end_date=2026-02-11`

**参数**:
- `start_date`: 开始日期，格式 `YYYY-MM-DD`
- `end_date`: 结束日期，格式 `YYYY-MM-DD`

**返回**:
```json
{
  "success": true,
  "start_date": "2026-02-10",
  "end_date": "2026-02-11",
  "data": {
    "2026-02-10": [{...}, {...}],
    "2026-02-11": [{...}, {...}]
  }
}
```

---

#### 7. 获取日期范围的1小时数据

**接口**: `GET /api/panic-paged/1h/date-range?start_date=2026-02-10&end_date=2026-02-11`

**参数**:
- `start_date`: 开始日期
- `end_date`: 结束日期

**返回**: 同上

---

## 🚀 部署步骤

### 1. 创建目录结构

```bash
cd /home/user/webapp
mkdir -p panic_paged_v2/data
mkdir -p logs
```

### 2. 复制文件

确保以下文件已创建：
- `collector_24h.py`
- `collector_1h.py`
- `data_manager.py`
- `api_routes.py`
- `ecosystem.config.json`

### 3. 集成到Flask应用

编辑 `/home/user/webapp/code/python/app.py`:

```python
# 在文件顶部添加
import sys
sys.path.insert(0, '/home/user/webapp/panic_paged_v2')

# 在创建app后添加
from api_routes import register_panic_paged_routes
register_panic_paged_routes(app)
```

### 4. 启动采集器

```bash
cd /home/user/webapp/panic_paged_v2
pm2 start ecosystem.config.json
pm2 save
```

### 5. 重启Flask应用

```bash
pm2 restart flask-app
```

### 6. 验证部署

```bash
# 检查采集器状态
pm2 status | grep panic-paged-v2

# 测试API
curl http://localhost:5000/api/panic-paged/available-dates | python3 -m json.tool
curl http://localhost:5000/api/panic-paged/24h/latest | python3 -m json.tool
curl http://localhost:5000/api/panic-paged/1h/latest | python3 -m json.tool

# 查看数据文件
ls -lh panic_paged_v2/data/
tail -1 panic_paged_v2/data/panic_24h_*.jsonl | python3 -m json.tool
tail -1 panic_paged_v2/data/panic_1h_*.jsonl | python3 -m json.tool
```

---

## 📈 数据示例

### 查看今天的24小时数据

```bash
cat panic_paged_v2/data/panic_24h_20260211.jsonl | head -3
```

输出:
```json
{"timestamp": 1770788797429, "beijing_time": "2026-02-11 13:46:37", "liquidation_24h": 14440.03, "liquidation_count_24h": 6.64, "open_interest": 56.78, "panic_index": 0.1169, "panic_level": "中等恐慌"}
{"timestamp": 1770788857429, "beijing_time": "2026-02-11 13:47:37", "liquidation_24h": 14450.12, "liquidation_count_24h": 6.65, "open_interest": 56.79, "panic_index": 0.1171, "panic_level": "中等恐慌"}
{"timestamp": 1770788917429, "beijing_time": "2026-02-11 13:48:37", "liquidation_24h": 14460.28, "liquidation_count_24h": 6.66, "open_interest": 56.80, "panic_index": 0.1172, "panic_level": "中等恐慌"}
```

### 查看今天的1小时数据

```bash
cat panic_paged_v2/data/panic_1h_20260211.jsonl | head -3
```

输出:
```json
{"timestamp": 1770788797429, "beijing_time": "2026-02-11 13:46:37", "liquidation_1h": 3734.63}
{"timestamp": 1770788857429, "beijing_time": "2026-02-11 13:47:37", "liquidation_1h": 3735.12}
{"timestamp": 1770788917429, "beijing_time": "2026-02-11 13:48:37", "liquidation_1h": 3736.45}
```

---

## 🔧 维护命令

### 查看日志

```bash
# 24小时采集器日志
pm2 logs panic-paged-v2-collector-24h --lines 50

# 1小时采集器日志
pm2 logs panic-paged-v2-collector-1h --lines 50

# 实时跟踪
pm2 logs panic-paged-v2-collector-24h --lines 0
```

### 数据清理

```bash
# 删除30天前的数据
find panic_paged_v2/data/ -name "panic_*.jsonl" -mtime +30 -delete

# 查看数据占用
du -sh panic_paged_v2/data/
```

### 性能监控

```bash
pm2 monit
```

---

## 🎨 前端集成

前端页面通过API获取数据，实现翻页功能。

### 示例代码

```javascript
// 获取指定日期的24小时数据
async function load24hData(date) {
    const response = await fetch(`/api/panic-paged/24h/by-date?date=${date}`);
    const result = await response.json();
    if (result.success) {
        return result.data;
    }
    return [];
}

// 获取指定日期的1小时数据
async function load1hData(date) {
    const response = await fetch(`/api/panic-paged/1h/by-date?date=${date}`);
    const result = await response.json();
    if (result.success) {
        return result.data;
    }
    return [];
}

// 获取可用日期
async function getAvailableDates() {
    const response = await fetch('/api/panic-paged/available-dates');
    const result = await response.json();
    if (result.success) {
        return {
            dates24h: result.dates_24h,
            dates1h: result.dates_1h
        };
    }
    return { dates24h: [], dates1h: [] };
}
```

---

## ⚠️ 注意事项

### 数据采集

1. **网络依赖**: 采集器依赖 `https://history.btc126.com/baocang/` 可用性
2. **频率限制**: 每60秒采集一次，避免请求过于频繁
3. **错误处理**: 采集失败会记录日志，但不会停止程序

### 数据存储

1. **文件大小**: 每天约产生 1440条记录（每分钟1条）
2. **磁盘空间**: 定期清理旧数据，避免占用过多空间
3. **并发写入**: 两个采集器独立运行，不会冲突

### API性能

1. **缓存**: 考虑添加缓存层（Redis）提升性能
2. **分页**: 对于大量数据，考虑添加分页参数
3. **压缩**: 可以考虑gzip压缩API响应

---

## 📚 相关文档

| 文档 | 路径 | 说明 |
|------|------|------|
| 系统架构 | 本文档 | 完整架构说明 |
| API文档 | 见上方 | 接口定义 |
| 数据格式 | 见上方 | JSONL格式规范 |

---

## 🎉 总结

**Panic Paged V2** 是一个完整的后端驱动系统，包含：

- ✅ **独立采集器**: 24h和1h分开采集，PM2管理
- ✅ **独立存储**: JSONL按日按类型保存
- ✅ **完整API**: 7个RESTful接口
- ✅ **易于维护**: 清晰的目录结构和文档
- ✅ **生产就绪**: PM2守护进程，日志记录完善

**立即部署**: 按照上述步骤，5分钟内可完成部署！

---

**文档版本**: v1.0  
**更新日期**: 2026-02-11  
**作者**: AI Assistant
