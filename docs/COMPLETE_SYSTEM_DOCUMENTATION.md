# 🎯 Complete System Documentation

## 完成时间
**2026-02-02 09:15** (北京时间)

---

## 📊 一、PM2运行的服务列表

### 1.1 核心服务 (22个在线 + 1个停止)

| ID | 服务名 | 状态 | PID | 运行时间 | CPU | 内存 | 说明 |
|----|--------|------|-----|----------|-----|------|------|
| **11** | **flask-app** | ✅ online | 1209973 | 7分钟 | 100% | 389.9 MB | **主Flask应用** |
| **18** | **escape-signal-calculator** | ✅ online | 671242 | 23小时 | 100% | 639.8 MB | 逃顶信号计算器 |
| 9 | anchor-profit-monitor | ✅ online | 657141 | 24小时 | 0% | 30.5 MB | 锚点盈利监控 |
| 14 | coin-change-tracker | ✅ online | 656920 | 24小时 | 0% | 30.5 MB | 币种涨跌追踪 |
| 1 | coin-price-tracker | ✅ online | 1205019 | 17分钟 | 0% | 30.4 MB | 币价追踪器 |
| 5 | crypto-index-collector | ✅ online | 1562 | 5天 | 0% | 31.4 MB | 加密指数采集 |
| 16 | data-health-monitor | ✅ online | 920866 | 12小时 | 0% | 40.9 MB | 数据健康监控 |
| 10 | escape-signal-monitor | ✅ online | 1567 | 5天 | 0% | 34.7 MB | 逃顶信号监控 |
| 23 | extreme-monitor-jsonl | ✅ online | 957921 | 10小时 | 0% | 30.8 MB | 极值监控(JSONL) |
| 20 | gdrive-detector | ✅ online | 865860 | 14小时 | 0% | 50.6 MB | Google Drive检测 |
| 8 | liquidation-1h-collector | ✅ online | 1565 | 5天 | 0% | 28.9 MB | 1小时爆仓采集 |
| 15 | major-events-monitor | ✅ online | 423165 | 2天 | 0% | 166.6 MB | 重大事件监控 |
| 13 | panic-collector | ✅ online | 769427 | 18小时 | 0% | 29.3 MB | 恐慌指数采集 |
| 3 | price-speed-collector | ✅ online | 1560 | 5天 | 0% | 30.1 MB | 价格速度采集 |
| 21 | sar-1min-collector | ✅ online | 751179 | 18小时 | 0% | 80.1 MB | SAR 1分钟采集 |
| 22 | sar-bias-stats-collector | ✅ online | 763950 | 18小时 | 0% | 32.0 MB | SAR偏离统计 |
| 17 | sar-jsonl-collector | ✅ online | 794189 | 17小时 | 0% | 85.6 MB | SAR JSONL采集 |
| 7 | sar-slope-collector | ✅ online | 1564 | 5天 | 0% | 29.4 MB | SAR斜率采集 |
| 12 | support-resistance-collector | ✅ online | 668835 | 23小时 | 0% | 31.3 MB | 支撑阻力采集 |
| 2 | support-resistance-snapshot | ✅ online | 18316 | 5天 | 0% | 98.4 MB | 支撑阻力快照 |
| 4 | v1v2-collector | ✅ online | 1561 | 5天 | 0% | 30.1 MB | V1V2数据采集 |
| **6** | **okx-day-change-collector** | ❌ **stopped** | 0 | 0 | 0% | 0 MB | OKX日涨跌采集 |

**总资源使用**：
- CPU: ~200% (主要是 flask-app 和 escape-signal-calculator)
- 内存: ~1.7 GB

---

## 📡 二、Flask API路由列表

### 2.1 主页和基础页面 (16个)

| 路由 | 页面名称 | 说明 |
|------|----------|------|
| `/` | 首页 | 系统首页 |
| `/query` | 查询页面 | 数据查询 |
| `/chart` | 图表页面 | 数据图表 |
| `/timeline` | 时间线 | 历史时间线 |
| `/status` | 状态页面 | 系统状态 |
| `/panic` | 恐慌指数 | 恐慌清洗指数 |
| `/extreme-tracking` | 极值追踪 | 极值追踪页面 |
| `/coin-change-tracker` | 币种涨跌 | 币种涨跌追踪 |
| `/monitor` | 监控页面 | 数据监控 |
| `/crypto-index` | 加密指数 | OKEx加密指数 |
| `/gdrive-detector` | GDrive检测 | Google Drive检测 |
| `/coin-price-tracker` | 币价追踪 | 币价追踪器 |
| `/system-status` | 系统状态 | 系统状态概览 |
| `/data-health-monitor` | 健康监控 | 数据健康监控 |
| `/okx-trading` | **OKX交易** | **OKX交易页面** ⭐ |
| `/anchor-system-real` | **锚点系统(实盘)** | **实盘锚点系统** ⭐ |

