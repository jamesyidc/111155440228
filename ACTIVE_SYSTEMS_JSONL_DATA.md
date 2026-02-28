# 运行中系统的JSONL数据位置

**更新日期**: 2026-02-16  
**用途**: 数据管理页面只显示当前正在运行的系统数据

---

## ✅ 当前运行的系统（7个）

根据最新扫描结果，以下系统正在运行并持续更新数据：

### 1. 📈 SAR趋势系统

**数据统计**: 50文件，537,505条记录，148.19 MB，16天数据（2026-02-01 ~ 2026-02-16）

**JSONL目录**:
- `sar_jsonl/` - 29个币种JSONL文件，每5分钟更新
- `sar_slope_jsonl/` - SAR斜率数据
- `sar_1min/` - 1分钟粒度SAR数据（按日存储）
- `sar_bias_stats/` - SAR乖离率统计（按日存储）

---

### 2. 💹 OKX全生态

**数据统计**: 51文件，14,249条记录，26.00 MB，17天数据（2026-01-21 ~ 2026-02-16）

**JSONL目录**:
- `okx_trading_jsonl/` - 日涨跌幅JSONL（每5分钟更新）
- `okx_trading_history/` - 交易历史（按日存储）
- `okx_trading_logs/` - 交易日志（按日存储）
- `okx_angle_analysis/` - 角度分析（按日存储）
- `okx_auto_strategy/` - 自动策略账户历史
- `okx_tpsl_settings/` - 止盈止损设置（按账户存储）

---

### 3. 📉 27币涨跌幅追踪系统

**数据统计**: 20文件，22,492条记录，58.07 MB，20天数据（2026-01-28 ~ 2026-02-16）

**JSONL目录**:
- `coin_change_tracker/` - 27币种分钟级涨跌幅跟踪（按日存储）
  - 文件格式: `coin_change_YYYYMMDD.jsonl`
  - 更新频率: 每1分钟
  - 基准价格: 每日00:00开盘价

---

### 4. 📍 价格位置预警系统 v2.0.5

**数据统计**: 6文件，791,833条记录，178.33 MB，2天数据（2026-02-15 ~ 2026-02-16）

**JSONL目录**:
- `price_position/` - 实时价格位置JSONL（按日存储）
  - 最新: `price_position_20260216.jsonl` (~2.7 MB)
- `price_speed_jsonl/` - 价格速度快照和历史
- `price_speed_10m/` - 10分钟粒度价格速度（按日存储）

**状态**: ✅ 正在运行，替代了老版"支撑压力(大盘)"系统

---

### 5. ⚠️ 恐慌监控洗盘

**数据统计**: 25文件，24,464条记录，14.98 MB，23天数据（2026-01-15 ~ 2026-02-10）

**JSONL目录**:
- `panic_jsonl/` - 恐慌指数快照
- `panic_daily/` - 按日恐慌数据

**状态**: 需要检查（最后更新：2026-02-10）

---

### 6. 🔔 11信号日线总

**数据统计**: 10文件，2,846条记录，0.59 MB，5天数据（2026-02-11 ~ 2026-02-15）

**JSONL目录**:
- `signal_stats/` - 1小时爆仓月线图信号统计

**状态**: 需要检查（最后更新：2026-02-15）

---

### 7. 📊 OKX日涨幅统计日记

**JSONL目录**:
- `okx_day_change/` - 日涨跌幅统计

**数据统计**: 可能合并到OKX全生态系统

---

## 🔴 已停用系统（已隐藏）

以下系统已停止运行并被新系统替代，数据管理页面不再显示：

### ⛔ 支撑压力(大盘) - 老版

- **停止时间**: 2026-02-07
- **数据目录**: `support_resistance_daily/`, `support_resistance_jsonl/`
- **数据量**: 45文件，1,641,238条记录，1,715.78 MB，41天数据
- **替代系统**: 价格位置预警系统 v2.0.5
- **状态**: 🔒 已隐藏，保留历史数据用于回测

### ⛔ 逃顶信号系统

- **停止时间**: 2026-01-28
- **数据目录**: `escape_signal_jsonl/`
- **数据量**: 3文件，56,142条记录，11.97 MB，1天数据
- **合并到**: 价格位置预警系统
- **状态**: 🔒 已隐藏，功能已整合到新系统

