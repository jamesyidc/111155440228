# JSONL 文件说明文档

本文档详细说明每个 JSONL 文件存储的内容及其被哪些系统使用。

---

## 📍 价格位置预警系统

### 1. price_position/ 目录

#### price_position_YYYYMMDD.jsonl
**存储内容**：
- 27个币种的实时价格位置数据
- 每条记录包含一个时间快照（snapshot_time）和所有币种的价格数据

**字段说明**：
```json
{
  "snapshot_time": "2026-02-16 18:38:35",
  "positions": [
    {
      "inst_id": "BTC-USDT-SWAP",
      "current_price": 95234.5,
      "high_48h": 96500.0,      // 48小时最高价
      "low_48h": 93800.0,       // 48小时最低价
      "position_48h": 62.3,     // 48小时内价格位置百分比 (0-100)
      "high_7d": 98000.0,       // 7天最高价
      "low_7d": 91000.0,        // 7天最低价
      "position_7d": 58.7,      // 7天内价格位置百分比 (0-100)
      "alert_48h_low": 0,       // 48小时低位预警 (1=触发, position≤5%)
      "alert_48h_high": 0,      // 48小时高位预警 (1=触发, position≥95%)
      "alert_7d_low": 0,        // 7天低位预警
      "alert_7d_high": 0        // 7天高位预警
    }
    // ... 其他26个币种
  ]
}
```

**使用系统**：
- 📍 价格位置预警系统 v2.0.5
- 🔔 重大事件监控系统（读取预警信号）

**采集频率**：实时更新，每分钟写入一次  
**数据保留**：每日一个文件，保留最近7天

---

### 2. price_speed_jsonl/ 目录

#### latest_price_speed.jsonl
**存储内容**：
- 最新的价格速度（涨跌速度）快照
- 单文件实时更新

**字段说明**：
```json
{
  "timestamp": "2026-02-16 18:38:00",
  "coins": [
    {
      "symbol": "BTCUSDT",
      "current_price": 95234.5,
      "speed_1m": 0.05,        // 1分钟涨跌幅 (%)
      "speed_5m": 0.23,        // 5分钟涨跌幅
      "speed_15m": 0.87,       // 15分钟涨跌幅
      "speed_1h": 2.34         // 1小时涨跌幅
    }
    // ... 27个币种
  ]
}
```

**使用系统**：
- 📍 价格位置预警系统
- 🔔 重大事件监控系统（检测急涨急跌）

**采集频率**：每分钟更新  
**数据保留**：单文件，只保留最新快照

---

#### price_speed_history.jsonl
**存储内容**：
- 历史价格速度数据
- 每分钟追加一条记录

**字段说明**：同 `latest_price_speed.jsonl`

**使用系统**：
- 📍 价格位置预警系统（历史回溯）
- 📊 数据分析和回测

**采集频率**：每分钟追加  
**数据保留**：按大小轮转，保留约7天历史

---

### 3. price_speed_10m/ 目录

#### price_speed_10m_YYYYMMDD.jsonl
**存储内容**：
- 10分钟粒度的价格速度统计
- 每10分钟计算一次平均涨跌速度

**字段说明**：
```json
{
  "timestamp": "2026-02-16 18:30:00",
  "interval": "10m",
  "coins": [
    {
      "symbol": "BTCUSDT",
      "avg_speed": 0.15,       // 10分钟平均速度
      "max_speed": 0.35,       // 10分钟最大速度
      "min_speed": -0.12,      // 10分钟最小速度
      "volatility": 0.23       // 波动率
    }
  ]
}
```

**使用系统**：
- 📍 价格位置预警系统
- 📊 波动率分析

**采集频率**：每10分钟统计一次  
**数据保留**：每日一个文件，保留30天

---

## 📈 SAR趋势系统

### 4. sar_jsonl/ 目录

#### {COIN}.jsonl (例如: BTC.jsonl, ETH.jsonl)
**存储内容**：
- 单个币种的SAR（抛物线转向）指标数据
- 每条记录包含一个时间点的SAR值和趋势状态

