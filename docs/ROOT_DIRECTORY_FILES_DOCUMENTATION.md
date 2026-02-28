# 根目录文件详细说明文档

**文档创建时间**: 2026-02-02 09:30 (北京时间)

---

## 📁 目录结构概览

根目录 `/home/user/webapp` 包含以下类型的文件：
- **Python 脚本** (.py) - 约 100+ 个文件，共 38,486 行代码
- **Markdown 文档** (.md) - 约 200+ 个文件
- **配置文件** (configs/, .json, .gitignore, requirements.txt)
- **数据目录** (data/, jsonl_data/)
- **模板目录** (source_code/templates/)
- **其他资源** (ecosystem.config.js, supervisord.conf 等)

---

## 🐍 核心 Python 文件

### 主应用文件

| 文件名 | 大小 | 行数 | 作用 |
|--------|------|------|------|
| `app_new.py` | 620K | 19,600+ | **主Flask应用** - 提供100+ API路由，包括OKX交易、锚点系统、数据监控等所有核心功能 |
| `trading_api.py` | 83K | 2,500+ | **交易API封装** - OKX API封装，提供开仓、平仓、查询订单等核心交易功能 |
| `anchor_monitor_daemon.py` | 9.0K | 250+ | **锚点监控守护进程** - 24/7监控锚点系统状态，自动重启异常进程 |
| `anchor_jsonl_manager.py` | 11K | 300+ | **锚点数据管理器** - 管理锚点系统的JSONL数据文件，自动归档和清理 |

### 数据采集脚本 (data_collectors/)

#### 极值数据采集
| 文件名 | 大小 | 作用 |
|--------|------|------|
| `extreme_realtime_collector.py` | 15K | **实时极值采集** - 每3分钟采集加密货币价格极值数据（最高价、最低价） |
| `extreme_jsonl_manager.py` | 12K | **极值数据管理** - 管理极值JSONL文件，自动归档历史数据 |
| `generate_today_extreme.py` | 4.8K | **生成今日极值** - 从历史数据生成今日极值统计 |
| `batch_import_today.py` | 2.5K | **批量导入** - 批量导入今日极值数据到数据库 |
| `import_all_today_files.py` | 8.5K | **导入所有文件** - 导入所有今日极值文件到系统 |

#### 市场数据采集
| 文件名 | 大小 | 作用 |
|--------|------|------|
| `coin_change_tracker.py` | 18K | **币种涨跌追踪** - 实时追踪币种价格变化，记录涨跌幅 |
| `coin_price_tracker.py` | 16K | **币价追踪** - 持续监控币种价格，记录价格历史 |
| `crypto_index_collector.py` | 14K | **加密指数采集** - 采集加密市场指数数据（恐慌指数、贪婪指数等） |
| `price_speed_collector.py` | 12K | **价格速度采集** - 计算并记录价格变化速度 |

#### 技术指标采集
| 文件名 | 大小 | 作用 |
|--------|------|------|
| `sar_1min_collector.py` | 19K | **SAR 1分钟采集** - 采集1分钟级别的抛物线转向指标 |
| `sar_jsonl_collector.py` | 21K | **SAR JSONL采集** - 采集SAR指标并存储为JSONL格式 |
| `sar_slope_collector.py` | 13K | **SAR斜率采集** - 计算并记录SAR指标的斜率变化 |
| `sar_bias_stats_collector.py` | 14K | **SAR偏差统计** - 统计SAR指标与价格的偏差 |
| `support_resistance_collector.py` | 17K | **支撑阻力采集** - 识别并记录支撑位和阻力位 |
| `support_resistance_snapshot.py` | 16K | **支撑阻力快照** - 定期快照支撑阻力数据 |

#### 风险监控采集
| 文件名 | 大小 | 作用 |
|--------|------|------|
| `panic_collector.py` | 11K | **恐慌指标采集** - 采集市场恐慌指标（爆仓数据、资金费率等） |
| `liquidation_1h_collector.py` | 10K | **爆仓数据采集** - 采集1小时级别的爆仓数据 |
| `escape_signal_calculator.py` | 25K | **逃顶信号计算** - 计算逃顶信号，提供卖出建议 |
| `escape_auto_updater.py` | 1.1K | **逃顶自动更新** - 自动更新逃顶信号数据 |

#### 其他采集
| 文件名 | 大小 | 作用 |
|--------|------|------|
| `v1v2_collector.py` | 8.5K | **V1V2数据采集** - 采集币种V1V2版本数据对比 |
| `gdrive_detector.py` | 6.2K | **Google Drive检测** - 检测并同步Google Drive中的数据 |
| `major_events_monitor.py` | 22K | **重大事件监控** - 监控加密市场重大事件（减半、升级等） |
| `data_health_monitor.py` | 19K | **数据健康监控** - 监控所有数据采集服务的健康状态 |

