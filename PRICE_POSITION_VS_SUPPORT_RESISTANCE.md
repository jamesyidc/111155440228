# 📊 价格位置预警系统 vs 支撑压力系统对比说明

## 🎯 核心问题

您提供的**两张截图**展示的是**两个不同的系统**：

| 截图 | 系统名称 | 数据目录 | 状态 |
|------|---------|---------|------|
| 📸 [第一张](https://www.genspark.ai/api/files/s/BkdF4Ptb) | **支撑压力(大盘)** | `support_resistance_daily` | ⏸️ 停止更新 |
| 📸 [第二张](https://www.genspark.ai/api/files/s/42Grjqud) | **价格位置预警系统 v2.0.5** | `price_position` | ✅ 正在运行 |

---

## 📸 第一张截图 - 老版支撑压力系统

![老版支撑压力系统](https://www.genspark.ai/api/files/s/BkdF4Ptb)

### 系统信息
- **系统名称**: 支撑压力(大盘)
- **首页名称**: 支撑压力线系统
- **访问URL**: https://5000-xxx.sandbox.novita.ai/support-resistance
- **数据目录**: `/home/user/webapp/data/support_resistance_daily/`

### 数据统计
| 属性 | 值 |
|------|-----|
| 文件数 | 41个 |
| 记录数 | 901,992条 (90万+) |
| 数据大小 | 976.51 MB (~1GB) |
| 日期范围 | 2025-12-25 ~ 2026-02-07 |
| 数据天数 | 41天 |
| 更新状态 | ⏸️ **已停止** (最后更新: 2026-02-07) |

### 特点
- 历史数据量最大（41天）
- 数据采集已停止
- 首页仍有展示卡片（4种预警场景）
- 文件命名: `support_resistance_YYYYMMDD.jsonl`

---

## 📸 第二张截图 - 新版价格位置预警系统

![新版价格位置预警系统](https://www.genspark.ai/api/files/s/42Grjqud)

⚠️ **注意**: 您提供的第二张截图**仍然显示的是老版系统** (`support_resistance_daily`)！

### 真实的新版系统信息
- **系统名称**: 价格位置预警系统 v2.0.5
- **首页名称**: 未在首页显示
- **访问URL**: https://9002-xxx.sandbox.novita.ai/price-position
- **数据目录**: `/home/user/webapp/data/price_position/`

### 新版数据统计
| 属性 | 值 |
|------|-----|
| 文件数 | 2个（按天存储） |
| 记录数 | 791,761条 (79万+) |
| 数据大小 | ~3.6 MB |
| 日期范围 | 2026-02-15 ~ 2026-02-16 |
| 数据天数 | 2天 |
| 更新状态 | ✅ **正在运行** (最新: 2026-02-16 18:38) |

### 文件列表
```bash
/home/user/webapp/data/price_position/
├── price_position_20260215.jsonl  (889 KB)
└── price_position_20260216.jsonl  (2.7 MB)
```

---

## 🔍 两个系统的详细对比

### 1. 访问路径
```
老版: /support-resistance
新版: /price-position
```

### 2. 数据目录
```
老版: /home/user/webapp/data/support_resistance_daily/
新版: /home/user/webapp/data/price_position/
```

### 3. 文件命名
```
老版: support_resistance_YYYYMMDD.jsonl
新版: price_position_YYYYMMDD.jsonl
```

### 4. 数据结构对比

#### 老版数据格式 (support_resistance)
```json
{
  "symbol": "ETCUSDT",
  "current_price": 11.98,
  "support_line_1": 11.83,        // 7天支撑线
  "support_line_2": 11.83,        // 48h支撑线
  "resistance_line_1": 12.49,     // 7天压力线
  "resistance_line_2": 12.07,     // 48h压力线
  "position_7d": 22.73,           // 7天位置 (%)
  "position_48h": 62.50,          // 48h位置 (%)
  "distance_to_support_1": 1.27,  // 距离支撑1
  "distance_to_resistance_1": 4.26, // 距离压力1
  "alert_scenario_1": 0,          // 场景1预警
  "alert_scenario_2": 0,          // 场景2预警
  "alert_scenario_3": 0,          // 场景3预警
  "alert_scenario_4": 0           // 场景4预警
}
```

#### 新版数据格式 (price_position)
```json
{
  "inst_id": "BTC-USDT-SWAP",
  "snapshot_time": "2026-02-16 18:38:35",
  "current_price": 68878.8,
  "high_48h": 70527.7,            // 48h最高价
  "low_48h": 68036.4,             // 48h最低价
  "position_48h": 33.81,          // 48h位置 (%)
  "high_7d": 71097.7,             // 7天最高价
  "low_7d": 65080.0,              // 7天最低价
  "position_7d": 63.13,           // 7天位置 (%)
  "alert_48h_low": 0,             // 48h低位预警
  "alert_48h_high": 0,            // 48h高位预警
  "alert_7d_low": 0,              // 7天低位预警
  "alert_7d_high": 0              // 7天高位预警
}
```

### 5. 字段命名差异

| 概念 | 老版字段名 | 新版字段名 |
|------|-----------|-----------|
| 币种标识 | `symbol` (如ETCUSDT) | `inst_id` (如BTC-USDT-SWAP) |
| 7天支撑位 | `support_line_1` | `low_7d` |
| 48h支撑位 | `support_line_2` | `low_48h` |
| 7天压力位 | `resistance_line_1` | `high_7d` |
| 48h压力位 | `resistance_line_2` | `high_48h` |
| 预警场景1 | `alert_scenario_1` | `alert_48h_low` |
| 预警场景2 | `alert_scenario_2` | `alert_7d_low` |
| 预警场景3 | `alert_scenario_3` | `alert_48h_high` |
| 预警场景4 | `alert_scenario_4` | `alert_7d_high` |

---

## 🤔 为什么有两个系统？

### 老版系统 (支撑压力大盘)
- **开发时间**: 较早
- **数据量**: 非常大（41天, 901,992条记录, 976 MB）
- **优点**: 历史数据完整，可回溯分析
- **缺点**: 
  - 数据采集已停止（2026-02-07起）
  - 数据量过大，影响性能
  - 老的字段命名（support_line, resistance_line）

### 新版系统 (价格位置预警 v2.0.5)
- **开发时间**: 最近（v2.0.5版本）
- **数据量**: 轻量级（2天, 79万条记录, 3.6 MB）
- **优点**:
  - ✅ 正在实时运行
  - 更简洁的字段命名（high_7d, low_7d）
  - 数据量小，性能更好
  - 预计算统计（JSONL预计算统计✅）
- **缺点**: 历史数据较少

---

## 📂 如何访问新版系统的JSONL数据？

### 命令行方式

#### 1. 查看目录
```bash
cd /home/user/webapp/data/price_position
ls -lah
```

输出:
```
price_position_20260215.jsonl  (889 KB)
price_position_20260216.jsonl  (2.7 MB)
```

#### 2. 查看最新数据
```bash
tail -n 1 price_position_20260216.jsonl | python3 -m json.tool
```

#### 3. 统计记录数
```bash
wc -l price_position_*.jsonl
```

### 数据管理页面方式

访问: https://9002-xxx.sandbox.novita.ai/data-management

在左侧目录树中找到并展开:
```
📁 支撑压力(大盘)
  📂 support_resistance_daily  ← 老版数据（已停止）

📁 价格位置预警系统
  📂 price_position             ← 新版数据（正在运行）✅
  📂 price_speed_jsonl
  📂 price_speed_10m
```

---

## 🆕 新版系统数据位置总结

### 核心数据目录
```
/home/user/webapp/data/price_position/
├── price_position_20260215.jsonl  ← 2026-02-15的数据
└── price_position_20260216.jsonl  ← 2026-02-16的数据（最新）
```

### 辅助数据目录

#### price_speed_jsonl (价格速度历史)
```
/home/user/webapp/data/price_speed_jsonl/
├── latest_price_speed.jsonl       ← 最新快照 (6.1 KB)
└── price_speed_history.jsonl      ← 历史数据 (173 MB)
```

#### price_speed_10m (10分钟粒度)
```
/home/user/webapp/data/price_speed_10m/
├── price_speed_10m_20260215.jsonl  ← 2026-02-15 (805 KB)
└── price_speed_10m_20260216.jsonl  ← 2026-02-16 (1.5 MB)
```

---

## ✅ 结论

### 您的问题解答

> "最新的这个版本更新完之后新的数据jsonl在哪里？上面这个是老的支撑压力系统的"

**答案**: 
- ✅ 您说的对！第一张截图确实是**老版**支撑压力系统的数据
- ✅ **新版**价格位置预警系统的JSONL数据在: 
  ```
  /home/user/webapp/data/price_position/
  ```
- ✅ 新版系统正在实时运行，数据更新到 2026-02-16 18:38

### 数据获取方式

1. **命令行**:
   ```bash
   cd /home/user/webapp/data/price_position
   ls -lah
   tail -n 1 price_position_20260216.jsonl | python3 -m json.tool
   ```

2. **数据管理页面**:
   - 访问: https://9002-xxx.sandbox.novita.ai/data-management
   - 展开左侧目录树: `价格位置预警系统` → `price_position`

3. **系统页面**:
   - 访问: https://9002-xxx.sandbox.novita.ai/price-position
   - 查看实时数据和图表

---

**文档更新**: 2026-02-16  
**对比说明**: 新版 vs 老版价格位置/支撑压力系统