**字段说明**：
```json
{
  "timestamp": "2026-02-16 18:35:00",
  "symbol": "BTCUSDT",
  "price": 95234.5,
  "sar_value": 94800.0,        // SAR指标值
  "trend": "bullish",          // 趋势: bullish(看涨) / bearish(看跌)
  "af": 0.02,                  // 加速因子
  "ep": 96500.0                // 极值点
}
```

**使用系统**：
- 📈 SAR趋势系统
- 🔔 重大事件监控系统（趋势反转信号）
- 🤖 OKX自动交易系统（趋势判断）

**采集频率**：每5分钟更新  
**数据保留**：每个币种独立文件，保留最近3000条记录

---

### 5. sar_slope_jsonl/ 目录

#### latest_sar_slope.jsonl
**存储内容**：
- 最新的SAR斜率数据
- SAR指标的变化速度

**字段说明**：
```json
{
  "timestamp": "2026-02-16 18:35:00",
  "coins": [
    {
      "symbol": "BTCUSDT",
      "sar_value": 94800.0,
      "sar_slope": 0.0023,     // SAR斜率（正值=上升趋势加强，负值=下降趋势加强）
      "slope_5m": 0.0015,      // 5分钟斜率变化
      "slope_15m": 0.0042,     // 15分钟斜率变化
      "trend_strength": 0.68   // 趋势强度 (0-1)
    }
  ]
}
```

**使用系统**：
- 📈 SAR趋势系统
- 🤖 OKX自动交易（判断入场时机）

**采集频率**：每5分钟更新  
**数据保留**：单文件，只保留最新快照

---

#### sar_slope_data.jsonl
**存储内容**：
- 历史SAR斜率数据
- 用于趋势分析和回测

**字段说明**：同 `latest_sar_slope.jsonl`

**使用系统**：
- 📈 SAR趋势系统（历史分析）
- 📊 回测系统

**采集频率**：每5分钟追加  
**数据保留**：保留最近7天

---

#### sar_slope_summary.jsonl
**存储内容**：
- SAR斜率每日汇总统计
- 包含最大/最小斜率、平均斜率等

**字段说明**：
```json
{
  "date": "2026-02-16",
  "summary": [
    {
      "symbol": "BTCUSDT",
      "max_slope": 0.0156,
      "min_slope": -0.0089,
      "avg_slope": 0.0034,
      "trend_changes": 3,      // 当日趋势反转次数
      "bullish_duration": 18.5, // 看涨持续小时数
      "bearish_duration": 5.5   // 看跌持续小时数
    }
  ]
}
```

**使用系统**：
- 📈 SAR趋势系统（日报统计）
- 📊 数据分析

**采集频率**：每日汇总一次  
**数据保留**：保留30天

---

### 6. sar_1min/ 目录

#### sar_1min_YYYYMMDD.jsonl
**存储内容**：
- 1分钟粒度的SAR数据
- 更精细的趋势判断

**字段说明**：类似 `{COIN}.jsonl`，但采集频率更高

**使用系统**：
- 📈 SAR趋势系统（精细分析）
- 🤖 高频交易策略

**采集频率**：每1分钟更新  
**数据保留**：每日一个文件，保留7天

---

### 7. sar_bias_stats/ 目录

#### sar_bias_YYYYMMDD.jsonl
**存储内容**：
- SAR乖离率统计
- 价格偏离SAR线的程度

**字段说明**：
```json
{
  "timestamp": "2026-02-16 18:35:00",
  "symbol": "BTCUSDT",
  "price": 95234.5,
  "sar_value": 94800.0,
  "bias": 0.46,                // 乖离率 (%) = (price - sar) / sar * 100
  "bias_level": "normal"       // 乖离程度: low / normal / high / extreme
}
```

**使用系统**：
- 📈 SAR趋势系统
- 🔔 重大事件监控（极端乖离预警）

**采集频率**：每5分钟更新  
**数据保留**：每日一个文件，保留14天

---

## 💹 OKX全生态

### 8. okx_trading_jsonl/ 目录

#### okx_day_change_YYYYMMDD.jsonl
**存储内容**：
- 27个币种的24小时涨跌幅数据
- 每5分钟采集一次最新数据