---

## 📝 数据管理页面显示规则

### ✅ 显示系统（7个）
1. SAR趋势系统
2. OKX全生态
3. 27币涨跌幅追踪系统
4. 价格位置预警系统
5. 恐慌监控洗盘
6. 11信号日线总
7. OKX日涨幅统计日记

### 🚫 隐藏目录（已停用）
- `support_resistance_daily/` - 老版支撑压力系统
- `support_resistance_jsonl/` - 老版支撑压力系统  
- `escape_signal_jsonl/` - 逃顶信号系统

---

## 🔧 系统映射配置

系统映射配置文件：`generate_system_grouped_data.py`

```python
SYSTEM_MAPPING = {
    "SAR趋势系统": {
        "dirs": ["sar_jsonl", "sar_slope_jsonl", "sar_1min", "sar_bias_stats"],
        "icon": "📈",
        "color": "#10B981"
    },
    "OKX全生态": {
        "dirs": ["okx_trading_jsonl", "okx_trading_history", "okx_trading_logs", 
                "okx_angle_analysis", "okx_auto_strategy", "okx_tpsl_settings"],
        "icon": "💹",
        "color": "#F59E0B"
    },
    "27币涨跌幅追踪系统": {
        "dirs": ["coin_change_tracker"],
        "icon": "📉",
        "color": "#6366F1"
    },
    "价格位置预警系统": {
        "dirs": ["price_speed_jsonl", "price_speed_10m", "price_position"],
        "icon": "📍",
        "color": "#06B6D4"
    },
    "恐慌监控洗盘": {
        "dirs": ["panic_jsonl", "panic_daily"],
        "icon": "⚠️",
        "color": "#DC2626"
    },
    "11信号日线总": {
        "dirs": ["signal_stats"],
        "icon": "🔔",
        "color": "#8B5CF6"
    },
    "OKX日涨幅统计日记": {
        "dirs": ["okx_day_change"],
        "icon": "📊",
        "color": "#EF4444"
    }
}
```

**注释说明**:
- 已停用系统：支撑压力(大盘) (已被价格位置预警系统替代)
- 已停用系统：逃顶信号系统 (已合并到价格位置预警系统)

---

## 🚀 快速命令

### 重新生成系统数据统计
```bash
cd /home/user/webapp
python3 generate_system_grouped_data.py
```

### 查看生成的JSON数据
```bash
cat data/system_grouped_data.json | python3 -m json.tool | less
```

### 检查最新数据文件
```bash
cd /home/user/webapp/data

# 各系统最新文件
ls -lht sar_1min/*.jsonl | head -3
ls -lht okx_trading_history/*.jsonl | head -3
ls -lht coin_change_tracker/*.jsonl | head -3
ls -lht price_position/*.jsonl | head -3
```

---

## 📊 总体数据统计

根据最新扫描（2026-02-16）：

| 系统 | 文件数 | 记录数 | 大小 | 天数 | 日期范围 |
|------|--------|--------|------|------|----------|
| SAR趋势系统 | 50 | 537,505 | 148.19 MB | 16 | 2026-02-01 ~ 2026-02-16 |
| OKX全生态 | 51 | 14,249 | 26.00 MB | 17 | 2026-01-21 ~ 2026-02-16 |
| 27币涨跌幅追踪 | 20 | 22,492 | 58.07 MB | 20 | 2026-01-28 ~ 2026-02-16 |
| 价格位置预警 | 6 | 791,833 | 178.33 MB | 2 | 2026-02-15 ~ 2026-02-16 |
| 恐慌监控洗盘 | 25 | 24,464 | 14.98 MB | 23 | 2026-01-15 ~ 2026-02-10 |
| 11信号日线总 | 10 | 2,846 | 0.59 MB | 5 | 2026-02-11 ~ 2026-02-15 |

**总计**: 162文件，1,393,389条记录（约139万），426.16 MB（约0.42 GB）

---

**文档更新**: 2026-02-16  
**生成脚本**: `generate_system_grouped_data.py`  
**数据文件**: `/home/user/webapp/data/system_grouped_data.json`  
**API端点**: `/api/data-management/systems-grouped`