### 数据管理脚本

| 文件名 | 大小 | 作用 |
|--------|------|------|
| `anchor_jsonl_manager.py` | 11K | 管理锚点系统JSONL文件 |
| `extreme_jsonl_manager.py` | 12K | 管理极值数据JSONL文件 |
| `panic_jsonl_manager.py` | 9.8K | 管理恐慌指标JSONL文件 |
| `sar_jsonl_manager.py` | 10K | 管理SAR指标JSONL文件 |
| `liquidation_jsonl_manager.py` | 9.5K | 管理爆仓数据JSONL文件 |
| `support_jsonl_manager.py` | 10K | 管理支撑阻力JSONL文件 |
| `v1v2_jsonl_manager.py` | 8.0K | 管理V1V2数据JSONL文件 |
| `coin_change_jsonl_manager.py` | 9.2K | 管理币种涨跌JSONL文件 |

### 工具脚本

| 文件名 | 大小 | 作用 |
|--------|------|------|
| `check_data_collection.py` | 5.5K | 检查数据采集状态 |
| `check_pm2_services.py` | 4.2K | 检查PM2服务状态 |
| `restart_all_collectors.py` | 3.8K | 重启所有数据采集器 |
| `update_extreme_timestamps.py` | 2.9K | 更新极值时间戳 |
| `fix_extreme_data.py` | 3.5K | 修复极值数据 |
| `backup_data.py` | 6.8K | 备份数据文件 |
| `clean_old_data.py` | 4.5K | 清理旧数据 |

### 测试脚本

| 文件名 | 大小 | 作用 |
|--------|------|------|
| `test_okx_api.py` | 12K | 测试OKX API连接和功能 |
| `test_trading.py` | 8.5K | 测试交易功能 |
| `test_anchor_system.py` | 9.8K | 测试锚点系统 |
| `test_data_health.py` | 7.2K | 测试数据健康监控 |

### 其他脚本

| 文件名 | 大小 | 作用 |
|--------|------|------|
| `add_base_record.py` | 3.2K | 添加基础记录到数据库 |
| `anchor_api_adapter.py` | 5.8K | 锚点API适配器 |
| `create_anchor_backups.py` | 4.5K | 创建锚点数据备份 |
| `fix_account_version.py` | 2.8K | 修复账户版本问题 |

---

## 📝 Markdown 文档分类

### 1️⃣ 系统配置文档 (约 30 个)

#### OKX 交易配置
- `OKX_API_CONFIGURATION_GUIDE.md` (5.2K) - OKX API配置指南
- `OKX_API_CONFIGURATION_COMPLETE.md` (4.8K) - OKX API配置完成报告
- `OKX_ACCOUNT_MODE_CONFIGURATION.md` (6.5K) - OKX账户模式配置说明
- `OKX_POSSIDE_FIX.md` (4.2K) - OKX posSide参数修复文档
- `OKX_TRADING_COMPLETE_SOLUTION.md` (6.9K) - OKX交易完整解决方案

#### 系统部署配置
- `DEPLOYMENT_GUIDE.md` (8.5K) - 系统部署指南
- `PM2_SERVICE_CONFIGURATION.md` (5.8K) - PM2服务配置说明
- `SUPERVISOR_CONFIGURATION.md` (4.2K) - Supervisor配置说明
- `BACKUP_INSTRUCTIONS.md` (0B) - 备份说明（空文件）

### 2️⃣ 功能修复文档 (约 50 个)

#### 交易功能修复
- `CLOSE_POSITION_FIX_COMPLETE.md` (7.2K) - 平仓功能修复完成
- `BATCH_CLOSE_POSITION_MODE_FIX.md` (6.8K) - 批量平仓模式修复
- `ABORT_ERROR_FIXED.md` (4.3K) - 中止错误修复
- `POSITION_QUERY_FIX.md` (5.5K) - 持仓查询修复

#### 界面优化修复
- `EXTREME_TABLE_HORIZONTAL_DISPLAY_FINAL.md` (8.9K) - 极值表格横向显示最终版
- `EXTREME_TABLE_HORIZONTAL_FORMAT_COMPLETE.md` (7.5K) - 极值表格横向格式完成
- `EXTREME_RECORD_OPTIMIZATION_COMPLETE.md` (9.2K) - 极值记录优化完成
- `EXTREME_UI_HORIZONTAL_LAYOUT_COMPLETE.md` (8.5K) - 极值UI横向布局完成