**字段说明**：
```json
{
  "timestamp": "2026-02-16 18:35:00",
  "symbol": "BTC-USDT-SWAP",
  "inst_id": "BTC-USDT-SWAP",
  "last_price": "95234.5",
  "change_24h": "2.34",        // 24小时涨跌幅 (%)
  "high_24h": "96500.0",
  "low_24h": "93000.0",
  "volume_24h": "1234567890",
  "turnover_24h": "117890000000"
}
```

**使用系统**：
- 💹 OKX全生态系统
- 📊 OKX日涨跌幅标记系统
- 🔔 重大事件监控（24小时涨跌幅预警）

**采集频率**：每5分钟更新  
**数据保留**：每日一个文件，保留30天

---

### 9. okx_trading_history/ 目录

#### okx_trades_YYYYMMDD.jsonl
**存储内容**：
- 当日所有交易记录
- 包含开仓、平仓、止盈止损触发等

**字段说明**：
```json
{
  "timestamp": "2026-02-16 14:23:15",
  "trade_id": "T20260216142315001",
  "symbol": "BTC-USDT-SWAP",
  "side": "buy",               // buy / sell
  "position_side": "long",     // long / short
  "action": "open",            // open / close / take_profit / stop_loss
  "price": 95234.5,
  "amount": 0.1,               // 数量（张数）
  "leverage": 10,              // 杠杆倍数
  "pnl": 0,                    // 盈亏（平仓时记录）
  "pnl_percent": 0,            // 盈亏百分比
  "reason": "manual"           // 交易原因: manual / auto / signal
}
```

**使用系统**：
- 💹 OKX全生态系统
- 🤖 OKX实盘交易系统
- 📊 OKX利润分析系统

**采集频率**：实时记录每笔交易  
**数据保留**：每日一个文件，永久保留

---

### 10. okx_trading_logs/ 目录

#### trading_log_YYYYMMDD.jsonl
**存储内容**：
- 交易系统运行日志
- 包含策略执行、风控检查、异常信息等

**字段说明**：
```json
{
  "timestamp": "2026-02-16 14:23:15",
  "level": "INFO",             // DEBUG / INFO / WARNING / ERROR
  "module": "auto_trader",
  "message": "检测到做多信号: BTC-USDT-SWAP",
  "details": {
    "symbol": "BTC-USDT-SWAP",
    "signal_type": "sar_bullish",
    "signal_strength": 0.85,
    "action_taken": "open_long"
  }
}
```

**使用系统**：
- 💹 OKX全生态系统
- 🤖 OKX实盘交易系统（调试和监控）
- 🔍 系统健康监控

**采集频率**：实时记录  
**数据保留**：每日一个文件，保留30天

---

### 11. okx_angle_analysis/ 目录

#### angle_analysis_YYYYMMDD.jsonl
**存储内容**：
- K线角度分析数据
- 价格变化的角度和趋势强度

**字段说明**：
```json
{
  "timestamp": "2026-02-16 14:23:15",
  "symbol": "BTC-USDT-SWAP",
  "timeframe": "15m",
  "angle": 45.5,               // K线角度（度）
  "angle_strength": "strong",  // weak / moderate / strong / extreme
  "trend_direction": "up",     // up / down / sideways
  "support_level": 94800.0,
  "resistance_level": 96200.0
}
```

**使用系统**：
- 💹 OKX全生态系统
- 🤖 OKX实盘交易（角度突破策略）

**采集频率**：每15分钟更新  
**数据保留**：每日一个文件，保留14天

---

### 12. okx_auto_strategy/ 目录

#### account_main_history.jsonl
**存储内容**：
- 主账户的自动交易策略历史
- 记录策略参数变化

**字段说明**：
```json
{
  "timestamp": "2026-02-16 10:00:00",
  "account": "main",
  "strategy": "sar_trend_following",
  "params": {
    "leverage": 10,
    "stop_loss": -10,          // 止损百分比
    "take_profit": 40,         // 止盈百分比
    "position_size": 0.1,      // 每次开仓比例
    "max_positions": 3         // 最大持仓数
  },
  "status": "active"
}
```

**使用系统**：
- 💹 OKX全生态系统
- 🤖 OKX实盘交易（策略管理）