### 2.2 恐慌指数相关API (6个)

| API路由 | 方法 | 说明 |
|---------|------|------|
| `/api/panic/latest` | GET | 最新恐慌指数 |
| `/api/panic/hour1-curve` | GET | 1小时曲线 |
| `/api/panic/history` | GET | 历史数据 |
| `/api/panic/30d-stats` | GET | 30天统计 |
| `/api/fear-greed/latest` | GET | 恐惧贪婪指数 |
| `/api/fear-greed/history` | GET | 恐惧贪婪历史 |

### 2.3 OKX交易相关API (15个)

| API路由 | 方法 | 说明 |
|---------|------|------|
| `/api/okx-trading/account-balance` | POST | 查询账户余额 |
| `/api/okx-trading/account-info` | POST | 查询账户信息 |
| `/api/okx-trading/positions` | POST | 查询持仓 |
| `/api/okx-trading/place-order` | POST | **下单(开仓)** ⭐ |
| `/api/okx-trading/close-position` | POST | **平仓** ⭐ |
| `/api/okx-trading/pending-orders` | POST | 查询委托 |
| `/api/okx-trading/cancel-order` | POST | 撤销委托 |
| `/api/okx-trading/order-detail` | POST | 订单详情 |
| `/api/okx-trading/set-tpsl` | POST | 设置止盈止损 |
| `/api/okx-trading/market-tickers` | GET | 市场行情 |
| `/api/okx-trading/logs` | GET | 交易日志 |
| `/api/okx-trading/favorite-symbols` | GET/POST | 收藏币种 |
| `/api/okx-trading/batch-order` | POST | 批量下单 |
| `/api/okx-trading/hedge-order` | POST | 对冲下单 |
| `/api/sub-account/close-position` | POST | **子账户平仓** ⭐ |

### 2.4 锚点系统相关API (12个)

| API路由 | 方法 | 说明 |
|---------|------|------|
| `/api/anchor-system/monitors` | GET | 监控列表 |
| `/api/anchor-system/alerts` | GET | 预警列表 |
| `/api/anchor-system/status` | GET | 系统状态 |
| `/api/anchor-system/profit-records` | GET | 盈利记录 |
| `/api/anchor-system/profit-records-with-coins` | GET | **盈利记录(含币种)** ⭐ |
| `/api/anchor-system/cleanup-extremes` | POST | 清理极值 |
| `/api/anchor-system/extreme-stats` | GET | 极值统计 |
| `/api/anchor-system/correction-log` | GET | 纠错日志 |
| `/api/anchor-system/current-positions` | GET | 当前持仓 |
| `/api/anchor-system/extreme-values` | GET | 极值数据 |
| `/api/anchor-system/warnings` | GET | 预警信息 |
| `/api/anchor-system/sub-account-positions` | GET | 子账户持仓 |

### 2.5 币种追踪相关API (4个)

| API路由 | 方法 | 说明 |
|---------|------|------|
| `/api/coin-change-tracker/latest` | GET | 最新涨跌 |
| `/api/coin-change-tracker/history` | GET | 历史涨跌 |
| `/api/coin-change-tracker/baseline` | GET | 基准价格 |
| `/api/coin-change-tracker/reset-baseline` | POST | 重置基准 |

### 2.6 数据健康监控API (4个)

| API路由 | 方法 | 说明 |
|---------|------|------|
| `/api/data-health-monitor/status` | GET | 健康状态 |
| `/api/data-health-monitor/logs` | GET | 监控日志 |
| `/api/data-health-monitor/restart` | POST | 重启服务 |
| `/api/data-health-monitor/service-logs` | GET | 服务日志 |

### 2.7 其他重要API (15+个)