#### 数据采集修复
- `DATA_HEALTH_INTEGRATION_COMPLETE.md` (6.5K) - 数据健康集成完成
- `COIN_TRACKER_FIX_COMPLETE.md` (5.8K) - 币种追踪修复完成
- `PANIC_COLLECTOR_FIX.md` (4.9K) - 恐慌采集器修复

### 3️⃣ 功能开发文档 (约 40 个)

#### 锚点系统
- `ANCHOR_SYSTEM_GUIDE.md` (12K) - 锚点系统使用指南
- `ANCHOR_PROFIT_MONITOR_COMPLETE.md` (8.5K) - 锚点利润监控完成
- `ANCHOR_AUTO_MONITOR_COMPLETE.md` (7.8K) - 锚点自动监控完成
- `ANCHOR_MULTI_TIMEFRAME_COMPLETE.md` (9.2K) - 锚点多时间框架完成

#### 数据健康监控
- `DATA_HEALTH_MONITOR_COMPLETE.md` (10K) - 数据健康监控完成
- `DATA_HEALTH_DASHBOARD_COMPLETE.md` (8.5K) - 数据健康仪表板完成
- `DATA_HEALTH_ALERT_SYSTEM.md` (7.2K) - 数据健康警报系统

#### 币种追踪
- `COIN_CHANGE_TRACKER_COMPLETE.md` (9.5K) - 币种涨跌追踪完成
- `COIN_PRICE_TRACKER_COMPLETE.md` (8.8K) - 币价追踪完成
- `27币追涨打包完成报告.md` (6.5K) - 27币追涨打包完成

### 4️⃣ 技术实现文档 (约 30 个)

#### Git 操作
- `GIT_COMMIT_COMMANDS.md` (3.5K) - Git提交命令说明
- `GIT_WORKFLOW.md` (5.2K) - Git工作流程
- `BRANCH_MANAGEMENT.md` (4.8K) - 分支管理说明

#### API 文档
- `API_DOCUMENTATION.md` (15K) - API完整文档
- `OKX_API_REFERENCE.md` (12K) - OKX API参考
- `TRADING_API_GUIDE.md` (10K) - 交易API指南

#### 数据库设计
- `DATABASE_SCHEMA.md` (8.5K) - 数据库模式设计
- `JSONL_DATA_FORMAT.md` (6.2K) - JSONL数据格式说明
- `DATA_MIGRATION_GUIDE.md` (7.8K) - 数据迁移指南

### 5️⃣ 故障排查文档 (约 20 个)

- `TROUBLESHOOTING_GUIDE.md` (12K) - 故障排查指南
- `COMMON_ERRORS.md` (8.5K) - 常见错误说明
- `DEBUG_TIPS.md` (6.8K) - 调试技巧
- `LOG_ANALYSIS.md` (7.2K) - 日志分析指南

### 6️⃣ 项目管理文档 (约 20 个)

- `COMPLETE_SYSTEM_DOCUMENTATION.md` (25K) - **完整系统文档**
- `PROJECT_STRUCTURE.md` (9.5K) - 项目结构说明
- `DELIVERY_CHECKLIST.md` (4.1K) - 交付检查清单
- `VERSION_HISTORY.md` (10K) - 版本历史记录
- `CHANGELOG.md` (8.5K) - 更新日志

### 7️⃣ 临时/测试文档 (约 10 个)

- `TEST_RESULTS.md` (5.5K) - 测试结果
- `TEMP_NOTES.md` (2.8K) - 临时笔记
- `DEBUG_LOG.md` (4.2K) - 调试日志

---

## ⚙️ 配置文件

### configs/ 目录

| 文件名 | 作用 |
|--------|------|
| `okx_api_config.json` | OKX API密钥配置（API Key, Secret, Passphrase） |
| `telegram_config.json` | Telegram机器人配置（Bot Token, Chat ID） |
| `trading_config.json` | 交易配置（杠杆、止损止盈等） |
| `monitor_config.json` | 监控配置（采集间隔、告警阈值等） |
| `database_config.json` | 数据库配置（连接信息） |

### 根目录配置

| 文件名 | 作用 |
|--------|------|
| `ecosystem.config.js` | PM2配置文件 - 定义所有PM2服务的启动参数 |
| `supervisord.conf` | Supervisor配置 - 管理Python服务 |
| `requirements.txt` | Python依赖包列表 |
| `.gitignore` | Git忽略文件规则 |
| `package.json` | Node.js依赖配置（如果有） |

---

## 📊 数据目录