**采集频率**：策略参数变更时记录  
**数据保留**：永久保留

---

#### account_point_history.jsonl
**存储内容**：
- 测试账户（point账户）的策略历史
- 用于策略回测和验证

**字段说明**：同 `account_main_history.jsonl`

**使用系统**：
- 💹 OKX全生态系统
- 🧪 策略测试和验证

**采集频率**：策略参数变更时记录  
**数据保留**：永久保留

---

### 13. okx_tpsl_settings/ 目录

#### account_main_tpsl_history.jsonl
**存储内容**：
- 主账户的止盈止损设置历史
- 记录每次修改止盈止损参数

**字段说明**：
```json
{
  "timestamp": "2026-02-16 14:25:00",
  "account": "main",
  "symbol": "BTC-USDT-SWAP",
  "position_side": "long",
  "take_profit": 40,           // 止盈百分比
  "stop_loss": -10,            // 止损百分比
  "trigger_type": "mark_price", // mark_price / last_price
  "updated_by": "auto"         // auto / manual
}
```

**使用系统**：
- 💹 OKX全生态系统
- 🤖 OKX实盘交易（风控管理）

**采集频率**：止盈止损参数变更时记录  
**数据保留**：永久保留

---

## ⚠️ 恐慌监控洗盘

### 14. panic_jsonl/ 目录

#### panic_index_latest.jsonl
**存储内容**：
- 最新的恐慌指数数据
- 基于爆仓数据和持仓量计算

**字段说明**：
```json
{
  "timestamp": "2026-02-16 18:35:00",
  "symbol": "BTCUSDT",
  "panic_index": 35.5,         // 恐慌指数 (0-100)
  "panic_level": "moderate",   // low / moderate / high / extreme
  "liquidation_24h": 125000000, // 24小时爆仓金额（美元）
  "liquidation_1h": 8500000,   // 1小时爆仓金额
  "open_interest": 25000000000, // 持仓量
  "oi_change_24h": -2.5,       // 持仓量24小时变化 (%)
  "funding_rate": 0.01         // 资金费率
}
```

**使用系统**：
- ⚠️ 恐慌监控洗盘系统
- 🔔 重大事件监控（恐慌指数预警）
- 🤖 OKX实盘交易（市场情绪判断）

**采集频率**：每小时更新  
**数据保留**：单文件，只保留最新快照

---

### 15. panic_daily/ 目录

#### panic_daily_YYYYMMDD.jsonl
**存储内容**：
- 每日恐慌指数统计
- 每小时记录一次

**字段说明**：同 `panic_index_latest.jsonl`

**使用系统**：
- ⚠️ 恐慌监控洗盘系统
- 📊 市场情绪分析

**采集频率**：每小时追加  
**数据保留**：每日一个文件，保留30天

---

## 🔔 11信号日线总

### 16. signal_stats/ 目录

#### signal_stats_YYYYMMDD.jsonl
**存储内容**：
- 每日信号统计汇总
- 包含1小时爆仓、30分钟K线等11个信号

**字段说明**：
```json
{
  "date": "2026-02-16",
  "signals": {
    "liquidation_1h": {
      "count": 15,             // 触发次数
      "max_amount": 185000000, // 最大爆仓金额
      "total_amount": 1250000000
    },
    "kline_30m_peak": {
      "count": 8,
      "max_peak": 175000000    // 最高峰值
    },
    "price_change_extreme": {
      "count": 5,
      "symbols": ["BTC", "ETH", "SOL"]
    }
    // ... 其他9个信号
  },
  "total_events": 28,          // 当日重大事件总数
  "most_active_hour": "14:00-15:00"
}
```

**使用系统**：
- 🔔 11信号日线总系统
- 🔔 重大事件监控系统
- 📊 每日市场回顾

**采集频率**：每日汇总一次  
**数据保留**：每日一个文件，保留90天

---

## 📉 27币涨跌幅追踪系统

### 17. coin_change_tracker/ 目录

#### coin_change_YYYYMMDD.jsonl
**存储内容**：
- 27个币种的实时涨跌幅追踪
- 以每日开盘价（00:00）作为基准

