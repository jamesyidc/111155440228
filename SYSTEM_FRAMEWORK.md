# 系统运行框架说明

## 📋 系统概览

本文档描述了整个系统的核心运行框架，包括所有后台服务、监控进程和自动化任务。

**最后更新**: 2026-03-02  
**系统版本**: v3.0

---

## 🚀 核心服务列表

### 1. Flask Web应用

**进程名**: `flask-app`  
**端口**: 9002  
**状态**: ✅ 在线运行

**功能**:
- Web界面展示（币涨跌幅追踪、OKX交易、数据管理等）
- RESTful API服务
- Websocket实时数据推送

**管理命令**:
```bash
pm2 restart flask-app
pm2 logs flask-app --lines 50
```

---

### 2. ✅ OKX止盈止损自动监控（v3.0 - 重要）

**进程名**: `okx-tpsl-monitor`  
**检查间隔**: 60秒  
**状态**: ✅ 后台7×24小时运行

#### 【问题】止盈止损需要浏览器保持打开，关闭后无法执行

#### 【修复】后台自动监控服务 - 无需浏览器

#### 🟢 核心特性：

- ✅ **PM2守护进程管理**，崩溃自动重启
- ✅ **每60秒自动检查**所有账户的持仓盈亏
- ✅ **触发条件时立即执行**平仓
- ✅ **完全不依赖浏览器**，关闭浏览器也能执行
- ✅ 支持**普通止盈止损** + **市场情绪紧急止盈**

#### 📊 监控账户（5个）：

1. **account_main**（主账户）
2. **account_fangfang12**
3. **account_poit_main**（POIT子账户）
4. **account_anchor**（锚点账户）
5. **account_dadanini**（新增，支持net_mode单向持仓）

#### 🎯 工作流程：

1. 每60秒扫描所有账户
2. 读取止盈止损配置（`data/okx_tpsl_settings/`）
3. 获取当前持仓并计算盈亏百分比
4. 检查是否触发：
   - **市场情绪止盈**（优先）：检测到极端信号立即平仓
   - **普通止盈**：盈亏% ≥ 止盈阈值
   - **普通止损**：盈亏% ≤ 止损阈值
5. 执行平仓（调用OKX API设置条件单）
6. 记录执行结果（防止重复执行）
7. 发送Telegram通知

#### 🔒 安全机制：

- ✅ **防重复执行**：每个持仓的止盈/止损只执行一次
- ✅ **执行记录**：保存到 `{account_id}_tpsl_execution.jsonl`
- ✅ **自动重启**：PM2确保进程崩溃后自动恢复
- ✅ **日志记录**：详细记录每次检查和执行过程
- ✅ **实时通知**：Telegram推送执行结果

#### 📋 配置文件：

```
data/okx_tpsl_settings/
├── account_main_tpsl.jsonl              # 止盈止损配置
├── account_main_tpsl_execution.jsonl    # 执行记录
├── account_fangfang12_tpsl.jsonl
├── account_poit_main_tpsl.jsonl
├── account_anchor_tpsl.jsonl
└── account_dadanini_tpsl.jsonl

data/okx_auto_strategy/
└── {account_id}.json                    # 账户API凭证
```

#### 🔍 查看运行状态：

```bash
# 查看监控进程
pm2 list | grep okx-tpsl-monitor

# 查看实时日志
pm2 logs okx-tpsl-monitor --lines 50

# 重启服务
pm2 restart okx-tpsl-monitor
```

#### 💡 重要提示：

1. ⭐ **监控进程已经在后台运行，无需手动启动**
2. 🌐 **浏览器中的止盈止损开关只控制前端页面的弹窗提示**
3. 📄 **后台监控服务读取JSONL配置文件，不受前端开关影响**
4. 🔄 **修改止盈止损阈值后，后台会在下次检查时自动读取新配置**
5. 🛑 **如需临时禁用监控，修改JSONL文件中的 `enabled` 字段为 `false`**

#### ⚠️ 注意事项：

1. 确保账户**API凭证配置正确**（apiKey、apiSecret、passphrase）
2. 确保账户有**足够的持仓**才会触发止盈止损
3. 监控进程**每60秒检查一次**，不是实时的（已够快）
4. 市场剧烈波动时可能存在**滑点**，建议设置合理的止盈止损阈值
5. **详细文档**: `OKX_TPSL_MONITOR_SYSTEM.md` 和 `FIX_BACKEND_AUTOMATION_2026-02-28.md`

