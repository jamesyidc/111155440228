# 系统依赖关系完整矩阵

**生成时间**: 2026-02-01 12:52:00  
**用途**: 快速诊断任何系统问题的完整检查清单

---

## 📊 系统组件依赖矩阵表

| 系统名称 | PM2服务 | 数据文件 | API路由 | 页面路由 | 更新周期 | 健康检查命令 |
|---------|---------|----------|---------|----------|----------|--------------|
| 27币涨跌幅追踪 | coin-change-tracker | data/coin_change_tracker.jsonl | /api/coin-change-tracker/* | /coin-change-tracker | 60秒 | `curl -s localhost:5000/api/coin-change-tracker/history\?limit=1` |
| SAR斜率系统 | sar-jsonl-collector<br>sar-slope-collector | data/sar_jsonl/*.jsonl<br>data/sar_slope_data.jsonl | /api/sar-slope/* | /sar-slope<br>/sar-slope/{symbol} | 300秒(采集)<br>60秒(斜率) | `curl -s localhost:5000/api/sar-slope/list` |
| 逃顶信号系统 | escape-signal-calculator<br>escape-signal-monitor | data/escape_signal_jsonl/escape_signal_stats.jsonl | /api/escape-signal-stats/* | /escape-signal-history | 60秒 | `curl -s localhost:5000/api/escape-signal-stats/keypoints?limit=1` |
| 支撑压力线系统 | support-resistance-collector<br>support-resistance-snapshot | data/support_resistance_daily/*.jsonl | /api/support-resistance/* | /support-resistance | 30秒(采集)<br>300秒(快照) | `curl -s localhost:5000/api/support-resistance/latest` |
| 锚点盈利统计 | anchor-profit-monitor | data/anchor_profit_history.jsonl | /api/anchor-system/* | /anchor-system | 60秒 | `curl -s localhost:5000/api/anchor-system/profit-history` |
| 恐慌清洗指数 | panic-collector | data/panic_index.jsonl | /api/panic/latest<br>/api/panic/index-curve | /panic-index | 60秒 | `curl -s localhost:5000/api/panic/latest` |
| 1小时爆仓金额 | liquidation-1h-collector | data/liquidation_1h.jsonl | /api/panic/hour1-curve | /panic-index | 60秒 | `curl -s localhost:5000/api/panic/hour1-curve` |
| 数据健康监控 | data-health-monitor | data/data_health_monitor_state.json | /api/data-health-monitor/status | /data-health-monitor | 60秒 | `curl -s localhost:5000/api/data-health-monitor/status` |
| OKX交易系统 | (无独立PM2) | data/okx_trading_logs/trading_log_*.jsonl<br>data/okx_trading_jsonl/okx_day_change.jsonl | /api/okx-trading/* | /okx-trading | 按需 | `curl -s localhost:5000/api/okx-trading/logs?limit=1` |
| 重大事件监控 | major-events-monitor | data/major_events/*.jsonl | /api/major-events/* | /major-events | 300秒 | `curl -s localhost:5000/api/major-events/latest` |
| 价格追踪 | coin-price-tracker | (内存缓存) | /api/coin-price/* | - | 实时 | `curl -s localhost:5000/api/coin-price/list` |
| 价格速度采集 | price-speed-collector | data/price_speed/*.jsonl | /api/price-speed/* | - | 60秒 | `ls -lh data/price_speed/ \| tail -5` |
| V1V2指标 | v1v2-collector | data/v1v2/*.jsonl | /api/v1v2/* | - | 300秒 | `ls -lh data/v1v2/ \| tail -5` |
| 加密指数 | crypto-index-collector | data/crypto_index/*.jsonl | /api/crypto-index/* | - | 300秒 | `ls -lh data/crypto_index/ \| tail -5` |

---

## 🔍 系统详细诊断检查清单

### 1️⃣ **27币涨跌幅追踪系统**

#### 必需组件
- **PM2服务**: `coin-change-tracker`
- **数据文件**: `data/coin_change_tracker.jsonl`
- **API端点**: 
  - `/api/coin-change-tracker/history` - 历史数据
  - `/api/coin-change-tracker/latest` - 最新数据
- **页面路由**: `/coin-change-tracker`
- **路由定义位置**: `source_code/app_new.py:5932-6070`

#### 健康检查命令
```bash
# 1. 检查PM2服务状态
pm2 status coin-change-tracker

# 2. 检查数据文件最新时间
tail -1 data/coin_change_tracker.jsonl | jq '{timestamp, data_count: .data | length}'

# 3. 测试API
curl -s 'http://localhost:5000/api/coin-change-tracker/history?limit=1' | jq '{success, data_count: .data | length, latest: .data[0].timestamp}'

# 4. 检查数据时效性（应该<5分钟）
echo "最新数据时间:" && tail -1 data/coin_change_tracker.jsonl | jq -r '.timestamp' && echo "当前时间:" && date -u '+%Y-%m-%d %H:%M:%S'
```

#### 故障排查
| 问题现象 | 可能原因 | 检查命令 | 修复方法 |
|---------|---------|----------|----------|
| API返回空数据 | PM2服务未运行 | `pm2 status coin-change-tracker` | `pm2 restart coin-change-tracker` |
| 数据过期 | 采集器卡死 | `pm2 logs coin-change-tracker --lines 50` | 查看错误日志，重启服务 |
| 页面显示错误 | 数据文件损坏 | `tail -10 data/coin_change_tracker.jsonl \| jq .` | 删除损坏行，重启采集器 |

---

### 2️⃣ **SAR斜率系统**

#### 必需组件
- **PM2服务**: 
  - `sar-jsonl-collector` (原始SAR数据采集)
  - `sar-slope-collector` (斜率计算)
- **数据文件**: 
  - `data/sar_jsonl/*.jsonl` (每个币种一个文件，如 `XRP.jsonl`)
  - `data/sar_slope_data.jsonl` (斜率统计数据)
- **API端点**: 
  - `/api/sar-slope/list` - 所有币种列表
  - `/api/sar-slope/current-cycle/{symbol}` - 单个币种当前序列
  - `/api/sar-slope/statistics` - 统计数据
- **页面路由**: 
  - `/sar-slope` - 主页
  - `/sar-slope/{symbol}` - 详情页
- **路由定义位置**: `source_code/app_new.py:4773-5244`

#### 健康检查命令
```bash
# 1. 检查两个PM2服务状态
pm2 status | grep sar

# 2. 检查原始SAR数据（以XRP为例）
tail -1 data/sar_jsonl/XRP.jsonl | jq '{time, position, sar, price}'

# 3. 检查斜率统计数据
tail -1 data/sar_slope_data.jsonl | jq '{timestamp, total_long, total_short}'

# 4. 测试API
curl -s 'http://localhost:5000/api/sar-slope/list' | jq '{success, data_count: .data | length, sample: .data[0]}'

# 5. 测试单个币种详情
curl -s 'http://localhost:5000/api/sar-slope/current-cycle/XRP?limit=10' | jq '{symbol, current_status, total_sequences}'
```

#### 故障排查
| 问题现象 | 可能原因 | 检查命令 | 修复方法 |
|---------|---------|----------|----------|
| 详情页显示undefined | 原始SAR数据未更新 | `tail -1 data/sar_jsonl/XRP.jsonl` | 检查`sar-jsonl-collector`日志和okx依赖 |
| 主页数据过期 | 斜率采集器未运行 | `pm2 logs sar-slope-collector --lines 30` | 重启`sar-slope-collector` |
| 缺少币种数据 | JSONL文件不存在 | `ls -lh data/sar_jsonl/ \| wc -l` | 等待首次采集或手动触发 |
| OKX API错误 | okx模块版本问题 | `python3 -c "from okx import api; print('OK')"` | `pip3 install --upgrade okx` |

#### 依赖关系
```
sar-jsonl-collector (每5分钟)
    ↓ 采集OKX K线数据
    ↓ 计算SAR值
    ↓ 写入 data/sar_jsonl/*.jsonl
    ↓
sar-slope-collector (每60秒)
    ↓ 读取所有币种SAR数据
    ↓ 计算斜率和序列
    ↓ 写入 data/sar_slope_data.jsonl
    ↓
Flask API (/api/sar-slope/*)
    ↓ 读取JSONL数据
    ↓ 返回给前端
```

---

### 3️⃣ **逃顶信号系统**

#### 必需组件
- **PM2服务**: 
  - `escape-signal-calculator` (信号计算)
  - `escape-signal-monitor` (预警监控)
- **数据文件**: 
  - `data/escape_signal_jsonl/escape_signal_stats.jsonl`
- **API端点**: 
  - `/api/escape-signal-stats/keypoints` - 关键点数据（用于图表）
  - `/api/escape-signal-stats/keypoints-monthly` - 月度统计
  - `/api/escape-signal-stats` - 完整历史（分页）
- **页面路由**: `/escape-signal-history`
- **路由定义位置**: `source_code/app_new.py:6256-6797`

#### 健康检查命令
```bash
# 1. 检查PM2服务
pm2 status | grep escape

# 2. 检查最新数据
tail -1 data/escape_signal_jsonl/escape_signal_stats.jsonl | jq '{stat_time, signal_2h_count, signal_24h_count}'

# 3. 测试关键点API（图表用）
curl -s 'http://localhost:5000/api/escape-signal-stats/keypoints?limit=5' | jq '{success, keypoint_count, data_range, latest: .keypoints[0]}'

# 4. 测试历史API（页面用）
curl -s 'http://localhost:5000/api/escape-signal-stats?limit=3' | jq '{success, total_count, latest_3: .history_data[0:3] | [.[] | {stat_time, signal_2h_count, signal_24h_count}]}'

# 5. 检查逃顶条件（sum >= 8 且两者都 >= 1）
tail -1 data/escape_signal_jsonl/escape_signal_stats.jsonl | jq '{stat_time, signal_2h_count, signal_24h_count, sum: (.signal_2h_count + .signal_24h_count), meets_criteria: ((.signal_2h_count + .signal_24h_count) >= 8 and .signal_2h_count >= 1 and .signal_24h_count >= 1)}'
```

#### 故障排查
| 问题现象 | 可能原因 | 检查命令 | 修复方法 |
|---------|---------|----------|----------|
| 页面显示旧数据 | API返回顺序错误 | `curl -s 'localhost:5000/api/escape-signal-stats?limit=3' \| jq '.history_data[0:3] \| .[].stat_time'` | 确保API返回倒序（最新在前） |
| 数据停止更新 | calculator服务停止 | `pm2 status escape-signal-calculator` | `pm2 restart escape-signal-calculator` |
| API缓存未失效 | TTL=60秒缓存 | 等待60秒或重启Flask | `pm2 restart flask-app` |

---

### 4️⃣ **支撑压力线系统**

#### 必需组件
- **PM2服务**: 
  - `support-resistance-collector` (实时数据采集)
  - `support-resistance-snapshot` (每日快照)
- **数据文件**: 
  - `data/support_resistance_daily/*.jsonl` (每日一个文件)
- **API端点**: 
  - `/api/support-resistance/latest` - 最新数据
  - `/api/support-resistance/snapshots` - 历史快照
  - `/api/support-resistance/signals-computed` - 信号统计
- **页面路由**: `/support-resistance`
- **路由定义位置**: `source_code/app_new.py:7612-7878`

#### 健康检查命令
```bash
# 1. 检查PM2服务
pm2 status | grep support

# 2. 检查最新数据文件
ls -lth data/support_resistance_daily/ | head -5

# 3. 检查最新数据内容
tail -1 data/support_resistance_daily/$(ls -t data/support_resistance_daily/ | head -1) | jq '{timestamp, type, symbols_count: .symbols | length}'

# 4. 测试最新数据API
curl -s 'http://localhost:5000/api/support-resistance/latest' | jq '{success, data_count: .data | length, sample: .data[0] | {symbol, current_price, support_1, resistance_1}}'

# 5. 测试信号统计API
curl -s 'http://localhost:5000/api/support-resistance/signals-computed' | jq '{success, latest_buy: .buy_signals_24h[0], latest_sell: .sell_signals_24h[0]}'

# 6. 检查预警币种
curl -s 'http://localhost:5000/api/support-resistance/latest' | jq '[.data[] | select(.alert_48h_low == true or .alert_48h_high == true or .alert_7d_low == true or .alert_7d_high == true)]'
```

#### 故障排查
| 问题现象 | 可能原因 | 检查命令 | 修复方法 |
|---------|---------|----------|----------|
| 页面空白（多空盈亏区域） | 当前无预警币种（正常） | 检查`alert_*`字段 | 这是正常业务逻辑 |
| 数据未更新 | collector服务停止 | `pm2 logs support-resistance-collector --lines 30` | 重启服务 |
| API返回空 | 数据文件缺失 | `ls -lh data/support_resistance_daily/` | 等待首次采集 |

---

### 5️⃣ **锚点盈利统计系统**

#### 必需组件
- **PM2服务**: `anchor-profit-monitor`
- **数据文件**: `data/anchor_profit_history.jsonl`
- **API端点**: `/api/anchor-system/profit-history`
- **页面路由**: `/anchor-system`
- **路由定义位置**: `source_code/app_new.py:5560-5687`

#### 健康检查命令
```bash
# 1. 检查PM2服务
pm2 status anchor-profit-monitor

# 2. 检查数据文件
tail -1 data/anchor_profit_history.jsonl | jq '{datetime, long_profit_rate, short_profit_rate}'

# 3. 测试API
curl -s 'http://localhost:5000/api/anchor-system/profit-history' | jq '{success, history_count: .history | length, latest: .history[0]}'
```

---

### 6️⃣ **恐慌清洗指数系统**

#### 必需组件
- **PM2服务**: `panic-collector`
- **数据文件**: `data/panic_index.jsonl`
- **API端点**: 
  - `/api/panic/latest` - 最新指数
  - `/api/panic/index-curve` - 历史曲线
- **页面路由**: `/panic-index`
- **路由定义位置**: `source_code/app_new.py:5297-5429`

#### 健康检查命令
```bash
# 1. 检查PM2服务
pm2 status panic-collector

# 2. 检查数据文件
tail -1 data/panic_index.jsonl | jq '{record_time, panic_index, long_profit_count, short_profit_count}'

# 3. 测试API
curl -s 'http://localhost:5000/api/panic/latest' | jq '{success, data}'
```

---

### 7️⃣ **1小时爆仓金额系统**

#### 必需组件
- **PM2服务**: `liquidation-1h-collector`
- **数据文件**: `data/liquidation_1h.jsonl`
- **API端点**: `/api/panic/hour1-curve`
- **路由定义位置**: `source_code/app_new.py:5432-5557`

#### 健康检查命令
```bash
# 1. 检查PM2服务
pm2 status liquidation-1h-collector

# 2. 检查数据文件
tail -1 data/liquidation_1h.jsonl | jq '{datetime, liquidation_1h}'

# 3. 测试API
curl -s 'http://localhost:5000/api/panic/hour1-curve' | jq '{success, data_count: .data | length, latest: .data[0]}'
```

---

### 8️⃣ **数据健康监控系统**

#### 必需组件
- **PM2服务**: `data-health-monitor`
- **数据文件**: `data/data_health_monitor_state.json`
- **API端点**: `/api/data-health-monitor/status`
- **页面路由**: `/data-health-monitor`
- **路由定义位置**: `source_code/app_new.py:7913-7998`
- **监控配置**: `source_code/data_health_monitor.py`

#### 健康检查命令
```bash
# 1. 检查PM2服务
pm2 status data-health-monitor

# 2. 查看监控状态文件
cat data/data_health_monitor_state.json | jq '.'

# 3. 测试API
curl -s 'http://localhost:5000/api/data-health-monitor/status' | jq '{stats, monitors: .monitors | [.[] | {name, status, delay_minutes}]}'

# 4. 查看最近重启记录
curl -s 'http://localhost:5000/api/data-health-monitor/status' | jq '.monitors | [.[] | select(.pm2_restarts > 0)] | sort_by(.pm2_restarts) | reverse'
```

#### 监控的系统列表
```python
MONITORS = {
    '27币涨跌幅追踪': {...},
    '1小时爆仓金额': {...},
    '恐慌清洗指数': {...},
    '锚点盈利统计': {...},
    '逃顶信号统计': {...},
    '支撑压力线系统': {...}
}
```

---

### 9️⃣ **OKX交易系统**

#### 必需组件
- **PM2服务**: 无（通过Flask直接调用OKX API）
- **数据文件**: 
  - `data/okx_trading_logs/trading_log_YYYYMMDD.jsonl` (交易日志)
  - `data/okx_trading_jsonl/okx_day_change.jsonl` (24小时涨跌幅，可选)
- **API端点**: 
  - `/api/okx-trading/account-info` - 账户信息
  - `/api/okx-trading/account-balance` - 账户余额
  - `/api/okx-trading/positions` - 持仓列表
  - `/api/okx-trading/place-order` - 下单
  - `/api/okx-trading/pending-orders` - 未成交订单
  - `/api/okx-trading/cancel-order` - 撤单
  - `/api/okx-trading/close-position` - 平仓
  - `/api/okx-trading/market-tickers` - 市场行情
  - `/api/okx-trading/logs` - 交易日志
  - `/api/okx-trading/favorite-symbols` - 收藏币种
- **页面路由**: `/okx-trading`
- **路由定义位置**: `source_code/app_new.py:13660-17888`

#### 健康检查命令
```bash
# 1. 检查交易日志文件
ls -lh data/okx_trading_logs/ | tail -5

# 2. 查看最新交易日志
TODAY=$(date +%Y%m%d)
tail -1 data/okx_trading_logs/trading_log_${TODAY}.jsonl 2>/dev/null | jq '.' || echo "今日无交易记录"

# 3. 测试日志API
curl -s 'http://localhost:5000/api/okx-trading/logs?limit=5' | jq '{success, data_count: .data | length, latest: .data[0]}'

# 4. 测试收藏币种API
curl -s 'http://localhost:5000/api/okx-trading/favorite-symbols' | jq '{success, symbols_count: .symbols | length}'

# 5. 测试市场行情API
curl -s 'http://localhost:5000/api/okx-trading/market-tickers' | jq '{success, tickers_count: .data | length, sample: .data[0]}' | head -20
```

#### 特殊说明
- OKX交易系统**不依赖PM2服务**，直接通过Flask调用OKX API
- 需要用户在页面配置 **API Key、API Secret、Passphrase**
- 交易日志按日期分文件存储：`trading_log_YYYYMMDD.jsonl`
- `okx-day-change-collector` (PM2 id=6) 已停用，用于采集24小时涨跌幅（可选功能）

#### 故障排查
| 问题现象 | 可能原因 | 检查命令 | 修复方法 |
|---------|---------|----------|----------|
| API返回认证错误 | API密钥未配置或错误 | 页面检查API配置 | 重新输入正确的API密钥 |
| 日志API返回空 | 今日无交易记录（正常） | 检查历史日期文件 | 这是正常现象 |
| 市场行情API失败 | OKX API限流或网络问题 | `curl https://www.okx.com/api/v5/public/time` | 等待或检查网络 |

---

### 🔟 **重大事件监控系统**

#### 必需组件
- **PM2服务**: `major-events-monitor`
- **数据文件**: `data/major_events/*.jsonl` (按日期分文件)
- **API端点**: 
  - `/api/major-events/latest` - 最新事件
  - `/api/major-events/history` - 历史事件
- **页面路由**: `/major-events`
- **路由定义位置**: `source_code/app_new.py:8001-8157`

#### 健康检查命令
```bash
# 1. 检查PM2服务
pm2 status major-events-monitor

# 2. 查看最新事件文件
ls -lth data/major_events/ | head -5

# 3. 测试API
curl -s 'http://localhost:5000/api/major-events/latest' | jq '{success, events_count: .events | length, latest: .events[0]}'
```

---

## 🚨 完整系统健康检查脚本

### 快速诊断所有系统
```bash
#!/bin/bash
cd /home/user/webapp

echo "======================================"
echo "系统完整健康检查报告"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "======================================"
echo ""

# 1. PM2服务总览
echo "【1】PM2服务状态"
pm2 status | grep -E "online|stopped|errored"
echo ""

# 2. Flask服务
echo "【2】Flask服务"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" http://localhost:5000/
echo ""

# 3. 数据健康监控
echo "【3】数据健康监控"
curl -s 'http://localhost:5000/api/data-health-monitor/status' | jq '{stats, unhealthy_systems: [.monitors[] | select(.status != "healthy") | .name]}'
echo ""

# 4. 关键系统数据时效性
echo "【4】关键系统数据时效性"
echo "27币涨跌幅:"
tail -1 data/coin_change_tracker.jsonl 2>/dev/null | jq -r '.timestamp' || echo "文件不存在"

echo "SAR斜率:"
tail -1 data/sar_slope_data.jsonl 2>/dev/null | jq -r '.timestamp' || echo "文件不存在"

echo "逃顶信号:"
tail -1 data/escape_signal_jsonl/escape_signal_stats.jsonl 2>/dev/null | jq -r '.stat_time' || echo "文件不存在"

echo "支撑压力线:"
ls -t data/support_resistance_daily/*.jsonl 2>/dev/null | head -1 | xargs tail -1 | jq -r '.timestamp' || echo "文件不存在"

echo "锚点盈利:"
tail -1 data/anchor_profit_history.jsonl 2>/dev/null | jq -r '.datetime' || echo "文件不存在"

echo "恐慌指数:"
tail -1 data/panic_index.jsonl 2>/dev/null | jq -r '.record_time' || echo "文件不存在"
echo ""

# 5. 磁盘空间
echo "【5】磁盘空间"
df -h / | grep -v Filesystem
du -sh data/
echo ""

# 6. SAR系统专项检查
echo "【6】SAR系统专项检查"
echo "SAR JSONL文件数量: $(ls data/sar_jsonl/*.jsonl 2>/dev/null | wc -l)"
echo "XRP最新SAR数据:"
tail -1 data/sar_jsonl/XRP.jsonl 2>/dev/null | jq '{time, position, sar}' || echo "XRP数据不存在"
echo ""

# 7. 错误的PM2服务
echo "【7】异常PM2服务"
pm2 status | grep -E "stopped|errored" || echo "所有服务正常"
echo ""

echo "======================================"
echo "检查完成"
echo "======================================"
```

保存为 `/home/user/webapp/scripts/quick_health_check.sh` 并运行：
```bash
chmod +x /home/user/webapp/scripts/quick_health_check.sh
./scripts/quick_health_check.sh
```

---

## 📋 系统问题排查决策树

```
系统出现问题
    ↓
1. 页面显示错误？
    ├─ 是 → 检查Flask服务是否运行
    │         ├─ 未运行 → pm2 restart flask-app
    │         └─ 运行中 → 检查浏览器控制台错误
    │                      ├─ API 404 → 检查路由定义
    │                      ├─ API 500 → 检查Flask日志
    │                      └─ 数据undefined → 检查API返回格式
    └─ 否 ↓

2. API返回空数据或错误？
    ├─ 是 → 检查对应PM2服务
    │         ├─ 未运行 → pm2 restart [service-name]
    │         ├─ 运行但报错 → pm2 logs [service-name]
    │         │                ├─ Python依赖错误 → pip3 install [module]
    │         │                ├─ 文件权限错误 → chmod/chown
    │         │                └─ 外部API错误 → 检查网络或API限流
    │         └─ 运行正常 → 检查数据文件
    └─ 否 ↓

3. 数据文件问题？
    ├─ 文件不存在 → 等待首次采集或手动触发
    ├─ 文件为空 → 检查PM2服务日志
    ├─ 数据过期 → 检查PM2服务是否正常运行
    └─ 数据格式错误 → 删除损坏行，重启服务
        ↓

4. 所有检查都正常但页面仍有问题？
    ├─ 清除浏览器缓存（Ctrl+Shift+R）
    ├─ 检查API缓存（等待TTL过期或重启Flask）
    └─ 查看数据健康监控页面寻找线索
```

---

## 🔧 常用维护命令速查

### PM2管理
```bash
# 查看所有服务状态
pm2 status

# 重启单个服务
pm2 restart [service-name]

# 查看服务日志（最近50行）
pm2 logs [service-name] --lines 50 --nostream

# 清空服务日志
pm2 flush [service-name]

# 保存PM2配置
pm2 save

# 查看服务详细信息
pm2 show [service-name]
```

### 数据文件管理
```bash
# 查看所有数据文件大小
du -sh data/*

# 查看最新的数据文件
find data -name "*.jsonl" -type f -exec ls -lth {} + | head -20

# 检查数据文件是否有效JSON
tail -10 data/[file].jsonl | jq . > /dev/null && echo "JSON有效" || echo "JSON无效"

# 清理30天前的旧数据（谨慎使用）
find data -name "*.jsonl" -type f -mtime +30 -delete
```

### Flask管理
```bash
# 重启Flask
pm2 restart flask-app

# 查看Flask日志
pm2 logs flask-app --lines 100 --nostream

# 测试Flask是否响应
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5000/
```

### Git操作
```bash
# 查看未提交的修改
git status

# 查看最近的提交
git log --oneline -10

# 提交所有修改
git add .
git commit -m "描述信息"
```

---

## 📊 系统性能基准值

| 指标 | 正常范围 | 警告阈值 | 说明 |
|------|---------|---------|------|
| 数据延迟 | < 2分钟 | > 5分钟 | 最新数据时间与当前时间差 |
| PM2重启次数 | < 5次/天 | > 10次/天 | 频繁重启说明服务不稳定 |
| Flask内存 | < 1GB | > 2GB | Flask应用内存占用 |
| 采集器内存 | < 50MB | > 100MB | 单个数据采集器内存 |
| 磁盘使用率 | < 70% | > 85% | 根分区磁盘使用率 |
| API响应时间 | < 500ms | > 2000ms | API接口响应时间 |
| JSONL文件大小 | 视情况 | 单文件>500MB | 考虑数据轮转 |

---

## 🎯 关键依赖关系图

```
                    Flask应用 (flask-app)
                           |
        +------------------+------------------+
        |                  |                  |
   数据文件层          PM2服务层          API路由层
        |                  |                  |
    data/              coin-change-        /api/*
    ├─ coin_change_    tracker             ├─ coin-change-tracker/*
    ├─ sar_jsonl/      sar-jsonl-          ├─ sar-slope/*
    ├─ sar_slope_      collector           ├─ escape-signal-stats/*
    ├─ escape_signal_  sar-slope-          ├─ support-resistance/*
    ├─ support_        collector           ├─ anchor-system/*
    │  resistance_     escape-signal-      ├─ panic/*
    ├─ anchor_         calculator          ├─ data-health-monitor/*
    ├─ panic_index     escape-signal-      ├─ okx-trading/*
    ├─ liquidation_    monitor             └─ major-events/*
    ├─ okx_trading_    support-
    └─ major_events/   resistance-
                       collector
                       support-
                       resistance-
                       snapshot
                       anchor-profit-
                       monitor
                       panic-collector
                       liquidation-1h-
                       collector
                       data-health-
                       monitor
                       major-events-
                       monitor
```

---

## ✅ 总结

### 关键要点
1. **每个系统的健康依赖于4个层面**：
   - PM2服务正常运行
   - 数据文件及时更新
   - API路由正确返回
   - 页面正确渲染

2. **数据健康监控是中枢**：
   - 监控6个核心系统
   - 自动检测数据时效性
   - 自动重启异常服务
   - 发送Telegram告警

3. **优先检查顺序**：
   - Flask服务 → PM2服务 → 数据文件 → API → 页面

4. **常见问题90%原因**：
   - PM2服务停止或错误
   - Python依赖缺失或版本不兼容
   - 数据文件损坏或权限问题
   - 外部API限流或网络问题

### 维护建议
- 每天运行一次完整健康检查脚本
- 关注数据健康监控页面的告警
- 定期清理30天以上的旧数据
- PM2重启次数异常时优先排查
- 磁盘使用率超过80%时清理日志

---

**文档版本**: v1.0  
**最后更新**: 2026-02-01 12:52:00  
**维护者**: GenSpark AI Developer