### data/ 目录结构

```
data/
├── extreme_jsonl/          # 极值数据JSONL文件
│   ├── extreme_20260202.jsonl
│   ├── extreme_20260201.jsonl
│   └── ...
├── anchor_daily/           # 锚点每日数据
│   ├── anchor_20260202.jsonl
│   └── ...
├── panic_jsonl/            # 恐慌指标数据
│   ├── panic_20260202.jsonl
│   └── ...
├── sar_jsonl/             # SAR指标数据
├── liquidation_jsonl/      # 爆仓数据
├── support_jsonl/          # 支撑阻力数据
├── coin_change_jsonl/      # 币种涨跌数据
└── v1v2_jsonl/            # V1V2对比数据
```

---

## 🌐 HTML 模板

### source_code/templates/ 目录

| 文件名 | 大小 | 作用 |
|--------|------|------|
| `okx_trading.html` | 152K | **OKX交易页面** - 主要交易界面，支持开仓、平仓、批量操作 |
| `anchor_system_real.html` | 270K | **锚点系统实盘页面** - 实盘锚点交易系统 |
| `anchor_system_paper.html` | 34K | **锚点系统模拟页面** - 模拟盘锚点交易 |
| `anchor_system.html` | 34K | **锚点系统主页面** - 锚点系统总览 |
| `trading_manager.html` | 177K | **交易管理器** - 交易订单管理 |
| `data_health_monitor.html` | 45K | **数据健康监控页面** - 数据采集服务监控 |
| `coin_change_tracker.html` | 38K | **币种涨跌追踪页面** - 币种价格变化追踪 |
| `anchor_warning.html` | 26K | **锚点警报页面** - 锚点系统警报 |
| `trading_signals.html` | 28K | **交易信号页面** - 交易信号展示 |
| `anchor_auto_monitor.html` | 19K | **锚点自动监控页面** - 自动监控界面 |

---

## 🔧 PM2 服务说明

### 运行中的服务 (22个在线 + 1个停止)

| 服务名 | PID | 内存 | CPU | 运行时长 | 作用 |
|--------|-----|------|-----|----------|------|
| `flask-app` | 1209973 | 389.9M | 100% | 7分钟 | **主Flask应用** - 提供所有Web界面和API |
| `escape-signal-calculator` | 671242 | 639.8M | 100% | 23小时 | **逃顶信号计算** - 计算卖出信号 |
| `anchor-profit-monitor` | 657141 | 30.5M | 0% | 24小时 | **锚点利润监控** - 监控锚点系统盈亏 |
| `coin-change-tracker` | 656920 | 30.5M | 0% | 24小时 | **币种涨跌追踪** - 追踪币种价格变化 |
| `coin-price-tracker` | 1205019 | 30.4M | 0% | 7小时 | **币价追踪** - 记录币种价格 |
| `crypto-index-collector` | 1562 | 31.4M | 0% | 28天 | **加密指数采集** - 采集市场指数 |
| `data-health-monitor` | 920866 | 40.9M | 0% | 19小时 | **数据健康监控** - 监控数据采集状态 |
| `gdrive-detector` | 865860 | 50.6M | 0% | 20小时 | **Google Drive检测** - 同步云端数据 |
| `liquidation-1h-collector` | 1565 | 28.9M | 0% | 28天 | **爆仓数据采集** - 采集1小时爆仓数据 |
| `major-events-monitor` | 423165 | 166.6M | 0% | 2天 | **重大事件监控** - 监控市场重大事件 |
| `panic-collector` | 769427 | 29.3M | 0% | 23小时 | **恐慌指标采集** - 采集恐慌指标 |
| `price-speed-collector` | 1560 | 30.1M | 0% | 28天 | **价格速度采集** - 计算价格变化速度 |
| `sar-1min-collector` | 751179 | 80.1M | 0% | 23小时 | **SAR 1分钟采集** - 采集1分钟SAR |
| `sar-bias-stats-collector` | 763950 | 32.0M | 0% | 23小时 | **SAR偏差统计** - SAR偏差分析 |
| `sar-jsonl-collector` | 794189 | 85.6M | 0% | 23小时 | **SAR JSONL采集** - SAR数据采集 |
| `sar-slope-collector` | 1564 | 29.4M | 0% | 28天 | **SAR斜率采集** - SAR斜率计算 |
| `support-resistance-collector` | 668835 | 31.3M | 0% | 24小时 | **支撑阻力采集** - 识别支撑阻力位 |
| `support-resistance-snapshot` | 18316 | 98.4M | 0% | 27天 | **支撑阻力快照** - 快照支撑阻力 |
| `v1v2-collector` | 1561 | 30.1M | 0% | 28天 | **V1V2采集** - V1V2数据对比 |
| `okx-day-change-collector` | 0 | - | - | **已停止** | **OKX日涨跌采集** - 采集日涨跌（未运行） |

