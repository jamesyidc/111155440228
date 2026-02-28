# 系统健康检查清单

**最后更新**: 2026-02-01 12:35 (北京时间 UTC+8)

本文档列出了所有系统的完整依赖关系，包括PM2服务、数据文件、API路由、前端页面等，用于快速诊断系统问题。

---

## 目录

1. [27币涨跌幅追踪系统](#1-27币涨跌幅追踪系统)
2. [SAR斜率系统](#2-sar斜率系统)
3. [逃顶信号系统](#3-逃顶信号系统)
4. [支撑压力线系统](#4-支撑压力线系统)
5. [锚点盈利统计系统](#5-锚点盈利统计系统)
6. [恐慌清洗指数系统](#6-恐慌清洗指数系统)
7. [1小时爆仓金额系统](#7-1小时爆仓金额系统)
8. [数据健康监控系统](#8-数据健康监控系统)
9. [OKX交易系统](#9-okx交易系统)
10. [重大事件监控系统](#10-重大事件监控系统)

---

## 1. 27币涨跌幅追踪系统

### 📋 基本信息
- **页面URL**: `/coin-change-tracker`
- **系统名称**: 27币涨跌幅追踪系统
- **更新频率**: 60秒
- **数据来源**: OKX API实时价格

### 🔧 依赖组件

#### PM2服务
```bash
# 主服务
pm2 list | grep coin-change-tracker
# 预期: online, 重启次数低, 内存约30MB
```

#### 数据文件
```bash
# 实时数据
ls -lh data/coin_change_tracker/coin_change_tracker.jsonl
# 预期: 文件存在, 大小合理, 修改时间<2分钟

# 基准价数据
ls -lh data/coin_change_tracker/daily_baseline.jsonl
# 预期: 文件存在, 包含当日00:00基准价

# 检查最新数据
tail -1 data/coin_change_tracker/coin_change_tracker.jsonl | jq '{timestamp, symbol, current_price, change_percent}'
# 预期: timestamp为最近1分钟内
```

#### API路由
```bash
# 1. 最新数据API
curl -s 'http://localhost:5000/api/coin-change-tracker/latest' | jq '{success, data_count: (.data | length), sample: .data[0] | {symbol, current_price, change_percent}}'
# 预期: success=true, data_count=27

# 2. 历史数据API
curl -s 'http://localhost:5000/api/coin-change-tracker/history?limit=10' | jq '{success, data_count: (.data | length)}'
# 预期: success=true, data_count=10

# 3. 基准价API
curl -s 'http://localhost:5000/api/coin-change-tracker/baseline' | jq '{success, baseline_count: (.baselines | length)}'
# 预期: success=true, baseline_count=27
```

#### 路由定义
```bash
grep -n "coin-change-tracker" source_code/app_new.py | head -5
# 预期: 找到路由定义
```

#### 健康检查脚本
```bash
#!/bin/bash
# 检查coin-change-tracker健康状态

echo "=== 27币涨跌幅追踪系统健康检查 ==="

# 1. PM2状态
pm2 jlist | jq '.[] | select(.name == "coin-change-tracker") | {name, status: .pm2_env.status, restarts: .pm2_env.restart_time}'

# 2. 数据文件
echo "最新数据时间:"
tail -1 data/coin_change_tracker/coin_change_tracker.jsonl | jq -r '.timestamp'

# 3. API测试
echo "API状态:"
curl -s 'http://localhost:5000/api/coin-change-tracker/latest' | jq '{success, data_count: (.data | length)}'

# 4. 数据时效性
echo "数据延迟(分钟):"
LATEST_TIME=$(tail -1 data/coin_change_tracker/coin_change_tracker.jsonl | jq -r '.timestamp')
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')
python3 -c "from datetime import datetime; a = datetime.strptime('$LATEST_TIME', '%Y-%m-%d %H:%M:%S'); b = datetime.strptime('$CURRENT_TIME', '%Y-%m-%d %H:%M:%S'); print((b-a).total_seconds() / 60)"
```

### ⚠️ 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 页面空白 | PM2服务停止 | `pm2 restart coin-change-tracker` |
| 数据不更新 | OKX API限流 | 检查日志，等待恢复 |
| 基准价错误 | 00:00未采集到开盘价 | 手动修复 daily_baseline.jsonl |
| API返回错误 | JSONL文件损坏 | 备份并重建文件 |

---

## 2. SAR斜率系统

### 📋 基本信息
- **主页URL**: `/sar-slope`
- **详情页URL**: `/sar-slope/<symbol>`
- **系统名称**: SAR斜率系统
- **更新频率**: 主页60秒, 详情页5分钟
- **数据来源**: OKX K线数据 + SAR计算

### 🔧 依赖组件

#### PM2服务
```bash
# 1. SAR原始数据采集器
pm2 list | grep sar-jsonl-collector
# 预期: online, 每5分钟采集一次

# 2. SAR斜率数据计算器
pm2 list | grep sar-slope-collector
# 预期: online, 每60秒计算一次
```

#### 数据文件
```bash
# 1. 原始SAR数据（27个币种各一个文件）
ls -lh data/sar_jsonl/*.jsonl | wc -l
# 预期: 27个文件

# 检查XRP最新数据
tail -1 data/sar_jsonl/XRP.jsonl | jq '{beijing_time, position, sar, price}'
# 预期: beijing_time为最近10分钟内

# 2. SAR斜率汇总数据
tail -1 data/sar_slope_jsonl/sar_slope_data.jsonl | jq '{collection_time, symbol, sar_position}'
# 预期: collection_time为最近2分钟内
```

#### API路由
```bash
# 1. 主页API - 所有币种状态
curl -s 'http://localhost:5000/api/sar-slope/status' | jq '{success, count, bullish_count, bearish_count}'
# 预期: success=true, count=27

# 2. 最新数据API
curl -s 'http://localhost:5000/api/sar-slope/latest' | jq '{data_count: (.data | length), sample: .data[0] | {symbol, sar_position}}'
# 预期: data_count=27

# 3. 详情页API - 单个币种周期
curl -s 'http://localhost:5000/api/sar-slope/current-cycle/XRP?limit=10' | jq '{success, symbol, total_sequences, current_status: {last_update, position}}'
# 预期: success=true, last_update为最近10分钟内
```

#### 路由定义
```bash
grep -n "sar-slope" source_code/app_new.py | grep "@app.route"
# 预期: 找到主页路由、详情页路由、多个API路由
```

#### 健康检查脚本
```bash
#!/bin/bash
echo "=== SAR斜率系统健康检查 ==="

# 1. PM2服务状态
echo "1. 采集器状态:"
pm2 jlist | jq '.[] | select(.name == "sar-jsonl-collector" or .name == "sar-slope-collector") | {name, status: .pm2_env.status, restarts: .pm2_env.restart_time}'

# 2. 原始数据文件数量
echo "2. 原始数据文件:"
ls data/sar_jsonl/*.jsonl | wc -l

# 3. 最新数据时间
echo "3. XRP最新SAR数据:"
tail -1 data/sar_jsonl/XRP.jsonl | jq '{beijing_time, position}'

# 4. 主页API
echo "4. 主页API状态:"
curl -s 'http://localhost:5000/api/sar-slope/status' | jq '{success, count}'

# 5. 详情页API
echo "5. 详情页API状态:"
curl -s 'http://localhost:5000/api/sar-slope/current-cycle/XRP?limit=1' | jq '{success, current_status: {last_update}}'
```

### ⚠️ 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 详情页显示undefined | sar-jsonl-collector停止 | 检查okx模块，重启采集器 |
| 主页数据不更新 | sar-slope-collector停止 | `pm2 restart sar-slope-collector` |
| 原始数据缺失 | OKX API错误 | 检查网络，查看错误日志 |
| 斜率计算错误 | 数据文件损坏 | 检查JSONL格式，重新采集 |

---

## 3. 逃顶信号系统

### 📋 基本信息
- **历史页URL**: `/escape-signal-history`
- **系统名称**: 逃顶信号统计系统
- **更新频率**: 60秒
- **数据来源**: 支撑压力线 + 锚点系统

### 🔧 依赖组件

#### PM2服务
```bash
# 1. 逃顶信号计算器
pm2 list | grep escape-signal-calculator
# 预期: online, 内存约60-70MB

# 2. 逃顶信号监控器（告警）
pm2 list | grep escape-signal-monitor
# 预期: online
```

#### 数据文件
```bash
# 1. 逃顶信号统计数据
tail -1 data/escape_signal_jsonl/escape_signal_stats.jsonl | jq '{stat_time, signal_2h_count, signal_24h_count}'
# 预期: stat_time为最近2分钟内

# 2. 峰值数据
tail -1 data/escape_signal_jsonl/escape_signal_peaks.jsonl | jq '{stat_time, signal_2h_count, signal_24h_count}'
# 预期: 文件存在且有数据
```

#### API路由
```bash
# 1. 关键点API（图表用）
curl -s 'http://localhost:5000/api/escape-signal-stats/keypoints?limit=5' | jq '{keypoint_count, data_range, last_3: .keypoints[-3:] | [.[] | {stat_time, signal_24h_count}]}'
# 预期: keypoint_count > 0, 最新stat_time为今天

# 2. 历史数据API（表格用）
curl -s 'http://localhost:5000/api/escape-signal-stats?limit=10' | jq '{data_range, history_count: (.history_data | length), first: .history_data[0] | {stat_time, signal_24h_count}}'
# 预期: first.stat_time为最新数据

# 3. 简化API
curl -s 'http://localhost:5000/api/escape-signal-simple' | jq '{success, recent_data_count: (.recent_data | length)}'
# 预期: success=true
```

#### 路由定义
```bash
grep -n "escape-signal" source_code/app_new.py | grep "@app.route" | head -10
# 预期: 找到页面路由和多个API路由
```

#### 健康检查脚本
```bash
#!/bin/bash
echo "=== 逃顶信号系统健康检查 ==="

# 1. PM2状态
echo "1. 服务状态:"
pm2 jlist | jq '.[] | select(.name | contains("escape-signal")) | {name, status: .pm2_env.status, mem: .monit.memory}'

# 2. 最新数据
echo "2. 最新统计数据:"
tail -1 data/escape_signal_jsonl/escape_signal_stats.jsonl | jq '{stat_time, signal_2h_count, signal_24h_count}'

# 3. API测试
echo "3. 关键点API:"
curl -s 'http://localhost:5000/api/escape-signal-stats/keypoints?limit=1' | jq '{data_range}'

echo "4. 历史API:"
curl -s 'http://localhost:5000/api/escape-signal-stats?limit=1' | jq '{data_range}'
```

### ⚠️ 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 页面显示旧数据 | API返回正序数据 | 已修复，重启Flask |
| 数据不更新 | escape-signal-calculator停止 | `pm2 restart escape-signal-calculator` |
| 内存占用高 | 数据量大 | 正常，约60-70MB |
| API返回空数据 | JSONL文件损坏 | 检查文件完整性 |

---

## 4. 支撑压力线系统

### 📋 基本信息
- **页面URL**: `/support-resistance`
- **系统名称**: 支撑压力线统计
- **更新频率**: 30秒
- **数据来源**: OKX K线 + 技术指标计算

### 🔧 依赖组件

#### PM2服务
```bash
# 1. 支撑压力线采集器
pm2 list | grep support-resistance-collector
# 预期: online, 每30秒采集一次

# 2. 快照服务
pm2 list | grep support-resistance-snapshot
# 预期: online, 内存约70MB
```

#### 数据文件
```bash
# 1. 每日数据文件（按日期分片）
TODAY=$(date +%Y%m%d)
ls -lh data/support_resistance_daily/support_resistance_${TODAY}.jsonl
# 预期: 文件存在, 大小增长中

# 检查最新数据
tail -1 data/support_resistance_daily/support_resistance_${TODAY}.jsonl | jq '{type, date, time}'
# 预期: time为最近1分钟内

# 2. 汇总数据
ls -lh data/support_resistance_jsonl/
# 预期: 目录存在，包含各类汇总文件
```

#### API路由
```bash
# 1. 最新数据API
curl -s 'http://localhost:5000/api/support-resistance/latest' | jq '{success, data_count: (.data | length), sample: .data[0] | {symbol, current_price, support_1, resistance_1}}'
# 预期: success=true, data_count=27

# 2. 快照数据API
curl -s 'http://localhost:5000/api/support-resistance/snapshots' | jq '{success, snapshots_count: (.snapshots | length)}'
# 预期: success=true

# 3. 信号计算API
curl -s 'http://localhost:5000/api/support-resistance/signals-computed' | jq '{buy_signals_24h_count: (.buy_signals_24h | length), sell_signals_24h_count: (.sell_signals_24h | length)}'
# 预期: 返回信号数量

# 4. 最新信号API
curl -s 'http://localhost:5000/api/support-resistance/latest-signal' | jq '{success, message}'
# 预期: success=true
```

#### 路由定义
```bash
grep -n "support-resistance" source_code/app_new.py | grep "@app.route" | head -10
# 预期: 找到页面路由和多个API路由
```

#### 健康检查脚本
```bash
#!/bin/bash
echo "=== 支撑压力线系统健康检查 ==="

# 1. PM2状态
echo "1. 服务状态:"
pm2 jlist | jq '.[] | select(.name | contains("support-resistance")) | {name, status: .pm2_env.status, restarts: .pm2_env.restart_time}'

# 2. 今日数据文件
TODAY=$(date +%Y%m%d)
echo "2. 今日数据文件:"
ls -lh data/support_resistance_daily/support_resistance_${TODAY}.jsonl

# 3. 最新数据时间
echo "3. 最新数据时间:"
tail -1 data/support_resistance_daily/support_resistance_${TODAY}.jsonl | jq '{type, time}'

# 4. API测试
echo "4. 最新数据API:"
curl -s 'http://localhost:5000/api/support-resistance/latest' | jq '{success, data_count: (.data | length)}'

# 5. 预警统计
echo "5. 当前预警统计:"
curl -s 'http://localhost:5000/api/support-resistance/latest' | jq '[.data[] | select(.alert_48h_high == true or .alert_7d_high == true or .alert_48h_low == true or .alert_7d_low == true)] | length'
```

### ⚠️ 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 页面显示空白 | 当前无预警触发 | 正常，等待价格触发预警 |
| 数据不更新 | support-resistance-collector停止 | `pm2 restart support-resistance-collector` |
| API返回空数据 | 数据文件缺失 | 检查数据目录权限 |
| 快照服务重启频繁 | 内存泄漏 | 监控内存，必要时重启 |

---

## 5. 锚点盈利统计系统

### 📋 基本信息
- **页面URL**: `/anchor-system`
- **系统名称**: 锚点盈利统计系统
- **更新频率**: 60秒
- **数据来源**: 极值追踪 + 实时价格

### 🔧 依赖组件

#### PM2服务
```bash
# 锚点盈利监控器
pm2 list | grep anchor-profit-monitor
# 预期: online, 内存约30MB
```

#### 数据文件
```bash
# 1. 盈利历史数据
tail -5 data/anchor_profit/anchor_profit_history.jsonl | jq '{datetime, total_positions, total_profit_percent}'
# 预期: datetime为最近2分钟内

# 2. 多头盈利数据
tail -1 data/anchor_profit/long_profit_history.jsonl | jq '{datetime, profitable_count, total_profit}'
# 预期: 文件存在且有数据

# 3. 空头盈利数据
tail -1 data/anchor_profit/short_profit_history.jsonl | jq '{datetime, profitable_count, total_profit}'
# 预期: 文件存在且有数据
```

#### API路由
```bash
# 1. 盈利历史API
curl -s 'http://localhost:5000/api/anchor-system/profit-history' | jq '{history_count: (.history | length), latest: .history[-1] | {datetime, total_profit_percent}}'
# 预期: history_count > 0

# 2. 当前持仓API
curl -s 'http://localhost:5000/api/anchor-system/current-positions' | jq '{positions_count: (.positions | length)}'
# 预期: positions_count ≤ 27

# 3. 统计API
curl -s 'http://localhost:5000/api/anchor-system/stats' | jq '{success}'
# 预期: success=true
```

#### 路由定义
```bash
grep -n "anchor-system" source_code/app_new.py | grep "@app.route"
# 预期: 找到页面路由和API路由
```

#### 健康检查脚本
```bash
#!/bin/bash
echo "=== 锚点盈利统计系统健康检查 ==="

# 1. PM2状态
pm2 jlist | jq '.[] | select(.name == "anchor-profit-monitor") | {name, status: .pm2_env.status, uptime: .pm2_env.pm_uptime}'

# 2. 数据文件
echo "数据文件:"
ls -lh data/anchor_profit/*.jsonl

# 3. 最新数据
echo "最新盈利数据:"
tail -1 data/anchor_profit/anchor_profit_history.jsonl | jq '{datetime, total_profit_percent}'

# 4. API测试
echo "API状态:"
curl -s 'http://localhost:5000/api/anchor-system/profit-history' | jq '{history_count: (.history | length)}'
```

### ⚠️ 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 盈利数据不更新 | anchor-profit-monitor停止 | `pm2 restart anchor-profit-monitor` |
| 持仓数量异常 | 极值数据缺失 | 检查极值追踪系统 |
| API返回空数据 | JSONL文件损坏 | 备份并重建 |

---

## 6. 恐慌清洗指数系统

### 📋 基本信息
- **页面URL**: `/panic`
- **系统名称**: 恐慌清洗指数
- **更新频率**: 60秒
- **数据来源**: 极值追踪系统计算

### 🔧 依赖组件

#### PM2服务
```bash
# 恐慌清洗采集器
pm2 list | grep panic-collector
# 预期: online
```

#### 数据文件
```bash
# 恐慌指数数据
tail -1 data/panic_index/panic_index.jsonl | jq '{record_time, panic_index, status}'
# 预期: record_time为最近2分钟内
```

#### API路由
```bash
# 1. 最新数据API
curl -s 'http://localhost:5000/api/panic/latest' | jq '{success, data: {record_time, panic_index, status}}'
# 预期: success=true

# 2. 历史数据API
curl -s 'http://localhost:5000/api/panic/history?limit=10' | jq '{data_count: (.data | length)}'
# 预期: data_count=10

# 3. 1小时曲线API
curl -s 'http://localhost:5000/api/panic/hour1-curve' | jq '{data_count: (.data | length)}'
# 预期: data_count > 0
```

#### 健康检查脚本
```bash
#!/bin/bash
echo "=== 恐慌清洗指数系统健康检查 ==="

pm2 jlist | jq '.[] | select(.name == "panic-collector") | {name, status: .pm2_env.status}'
tail -1 data/panic_index/panic_index.jsonl | jq '{record_time, panic_index}'
curl -s 'http://localhost:5000/api/panic/latest' | jq '{success, data: {panic_index}}'
```

---

## 7. 1小时爆仓金额系统

### 📋 基本信息
- **数据来源**: OKX爆仓数据
- **更新频率**: 60秒
- **PM2服务**: liquidation-1h-collector

### 🔧 依赖组件

#### PM2服务
```bash
pm2 list | grep liquidation-1h-collector
# 预期: online
```

#### 数据文件
```bash
tail -1 data/liquidation/liquidation_1h.jsonl | jq '{datetime, total_liquidation}'
# 预期: datetime为最近2分钟内
```

#### API路由
```bash
curl -s 'http://localhost:5000/api/panic/hour1-curve' | jq '{data_count: (.data | length), latest: .data[-1] | {datetime, total_liquidation}}'
# 预期: data_count > 0
```

---

## 8. 数据健康监控系统

### 📋 基本信息
- **页面URL**: `/data-health-monitor`
- **系统名称**: 数据健康监控与自动修复
- **更新频率**: 60秒
- **监控系统数量**: 6个

### 🔧 依赖组件

#### PM2服务
```bash
pm2 list | grep data-health-monitor
# 预期: online, 内存约33MB
```

#### 配置文件
```bash
# 监控配置
cat source_code/data_health_monitor.py | grep "MONITORS = {"
# 预期: 包含6个监控配置
```

#### 状态文件
```bash
# 状态持久化文件
cat data/data_health_monitor_state.json | jq 'keys'
# 预期: 包含6个监控器的状态
```

#### API路由
```bash
curl -s 'http://localhost:5000/api/data-health-monitor/status' | jq '{stats, monitors_count: (.monitors | length)}'
# 预期: monitors_count=6, 显示healthy/unhealthy统计
```

#### 健康检查脚本
```bash
#!/bin/bash
echo "=== 数据健康监控系统健康检查 ==="

# 1. 自身状态
pm2 jlist | jq '.[] | select(.name == "data-health-monitor") | {name, status: .pm2_env.status}'

# 2. 监控的系统数量
curl -s 'http://localhost:5000/api/data-health-monitor/status' | jq '{total: .stats.total, healthy: .stats.healthy, unhealthy: .stats.unhealthy}'

# 3. 每个系统的状态
curl -s 'http://localhost:5000/api/data-health-monitor/status' | jq '.monitors[] | {name, status, delay_minutes}'
```

---

## 9. OKX交易系统

### 📋 基本信息
- **页面URL**: `/okx-trading`
- **系统名称**: OKX实盘交易系统
- **功能**: 账户管理、持仓、开仓、平仓

### 🔧 依赖组件

#### 配置文件
```bash
# OKX API配置
ls -lh okx_config.json
# 预期: 文件存在, 包含api_key, secret_key, passphrase

# 检查配置格式
jq '{api_key_length: (.api_key | length), has_secret: (.secret_key != null)}' okx_config.json
# 预期: api_key_length > 0, has_secret=true
```

#### 数据文件
```bash
# 交易日志
ls -lh data/okx_trading/trading_log.jsonl
# 预期: 文件存在

# 最近交易记录
tail -5 data/okx_trading/trading_log.jsonl | jq '{timestamp, action, symbol}'
```

#### API路由
```bash
# 1. 账户信息API
curl -s 'http://localhost:5000/api/okx/account-info' | jq '{success}'
# 预期: success=true（需要有效的API配置）

# 2. 持仓信息API
curl -s 'http://localhost:5000/api/okx/positions' | jq '{success}'
# 预期: success=true

# 3. 交易历史API
curl -s 'http://localhost:5000/api/okx/trading-history' | jq '{trades_count: (.trades | length)}'
# 预期: trades_count ≥ 0
```

#### 路由定义
```bash
grep -n "okx-trading\|/api/okx" source_code/app_new.py | grep "@app.route" | head -10
# 预期: 找到页面路由和多个API路由
```

#### 健康检查脚本
```bash
#!/bin/bash
echo "=== OKX交易系统健康检查 ==="

# 1. 配置文件
echo "1. 配置文件:"
if [ -f okx_config.json ]; then
    echo "✅ 配置文件存在"
    jq '{api_key_length: (.api_key | length)}' okx_config.json
else
    echo "❌ 配置文件缺失"
fi

# 2. 数据目录
echo "2. 数据目录:"
ls -lh data/okx_trading/

# 3. API测试（需要有效配置）
echo "3. API测试:"
curl -s 'http://localhost:5000/api/okx/positions' | jq '{success}'
```

### ⚠️ 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| API调用失败 | API配置错误 | 检查okx_config.json |
| 无法开仓 | 账户余额不足 | 充值或调整仓位 |
| 持仓显示错误 | API权限不足 | 检查API权限设置 |

---

## 10. 重大事件监控系统

### 📋 基本信息
- **页面URL**: `/major-events`
- **系统名称**: 重大事件监控
- **更新频率**: 实时检测
- **PM2服务**: major-events-monitor

### 🔧 依赖组件

#### PM2服务
```bash
pm2 list | grep major-events-monitor
# 预期: online, 内存约160MB
```

#### 数据文件
```bash
# 事件记录
ls -lh data/major_events/
# 预期: 目录存在，包含事件记录文件

# 最新事件
tail -5 data/major_events/events.jsonl | jq '{timestamp, event_type, coins_count}'
```

#### API路由
```bash
# 1. 最新事件API
curl -s 'http://localhost:5000/api/major-events/latest' | jq '{events_count: (.events | length)}'
# 预期: events_count ≥ 0

# 2. 事件历史API
curl -s 'http://localhost:5000/api/major-events/history?limit=10' | jq '{events_count: (.events | length)}'
# 预期: events_count ≤ 10
```

---

## 🛠️ 通用健康检查工具

### 完整系统健康检查脚本

```bash
#!/bin/bash
# 文件: /home/user/webapp/scripts/system_health_check.sh

echo "========================================"
echo "   系统完整健康检查"
echo "   时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# 1. PM2服务状态
echo -e "\n【1. PM2服务状态】"
pm2 jlist | jq '[.[] | {name, status: .pm2_env.status, restarts: .pm2_env.restart_time, mem: (.monit.memory / 1024 / 1024 | round)}] | map(select(.status == "errored" or .status == "stopped"))'

# 2. Flask服务
echo -e "\n【2. Flask服务】"
curl -s 'http://localhost:5000/' > /dev/null && echo "✅ Flask运行正常" || echo "❌ Flask无响应"

# 3. 数据健康监控
echo -e "\n【3. 数据健康监控】"
curl -s 'http://localhost:5000/api/data-health-monitor/status' | jq '{total: .stats.total, healthy: .stats.healthy, unhealthy: .stats.unhealthy, today_restarts: .stats.today_restarts}'

# 4. 各系统最新数据时间
echo -e "\n【4. 数据时效性检查】"

echo "27币涨跌幅:"
tail -1 data/coin_change_tracker/coin_change_tracker.jsonl | jq -r '.timestamp'

echo "SAR斜率:"
tail -1 data/sar_slope_jsonl/sar_slope_data.jsonl | jq -r '.collection_time'

echo "逃顶信号:"
tail -1 data/escape_signal_jsonl/escape_signal_stats.jsonl | jq -r '.stat_time'

echo "支撑压力线:"
TODAY=$(date +%Y%m%d)
tail -1 data/support_resistance_daily/support_resistance_${TODAY}.jsonl 2>/dev/null | jq -r '.time // "文件不存在"'

# 5. 磁盘空间
echo -e "\n【5. 磁盘空间】"
df -h /home/user/webapp | tail -1 | awk '{print "使用: "$3" / "$2" ("$5")"}'

# 6. 数据目录大小
echo -e "\n【6. 数据目录大小】"
du -sh data/ logs/

echo -e "\n========================================"
echo "   健康检查完成"
echo "========================================"
```

### 快速诊断脚本

```bash
#!/bin/bash
# 文件: /home/user/webapp/scripts/quick_diagnosis.sh
# 用途: 快速诊断某个系统的问题

SYSTEM=$1

if [ -z "$SYSTEM" ]; then
    echo "用法: $0 <系统名称>"
    echo "可选系统: coin-change-tracker, sar-slope, escape-signal, support-resistance"
    exit 1
fi

case $SYSTEM in
    "coin-change-tracker")
        echo "=== 27币涨跌幅追踪系统诊断 ==="
        pm2 jlist | jq '.[] | select(.name == "coin-change-tracker")'
        tail -1 data/coin_change_tracker/coin_change_tracker.jsonl | jq
        curl -s 'http://localhost:5000/api/coin-change-tracker/latest' | jq '{success, data_count: (.data | length)}'
        ;;
    
    "sar-slope")
        echo "=== SAR斜率系统诊断 ==="
        pm2 jlist | jq '.[] | select(.name | contains("sar"))'
        tail -1 data/sar_jsonl/XRP.jsonl | jq
        tail -1 data/sar_slope_jsonl/sar_slope_data.jsonl | jq
        curl -s 'http://localhost:5000/api/sar-slope/status' | jq
        ;;
    
    "escape-signal")
        echo "=== 逃顶信号系统诊断 ==="
        pm2 jlist | jq '.[] | select(.name | contains("escape"))'
        tail -1 data/escape_signal_jsonl/escape_signal_stats.jsonl | jq
        curl -s 'http://localhost:5000/api/escape-signal-stats/keypoints?limit=1' | jq '{data_range}'
        ;;
    
    "support-resistance")
        echo "=== 支撑压力线系统诊断 ==="
        pm2 jlist | jq '.[] | select(.name | contains("support"))'
        TODAY=$(date +%Y%m%d)
        tail -1 data/support_resistance_daily/support_resistance_${TODAY}.jsonl | jq
        curl -s 'http://localhost:5000/api/support-resistance/latest' | jq '{success, data_count: (.data | length)}'
        ;;
    
    *)
        echo "未知系统: $SYSTEM"
        exit 1
        ;;
esac
```

---

## 📊 依赖关系图

```
数据流向图:

OKX API
  ↓
coin-price-tracker ──→ 实时价格数据
  ↓
├─→ coin-change-tracker ──→ 27币涨跌幅
├─→ sar-jsonl-collector ──→ SAR原始数据 ──→ sar-slope-collector ──→ SAR斜率
├─→ support-resistance-collector ──→ 支撑压力线
├─→ liquidation-1h-collector ──→ 爆仓数据 ──→ panic-collector ──→ 恐慌指数
└─→ anchor-profit-monitor ──→ 锚点盈利

支撑压力线 + 锚点盈利
  ↓
escape-signal-calculator ──→ 逃顶信号

所有系统
  ↓
data-health-monitor ──→ 健康监控

Flask ──→ 前端页面 + API路由
```

---

## 📝 维护建议

### 日常检查（每天）
```bash
# 1. 检查所有PM2服务状态
pm2 status

# 2. 检查数据健康监控
curl -s 'http://localhost:5000/api/data-health-monitor/status' | jq

# 3. 检查磁盘空间
df -h /home/user/webapp

# 4. 查看错误日志
pm2 logs --err --lines 50
```

### 周度检查（每周）
```bash
# 1. 清理旧日志
pm2 flush

# 2. 检查数据文件大小
du -sh data/*/

# 3. 备份重要配置
tar -czf backup_$(date +%Y%m%d).tar.gz okx_config.json ecosystem.config.js

# 4. 检查所有数据文件的最新时间
find data/ -name "*.jsonl" -exec ls -lh {} \; | tail -20
```

### 月度维护（每月）
```bash
# 1. 清理超过30天的旧数据
find data/ -name "*.jsonl" -mtime +30 -delete

# 2. 重启所有服务
pm2 restart all

# 3. 更新依赖包
pip3 list --outdated

# 4. 检查系统资源
free -h
```

---

## 🆘 故障排查流程

### 问题：页面打不开或显示空白

1. **检查Flask服务**
```bash
pm2 status flask-app
pm2 logs flask-app --err --lines 20
```

2. **检查路由是否存在**
```bash
grep -n "页面URL" source_code/app_new.py
```

3. **清除浏览器缓存**
- Windows/Linux: Ctrl + Shift + R
- Mac: Cmd + Shift + R

### 问题：数据不更新

1. **检查对应的PM2服务**
```bash
pm2 list | grep [系统名称]
pm2 logs [系统名称] --lines 50
```

2. **检查数据文件**
```bash
ls -lh data/[系统目录]/*.jsonl
tail -1 data/[系统目录]/[数据文件].jsonl
```

3. **检查API**
```bash
curl -s 'http://localhost:5000/api/[系统API]' | jq
```

4. **重启服务**
```bash
pm2 restart [系统名称]
```

### 问题：PM2服务频繁重启

1. **查看错误日志**
```bash
pm2 logs [系统名称] --err --lines 100
```

2. **检查内存使用**
```bash
pm2 jlist | jq '.[] | {name, mem: (.monit.memory / 1024 / 1024)}'
```

3. **检查是否缺少依赖**
```bash
pip3 list | grep [模块名称]
```

4. **手动运行脚本查看错误**
```bash
python3 source_code/[脚本名称].py
```

---

## 📞 联系与支持

如果遇到无法解决的问题，请：

1. 保存完整的错误日志
2. 记录问题发生的时间和步骤
3. 运行完整健康检查脚本
4. 提供系统状态快照

---

**文档版本**: v1.0  
**最后更新**: 2026-02-01 12:35  
**维护者**: GenSpark AI Developer