**字段说明**：
```json
{
  "timestamp": "2026-02-16 18:35:00",
  "baseline_time": "2026-02-16 00:00:00",
  "summary": {
    "up_count": 18,            // 上涨币种数
    "down_count": 9,           // 下跌币种数
    "up_ratio": 66.67,         // 上涨比例 (%)
    "avg_change": 1.23,        // 平均涨跌幅
    "max_gain": 5.67,          // 最大涨幅
    "max_loss": -3.21          // 最大跌幅
  },
  "changes": [
    {
      "symbol": "BTCUSDT",
      "baseline_price": 93500.0,
      "current_price": 95234.5,
      "change_percent": 1.85,
      "change_tag": "up",      // up / down / flat
      "high_today": 96000.0,
      "low_today": 93200.0
    }
    // ... 其他26个币种
  ]
}
```

**使用系统**：
- 📉 27币涨跌幅追踪系统
- 🔔 重大事件监控（整体涨跌幅监控）
- 📊 市场热度分析

**采集频率**：每1分钟更新  
**数据保留**：每日一个文件，保留30天

---

## 🗄️ 已归档系统（历史数据保留，但不在界面显示）

### 18. support_resistance_daily/ 目录（已停用）

#### support_resistance_YYYYMMDD.jsonl
**存储内容**：
- 27个币种的支撑压力位数据（老版系统）
- 7天和48小时双周期计算

**停止原因**：已被"价格位置预警系统 v2.0.5"替代  
**停止日期**：2026-02-07  
**数据保留**：历史数据完整保留，用于回测分析

---

### 19. escape_signal_jsonl/ 目录（已停用）

#### escape_signal_YYYYMMDD.jsonl
**存储内容**：
- 2小时顶部逃离信号
- 价格突破检测

**停止原因**：功能已合并到"价格位置预警系统"  
**停止日期**：2026-01-28  
**数据保留**：历史数据完整保留

---

## 📋 使用系统汇总

### 首页系统与JSONL文件对应关系

| 系统名称 | JSONL目录 | 文件数 | 主要用途 |
|---------|----------|--------|---------|
| 📍 价格位置预警系统 | price_position<br>price_speed_jsonl<br>price_speed_10m | 6 | 价格位置监控、预警 |
| 📈 SAR趋势系统 | sar_jsonl<br>sar_slope_jsonl<br>sar_1min<br>sar_bias_stats | 50 | 趋势判断、信号生成 |
| 💹 OKX全生态 | okx_trading_jsonl<br>okx_trading_history<br>okx_trading_logs<br>okx_angle_analysis<br>okx_auto_strategy<br>okx_tpsl_settings | 51 | 实盘交易、策略管理 |
| ⚠️ 恐慌监控洗盘 | panic_jsonl<br>panic_daily | 25 | 市场情绪监控 |
| 🔔 11信号日线总 | signal_stats | 10 | 每日信号统计 |
| 📉 27币涨跌幅追踪系统 | coin_change_tracker | 20 | 实时涨跌幅追踪 |

---

## 🔍 快速查找指南

### 按用途查找

**实时价格数据**：
- `price_position_YYYYMMDD.jsonl` - 价格位置
- `okx_day_change_YYYYMMDD.jsonl` - 24小时涨跌幅
- `coin_change_YYYYMMDD.jsonl` - 日内涨跌幅

**趋势判断**：
- `{COIN}.jsonl` (sar_jsonl) - SAR指标
- `latest_sar_slope.jsonl` - SAR斜率
- `angle_analysis_YYYYMMDD.jsonl` - K线角度

**交易记录**：
- `okx_trades_YYYYMMDD.jsonl` - 交易明细
- `trading_log_YYYYMMDD.jsonl` - 交易日志

**市场情绪**：
- `panic_index_latest.jsonl` - 恐慌指数
- `panic_daily_YYYYMMDD.jsonl` - 每日恐慌数据

**统计分析**：
- `signal_stats_YYYYMMDD.jsonl` - 信号统计
- `sar_slope_summary.jsonl` - SAR汇总

---

**文档更新时间**：2026-02-16  
**文档版本**：v1.0  
**总文件类型**：19种  
**活跃系统**：6个  