| API路由 | 方法 | 说明 |
|---------|------|------|
| `/api/stats` | GET | 统计数据 |
| `/api/homepage/summary` | GET | 首页摘要 |
| `/api/query` | GET | 查询数据 |
| `/api/chart` | GET | 图表数据 |
| `/api/timeline` | GET | 时间线数据 |
| `/api/liquidation-1h/latest` | GET | 1小时爆仓 |
| `/api/gdrive-detector/status` | GET | GDrive状态 |
| `/api/v1v2/latest` | GET | V1V2最新 |
| `/api/price-speed/latest` | GET | 价格速度 |
| `/api/major-events/current-status` | GET | 重大事件状态 |
| `/api/extreme-tracking/snapshots` | GET | 极值快照 |
| `/api/service-health` | GET | 服务健康 |
| `/api/collectors/status` | GET | 采集器状态 |
| `/api/modules/stats` | GET | 模块统计 |
| ... | ... | ... |

**总API数量**：~100+ 个

---

## 📁 三、核心文件结构

### 3.1 主应用文件

```
/home/user/webapp/
├── source_code/
│   ├── app_new.py                          # 主Flask应用 (19,600+ 行)
│   ├── app.py                              # 旧版Flask应用 (已废弃)
│   └── templates/
│       ├── anchor_system_real.html         # 实盘锚点系统页面
│       ├── okx_trading.html                # OKX交易页面
│       ├── anchor_system.html              # 锚点系统通用页面
│       ├── anchor_system_paper.html        # 模拟盘锚点系统
│       ├── coin_change_tracker.html        # 币种涨跌追踪
│       └── ... (其他30+个HTML模板)
```

### 3.2 数据采集脚本

```
├── source_code/
│   ├── anchor_profit_monitor.py            # 锚点盈利监控
│   ├── coin_change_tracker.py              # 币种涨跌追踪
│   ├── coin_price_tracker.py               # 币价追踪器
│   ├── crypto_index_collector.py           # 加密指数采集
│   ├── data_health_monitor.py              # 数据健康监控
│   ├── escape_signal_calculator.py         # 逃顶信号计算
│   ├── escape_signal_monitor.py            # 逃顶信号监控
│   ├── extreme_monitor_jsonl.py            # 极值监控(JSONL)
│   ├── gdrive_detector_jsonl.py            # GDrive检测(JSONL)
│   ├── liquidation_1h_collector.py         # 1小时爆仓采集
│   ├── major_events_monitor.py             # 重大事件监控
│   ├── panic_collector_jsonl.py            # 恐慌指数采集
│   ├── price_speed_collector.py            # 价格速度采集
│   ├── sar_1min_collector.py               # SAR 1分钟采集
│   ├── sar_bias_stats_collector.py         # SAR偏离统计
│   ├── sar_jsonl_collector.py              # SAR JSONL采集
│   ├── sar_slope_collector.py              # SAR斜率采集
│   ├── support_resistance_collector.py     # 支撑阻力采集
│   ├── support_resistance_snapshot.py      # 支撑阻力快照
│   └── v1v2_collector.py                   # V1V2数据采集
```

### 3.3 数据管理器 (JSONL)

```
├── anchor_jsonl_manager.py                 # 锚点数据管理
├── crypto_index_jsonl_manager.py           # 加密指数管理
├── escape_signal_jsonl_manager.py          # 逃顶信号管理
├── extreme_jsonl_manager.py                # 极值数据管理
├── panic_jsonl_manager.py                  # 恐慌指数管理
├── query_jsonl_manager.py                  # 查询数据管理
├── sar_jsonl_manager.py                    # SAR数据管理
└── price_speed_jsonl_manager.py            # 价格速度管理
```

### 3.4 配置文件

```
├── configs/
│   ├── okx_api_config.json                 # OKX API配置 ⭐
│   ├── telegram_config.json                # Telegram配置
│   ├── trading_config.json                 # 交易配置
│   ├── anchor_config.json                  # 锚点配置
│   ├── v1v2_settings.json                  # V1V2设置
│   ├── daily_folder_config.json            # 日期文件夹配置
│   └── fund_monitor_config.json            # 资金监控配置
```

### 3.5 数据目录