---

### 3. 币涨跌幅预测监控

**进程名**: `coin-change-predictor`  
**运行时间**: 每日00:10-02:00（北京时间）  
**更新间隔**: 每10分钟

**功能**:
- 分析0点-2点的币涨跌幅数据
- 判断市场信号（低吸、等待新低、做空等）
- 检测二级触发条件（2:10-2:30的三根柱子）
- 生成每日预测报告

**新增逻辑** (2026-03-02):
- **情况1c**: 绿色>=3根 + (有红色或有空白) → 低吸
- **二级触发扩展**: 支持红色柱子组合
  - 🔴🔴🔴 三根全红 → 等跌后做多
  - 🔴🔴⚪ 红红空白 → 等跌后做多
  - 🔴⚪⚪ 红空白空白 → 等跌后做多

**配置文件**:
- 预测数据: `data/daily_predictions/prediction_YYYYMMDD.jsonl`

**管理命令**:
```bash
pm2 restart coin-change-predictor
pm2 logs coin-change-predictor --lines 50

# 手动触发预测
cd /home/user/webapp/monitors
python3 coin_change_prediction_monitor.py
```

---

### 4. 数据采集服务（27个）

#### 价格类采集器
- **signal-collector**: 信号数据采集
- **liquidation-1h-collector**: 1小时清算数据
- **crypto-index-collector**: 加密货币指数
- **price-speed-collector**: 价格速度
- **price-position-collector**: 价格位置
- **price-baseline-collector**: 价格基线
- **price-comparison-collector**: 价格对比
- **coin-price-tracker**: 币价追踪

#### 技术指标采集器
- **v1v2-collector**: V1/V2指标
- **sar-slope-collector**: SAR斜率
- **sar-bias-stats-collector**: SAR偏差统计
- **financial-indicators-collector**: 金融指标

#### 市场数据采集器
- **okx-day-change-collector**: OKX日涨跌幅
- **panic-wash-collector**: 恐慌洗盘
- **market-sentiment-collector**: 市场情绪
- **new-high-low-collector**: 创新高低统计

#### 特殊采集器
- **coin-change-tracker**: 币涨跌幅追踪（0-2点）
- **dashboard-jsonl-manager**: 仪表板数据管理
- **gdrive-jsonl-manager**: Google Drive数据同步

---

### 5. 监控和告警服务（8个）

#### 交易监控
- **okx-tpsl-monitor**: 止盈止损自动执行（⭐ 核心服务）
- **okx-percent-tpsl-monitor**: 百分比止盈止损
- **okx-crash-warning-stop-loss**: 崩盘预警止损
- **okx-trade-history**: 交易历史记录
- **okx-confirm-structure-monitor**: 确认结构监控

#### 策略监控
- **bottom-signal-long-monitor**: 底部信号做多
- **rsi-takeprofit-monitor**: RSI止盈监控

#### 系统监控
- **liquidation-alert-monitor**: 清算告警
- **data-health-monitor**: 数据健康检查
- **system-health-monitor**: 系统健康检查

---

## 📊 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask Web Application                     │
│                      (Port: 9002)                             │
│  - Web UI (币涨跌幅追踪、OKX交易、数据管理等)                  │
│  - RESTful API                                                │
│  - Websocket实时推送                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 数据交互
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐   ┌──────────────────┐   ┌──────────────┐
│  数据采集层  │   │   监控告警层     │   │  自动执行层  │
│  (27个进程)  │   │   (8个进程)      │   │  (核心服务)  │
├──────────────┤   ├──────────────────┤   ├──────────────┤
│ • 价格采集   │   │ • 交易监控       │   │ • 止盈止损   │
│ • 指标计算   │   │ • 策略监控       │   │ • 市场情绪   │
│ • 市场数据   │   │ • 系统健康       │   │ • 条件平仓   │
└──────────────┘   └──────────────────┘   └──────────────┘
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   数据存储层     │
                    │  (JSONL Files)   │
                    ├──────────────────┤
                    │ • 历史数据       │
                    │ • 配置文件       │
                    │ • 执行记录       │
                    │ • 统计报告       │
                    └──────────────────┘
```

---

## 🔧 系统管理命令

### 查看所有服务状态
```bash
pm2 status
```

### 重启所有服务
```bash
pm2 restart ecosystem.config.js
```

### 查看特定服务日志
```bash
# 查看止盈止损监控日志
pm2 logs okx-tpsl-monitor --lines 50