**总资源占用**:
- **总内存**: ~1.7GB
- **总CPU**: ~200% (主要是 flask-app 和 escape-signal-calculator)
- **在线服务**: 22个
- **停止服务**: 1个

---

## 📈 系统功能总览

### 核心功能模块

1. **OKX 交易系统**
   - 开仓（市价单、限价单）
   - 平仓（全部平仓、部分平仓）
   - 批量操作（批量开仓、批量平仓）
   - 持仓查询
   - 订单管理

2. **锚点系统**
   - 实盘交易
   - 模拟交易
   - 利润监控
   - 自动监控
   - 警报系统

3. **数据采集系统**
   - 极值数据（最高价、最低价）
   - 技术指标（SAR、支撑阻力）
   - 市场数据（价格、涨跌幅）
   - 风险指标（爆仓、恐慌指数）

4. **监控告警系统**
   - 数据健康监控
   - 服务状态监控
   - 交易异常监控
   - Telegram通知

5. **数据管理系统**
   - JSONL数据管理
   - 自动归档
   - 数据清理
   - 数据备份

---

## 🚀 快速启动命令

### 启动所有服务
```bash
cd /home/user/webapp
pm2 start ecosystem.config.js
```

### 重启Flask应用
```bash
pm2 restart flask-app
```

### 查看服务状态
```bash
pm2 status
pm2 logs flask-app --lines 50
```

### 重启所有数据采集器
```bash
python restart_all_collectors.py
```

---

## 📝 重要提示

### 配置文件安全
- ⚠️ **configs/okx_api_config.json** 包含敏感信息（API密钥），权限设置为 `600`
- ⚠️ **configs/telegram_config.json** 包含Telegram密钥，需妥善保管
- ⚠️ 所有配置文件已在 `.gitignore` 中排除，不会提交到Git

### 数据文件管理
- 📁 **data/** 目录包含所有JSONL数据文件
- 🔄 每天自动归档历史数据
- 🗑️ 超过30天的旧数据会自动清理
- 💾 重要数据请定期备份

### 服务监控
- 🔍 使用 `data-health-monitor` 监控所有数据采集服务
- 📊 访问 `/data-health-monitor` 查看服务状态
- 📱 异常情况会通过Telegram通知

---

## 📞 常见问题

### Q1: Flask应用无法启动？
```bash
# 查看错误日志
pm2 logs flask-app --err

# 检查端口占用
lsof -i :5000

# 重启服务
pm2 restart flask-app
```

### Q2: 数据采集器停止工作？
```bash
# 查看采集器状态
pm2 status

# 重启特定采集器
pm2 restart extreme-realtime-collector

# 重启所有采集器
python restart_all_collectors.py
```

### Q3: OKX交易报错？
- 检查 `configs/okx_api_config.json` 配置是否正确
- 检查API密钥权限（需要交易权限）
- 查看Flask日志：`pm2 logs flask-app | grep "OKX"`

### Q4: 如何查看系统运行状态？
- 访问: `https://5000-xxx.sandbox.novita.ai/data-health-monitor`
- 或运行: `python check_pm2_services.py`

---

## 🎯 下一步操作建议

1. **立即测试平仓功能**
   - 访问 OKX 交易页面
   - 测试"平全部空单"功能
   - 查看日志确认修复成功

2. **提交代码到Git**
   ```bash
   cd /home/user/webapp
   git add source_code/app_new.py
   git commit -m "fix(trading): 修复批量平仓持仓模式检测问题"
   git push origin genspark_ai_developer
   ```

3. **创建Pull Request**
   - 从 `genspark_ai_developer` 到 `main`
   - 标题: "修复OKX批量平仓功能"
   - 描述: 修复了批量平仓时持仓模式检测问题

4. **监控系统运行**
   - 查看数据健康监控页面
   - 确保所有采集器正常运行
   - 检查是否有异常告警

---

**文档版本**: v1.0  
**最后更新**: 2026-02-02 09:30  
**维护者**: GenSpark AI Developer  

---

**相关文档**:
- [完整系统文档](COMPLETE_SYSTEM_DOCUMENTATION.md)
- [API文档](API_DOCUMENTATION.md)
- [部署指南](DEPLOYMENT_GUIDE.md)
- [故障排查](TROUBLESHOOTING_GUIDE.md)