```
├── data/
│   ├── anchor_daily/                       # 锚点日数据
│   ├── baseline_prices/                    # 基准价格
│   ├── coin_change_tracker/                # 币种涨跌数据
│   ├── coin_price_tracker/                 # 币价数据
│   ├── escape_signal_daily/                # 逃顶信号日数据
│   ├── extreme_jsonl/                      # 极值JSONL数据
│   ├── panic_jsonl/                        # 恐慌指数JSONL
│   ├── sar_jsonl/                          # SAR JSONL数据
│   ├── support_resistance_jsonl/           # 支撑阻力JSONL
│   └── tpsl_strategy_config.json           # 止盈止损策略
```

---

## 🎯 四、主要功能模块

### 4.1 OKX交易模块 ⭐

**页面**：`/okx-trading`

**核心功能**：
- ✅ 账户管理（余额、持仓查询）
- ✅ 开仓（市价/限价、杠杆设置）
- ✅ 平仓（全部/部分、批量平仓）
- ✅ 止盈止损设置
- ✅ 委托管理（查询、撤销）
- ✅ 交易日志

**最近修复**：
- ✅ 修复账户持仓模式检测（单向/双向）
- ✅ 修复平仓接口的 posSide 参数错误
- ✅ 新增子账户平仓接口

### 4.2 锚点系统(实盘) ⭐

**页面**：`/anchor-system-real`

**核心功能**：
- ✅ 实时持仓监控
- ✅ 盈利记录追踪
- ✅ 历史极值记录（每条4行显示）
- ✅ 子账户持仓管理
- ✅ 预警系统
- ✅ 自动维护

**最近修复**：
- ✅ 极值记录表格改为横向显示（每条4行）
- ✅ 新增最后更新时间显示
- ✅ 启动极值监控服务（3分钟采集）
- ✅ 加入数据健康监控

### 4.3 数据采集系统

**22个采集器**（21个在线 + 1个停止）

**采集频率**：
- 极值监控：3分钟
- 币价追踪：实时
- SAR数据：1分钟
- 恐慌指数：定期
- 支撑阻力：实时
- ... 等

**数据存储**：JSONL格式，按日期分区

### 4.4 数据健康监控

**页面**：`/data-health-monitor`

**监控项目**：
- ✅ 所有22个数据采集器
- ✅ 数据新鲜度检测
- ✅ 自动重启失败服务
- ✅ Telegram通知
- ✅ 历史日志记录

### 4.5 币种涨跌追踪

**页面**：`/coin-change-tracker`

**功能**：
- ✅ 27个币种实时追踪
- ✅ 涨跌幅度计算
- ✅ 基准价格管理
- ✅ 历史数据查询

---

## 🔧 五、系统配置

### 5.1 OKX API配置

**文件**：`configs/okx_api_config.json`

```json
{
  "api_key": "YOUR_API_KEY",
  "secret_key": "YOUR_SECRET_KEY",
  "passphrase": "YOUR_PASSPHRASE",
  "base_url": "https://www.okx.com",
  "trade_mode": "real"
}
```

**权限要求**：
- ✅ 交易权限
- ✅ 读取权限
- ❌ 提币权限（不需要）

### 5.2 账户模式

**必须设置**：
- 账户模式：单币种保证金 或 跨币种保证金
- 持仓模式：单向持仓 或 双向持仓（自动检测）

### 5.3 PM2配置

**查看配置**：
```bash
pm2 list
pm2 logs flask-app
pm2 restart flask-app
```

**自动启动**：
```bash
pm2 startup
pm2 save
```

---

## 📊 六、数据流图

```
Windows客户端
    ↓
Google Drive (每5分钟)
    ↓
gdrive-detector (检测新文件)
    ↓
各数据采集器 (处理并存储)
    ↓
JSONL文件 (按日期分区)
    ↓
Flask API (提供数据)
    ↓
前端页面 (展示数据)
```

---

## 🚀 七、使用指南

### 7.1 开仓流程

1. 访问：https://5000-...sandbox.../okx-trading
2. 选择币种
3. 设置价格类型（市价/限价）
4. 设置杠杆倍数
5. 输入金额
6. 点击"做多"或"做空"
7. 确认开仓

### 7.2 平仓流程

**方法1：批量平仓**
1. 在OKX交易页面
2. 点击批量平仓按钮（平一半多单/平全部空单等）
3. 确认操作

**方法2：单个平仓**
1. 在锚点系统页面：/anchor-system-real
2. 找到持仓列表
3. 点击"🚨 平仓"按钮
4. 选择平仓比例（输入 7 = 全部平仓）
5. 确认操作