# 查看Flask应用日志
pm2 logs flask-app --lines 50

# 查看预测监控日志
pm2 logs coin-change-predictor --lines 50
```

### 停止/启动特定服务
```bash
pm2 stop okx-tpsl-monitor
pm2 start okx-tpsl-monitor
pm2 restart okx-tpsl-monitor
```

---

## 📁 重要目录结构

```
/home/user/webapp/
├── app.py                              # Flask主应用
├── ecosystem.config.js                  # PM2配置文件
│
├── monitors/                            # 监控脚本
│   ├── coin_change_prediction_monitor.py
│   └── ...
│
├── source_code/                         # 核心服务脚本
│   ├── okx_tpsl_monitor.py             # 止盈止损监控 ⭐
│   ├── data_manager.py
│   └── ...
│
├── data/                                # 数据目录
│   ├── okx_tpsl_settings/              # 止盈止损配置 ⭐
│   ├── okx_auto_strategy/              # 账户API凭证
│   ├── daily_predictions/               # 每日预测数据
│   ├── coin_change_history/             # 币涨跌幅历史
│   └── ...                              # 其他数据目录（42个）
│
├── templates/                           # 前端模板
│   ├── okx_trading.html                # OKX交易页面
│   ├── coin_change_tracker.html         # 币涨跌幅追踪
│   └── ...
│
└── logs/                                # 日志目录
    └── ~/.pm2/logs/                     # PM2日志
```

---

## 🔐 安全和备份

### 1. 自动备份
- **数据备份**: `source_code/data_backup_service.py`
- **备份目录**: `/home/user/webapp/backups/`
- **备份频率**: 手动或定时任务

### 2. 执行记录
- 所有自动执行操作都有完整记录
- 止盈止损: `data/okx_tpsl_settings/*_execution.jsonl`
- 交易历史: `data/okx_trading_history/`
- 策略执行: `data/okx_auto_strategy/*_execution.jsonl`

### 3. 日志管理
- PM2自动管理日志文件
- 日志位置: `~/.pm2/logs/`
- 日志轮转: 自动进行

---

## 🚨 故障处理

### 服务未运行
```bash
# 检查服务状态
pm2 status

# 查看错误日志
pm2 logs <service-name> --err --lines 50

# 重启服务
pm2 restart <service-name>
```

### 止盈止损未触发
1. 检查配置文件: `cat data/okx_tpsl_settings/account_main_tpsl.jsonl`
2. 确认 `enabled: true`
3. 检查执行记录: `cat data/okx_tpsl_settings/account_main_tpsl_execution.jsonl`
4. 查看监控日志: `pm2 logs okx-tpsl-monitor`

### API调用失败
1. 检查API凭证: `cat data/okx_auto_strategy/account_main.json`
2. 验证OKX账户权限
3. 检查网络连接
4. 查看Flask日志: `pm2 logs flask-app`

---

## 📱 通知系统

### Telegram通知
- **配置文件**: `.env`
- **测试命令**: `python3 test_telegram.py`
- **通知类型**:
  - 止盈止损执行结果
  - 市场情绪警报
  - 系统异常告警

### 配置Telegram
```bash
# 编辑 .env 文件
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# 测试配置
python3 test_telegram.py
```

---

## 📖 相关文档

- **止盈止损监控系统**: `OKX_TPSL_MONITOR_SYSTEM.md` ⭐
- **后台自动化修复**: `FIX_BACKEND_AUTOMATION_2026-02-28.md`
- **数据管理指南**: `DATA_MANAGEMENT_GUIDE.md`
- **系统状态**: `SYSTEM_STATUS.md`
- **部署说明**: `README_DEPLOYMENT.md`

---

## ✅ 系统检查清单

- [x] Flask应用正常运行（Port 9002）
- [x] 止盈止损监控后台运行（每60秒检查）
- [x] 5个账户配置完整（含DADANINI）
- [x] 币涨跌幅预测每日自动运行
- [x] 27个数据采集器正常运行
- [x] 8个监控服务正常运行
- [x] Telegram通知配置完成
- [x] 数据备份策略就绪
- [x] 日志记录完整
- [x] 文档更新到v3.0

---

**系统状态**: 🟢 在线运行  
**最后更新**: 2026-03-02  
**版本**: v3.0  
**维护者**: AI Assistant