### 7.3 查看数据

- **首页**：/ （系统概览）
- **恐慌指数**：/panic
- **币种涨跌**：/coin-change-tracker
- **数据健康**：/data-health-monitor
- **系统状态**：/system-status

---

## ⚠️ 八、注意事项

### 8.1 安全提示

1. **API密钥安全**：
   - ❌ 不要泄露
   - ❌ 不要开启提币权限
   - ✅ 定期更换
   - ✅ 设置IP白名单

2. **交易风险**：
   - ⚠️ 永续合约有爆仓风险
   - ⚠️ 杠杆放大风险
   - ⚠️ 首次测试用小额
   - ⚠️ 务必设置止损

### 8.2 系统维护

1. **定期检查**：
   - PM2服务状态
   - 数据健康监控
   - 磁盘空间
   - 日志文件

2. **日常操作**：
   ```bash
   # 查看服务状态
   pm2 list
   
   # 查看日志
   pm2 logs flask-app --lines 100
   
   # 重启服务
   pm2 restart flask-app
   
   # 清理日志
   pm2 flush
   ```

---

## 📞 九、故障排查

### 9.1 开仓失败

**错误51010**：账户模式错误
- 解决：切换到单币种保证金模式

**错误51000**：posSide参数错误
- 解决：已修复，检查持仓模式

### 9.2 平仓失败

**错误提示**："当前账户不支持全仓杠杆"
- 解决：已修复，自动检测持仓模式

**找不到平仓按钮**：
- OKX交易页面：批量平仓按钮
- 锚点系统页面：持仓列表中的"🚨 平仓"按钮

### 9.3 数据问题

**数据不更新**：
- 检查：`/data-health-monitor`
- 查看采集器状态
- 重启失败的服务

---

## ✅ 十、系统状态总结

### 10.1 当前状态

- ✅ Flask应用运行正常
- ✅ 22个采集器运行正常（21在线 + 1停止）
- ✅ 数据健康监控正常
- ✅ OKX交易功能正常
- ✅ 开仓功能正常
- ✅ 平仓功能正常（已修复）
- ✅ 极值监控正常（3分钟采集）

### 10.2 资源使用

- **CPU**：~200% (主要是计算密集型任务)
- **内存**：~1.7 GB
- **磁盘**：稳定
- **网络**：正常

### 10.3 最近更新

**2026-02-02**：
1. ✅ 修复OKX开仓posSide参数错误
2. ✅ 修复OKX平仓持仓模式检测
3. ✅ 新增子账户平仓接口
4. ✅ 极值记录表格改为横向显示
5. ✅ 启动极值监控（3分钟采集）
6. ✅ 添加最后更新时间显示

---

## 📝 十一、相关文档

### 11.1 配置文档

- `OKX_API_CONFIGURATION_GUIDE.md` - API配置指南
- `OKX_ACCOUNT_MODE_CONFIGURATION.md` - 账户模式配置
- `OKX_TRADING_COMPLETE_SOLUTION.md` - 完整解决方案

### 11.2 功能文档

- `EXTREME_MONITORING_3MIN_COMPLETE.md` - 极值监控
- `DATA_HEALTH_MONITOR_COMPLETE.md` - 健康监控
- `COIN_CHANGE_TRACKER_SUMMARY.md` - 币种追踪

### 11.3 问题修复

- `OKX_POSSIDE_FIX.md` - posSide参数修复
- `EXTREME_TABLE_HORIZONTAL_DISPLAY_FINAL.md` - 表格显示修复

---

## 🎯 十二、快速链接

### 12.1 常用页面

- 首页：https://5000-...sandbox.../
- OKX交易：https://5000-...sandbox.../okx-trading
- 锚点系统：https://5000-...sandbox.../anchor-system-real
- 健康监控：https://5000-...sandbox.../data-health-monitor
- 币种追踪：https://5000-...sandbox.../coin-change-tracker

### 12.2 常用命令

```bash
# PM2管理
pm2 list
pm2 logs flask-app
pm2 restart flask-app

# 查看数据
ls -la data/extreme_jsonl/
tail -100 data/extreme_jsonl/extreme_real.jsonl

# Git操作
git status
git add .
git commit -m "message"
git push origin genspark_ai_developer
```

---

**文档完成！** 🎉

**最后更新**：2026-02-02 09:15 (北京时间)
