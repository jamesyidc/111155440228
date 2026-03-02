# 交易系统完整备份说明

## 📦 备份概览

- **备份时间**: 2026-02-28
- **备份文件**: `trading_system_backup_20260228_171211.tar.gz`
- **文件大小**: 253 MB (压缩后)
- **原始大小**: ~3.7 GB
- **压缩比**: ~93% (压缩率很高)
- **存放位置**: `/tmp/trading_system_backup_YYYYMMDD_HHMMSS.tar.gz`

---

## 📊 备份内容统计

### 总体统计
- **总文件数**: 2,598 个
- **Python 文件**: 88+ 个
- **JSONL 数据**: 2,089 个
- **HTML 模板**: 88 个
- **Markdown 文档**: 440 个

### 目录大小分布
```
├── data/                3.1 GB    # 完整历史数据
├── templates/           7.4 MB    # HTML 模板
├── code/                956 KB    # 工具代码
├── source_code/         744 KB    # API 源码
├── static/              396 KB    # 静态资源
├── scripts/             244 KB    # 工具脚本
├── monitors/            180 KB    # 监控脚本
├── config/              172 KB    # 配置文件
├── panic_v3/            168 KB    # Panic 系统 v3
├── panic_paged_v2/      140 KB    # Panic 系统 v2
├── tests/               8.0 KB    # 测试文件
└── python_core/         47 files  # 主目录 Python
```

---

## 🗂️ 完整目录结构

```
trading_system_backup_YYYYMMDD_HHMMSS/
│
├── 📁 python_core/                      # 主目录所有 Python 文件 (47个)
│   ├── app.py                           # 主 Flask 应用 ⭐
│   ├── okx_confirm_structure_monitor.py # 确认结构监控 ⭐
│   ├── generate_*.py                    # 生成工具
│   ├── test_*.py                        # 测试脚本
│   └── ... (其他工具脚本)
│
├── 📁 source_code/                      # Python API 源代码 (744KB)
│   ├── api/
│   ├── utils/
│   └── ...
│
├── 📁 panic_paged_v2/                   # Panic 系统 v2 (140KB)
│   └── (Panic 分页系统相关代码)
│
├── 📁 panic_v3/                         # Panic 系统 v3 (168KB)
│   └── (Panic 系统最新版本)
│
├── 📁 code/                             # 代码工具目录 (956KB)
│   ├── python/
│   │   ├── collectors/                  # 数据采集器
│   │   │   ├── signal_collector.py
│   │   │   ├── liquidation_1h_collector.py
│   │   │   ├── okx_day_change_collector.py
│   │   │   └── ... (20+ 采集器)
│   │   ├── monitors/                    # 监控服务
│   │   ├── managers/                    # 管理器
│   │   └── schedulers/                  # 调度器
│   └── javascript/
│
├── 📁 config/                           # 配置目录 (172KB)
│   └── (各种配置文件)
│
├── 📁 monitors/                         # 监控脚本 (180KB)
│   ├── okx_tpsl_monitor.py             # 固定止盈止损监控 ⭐
│   ├── okx_percent_tpsl_monitor.py     # 百分比止盈止损 ⭐
│   ├── rsi_takeprofit_monitor.py       # RSI 止盈监控
│   ├── bottom_signal_long_monitor.py   # 见底信号多单
│   └── okx_trade_history.py            # 交易历史
│
├── 📁 scripts/                          # 工具脚本 (244KB)
│   ├── backup_full_system.sh           # 完整备份脚本 ⭐
│   ├── verify_backup.sh                # 备份验证脚本 ⭐
│   └── ... (其他工具)
│
├── 📁 tests/                            # 测试文件 (8KB)
│   └── (单元测试)
│
├── 📁 static/                           # 静态资源 (396KB)
│   ├── css/
│   ├── js/
│   └── images/
│
├── 📁 templates/                        # HTML 模板 (7.4MB)
│   ├── index.html
│   ├── okx_trading.html                # OKX 交易界面 ⭐
│   ├── panic_paged_v2.html
│   └── ... (88+ 模板)
│
├── 📁 data/                             # 完整数据文件 (3.1GB) ⭐⭐⭐
│   ├── okx_tpsl_settings/              # 止盈止损配置
│   │   ├── account_main_percent_tpsl.jsonl
│   │   ├── account_main_tpsl.jsonl
│   │   ├── account_main_confirm_structure_alerts.jsonl
│   │   ├── account_main_credentials.json
│   │   └── ... (多账户配置)
│   ├── daily_predictions/              # 每日预测
│   │   ├── prediction_20260228.jsonl
│   │   └── ... (历史预测数据)
│   ├── market_sentiment/               # 市场情绪
│   │   ├── market_sentiment_20260228.jsonl
│   │   └── ... (历史情绪数据)
│   ├── signals/                        # 交易信号
│   ├── liquidation_1h/                 # 清算数据
│   ├── panic_wash/                     # 恐慌洗盘
│   ├── sar_bias_stats/                 # SAR 偏差统计
│   ├── price_position/                 # 价格仓位
│   ├── new_high_low/                   # 新高新低
│   └── ... (20+ 数据类型目录)
│
├── 📁 config_files/                     # 配置和依赖文件 ⭐
│   ├── requirements.txt                # Python 依赖
│   ├── ecosystem.config.js             # PM2 配置
│   ├── .env                            # 环境变量
│   ├── .gitignore                      # Git 忽略规则
│   ├── pm2_dump.pm2                    # PM2 进程快照
│   └── pm2_processes.json              # PM2 进程详情
│
├── 📁 system_info/                      # 系统依赖信息 ⭐
│   ├── pip_freeze.txt                  # Python 包列表 (235个)
│   ├── apt_packages.txt                # APT 包列表
│   ├── npm_global_packages.txt         # npm 全局包
│   ├── node_version.txt                # Node.js 版本
│   └── environment_vars.txt            # 环境变量
│
├── 📄 DEPLOYMENT_GUIDE.md               # 部署指南 ⭐⭐⭐
└── 📄 BACKUP_MANIFEST.txt               # 备份清单
```

**注**: ⭐ 标记为重要文件/目录

---

## 🔑 关键文件说明

### 核心应用
- **app.py**: 主 Flask 应用，端口 9002
- **okx_confirm_structure_monitor.py**: 确认结构监控服务

### 配置文件
- **requirements.txt**: Python 依赖（235个包）
- **ecosystem.config.js**: PM2 进程配置
- **.env**: 环境变量（Telegram、OKX API 等）

### 监控服务
- **okx_tpsl_monitor.py**: 固定金额止盈止损
- **okx_percent_tpsl_monitor.py**: 百分比止盈止损
- **okx_confirm_structure_monitor.py**: 确认结构（新增）

### 数据采集器（code/python/collectors/）
1. signal_collector.py - 信号采集
2. liquidation_1h_collector.py - 清算数据
3. okx_day_change_collector.py - 日涨跌幅
4. price_baseline_collector.py - 价格基线
5. sar_slope_collector.py - SAR 斜率
6. market_sentiment_collector.py - 市场情绪
7. ... (20+ 采集器)

---

## 🚀 快速恢复流程

### 1. 解压备份
```bash
cd /home/user
tar -xzf /tmp/trading_system_backup_20260228_171211.tar.gz
mv trading_system_backup_20260228_171211 webapp
cd webapp
```

### 2. 恢复文件结构
```bash
# 复制 Python 文件到主目录
cp python_core/*.py ./

# 添加执行权限
chmod +x *.py
find monitors/ -name "*.py" -exec chmod +x {} \;
```

### 3. 安装依赖
```bash
# Python 依赖
pip3 install -r config_files/requirements.txt

# 或使用精确版本
pip3 install -r system_info/pip_freeze.txt
```

### 4. 配置环境
```bash
# 复制环境配置
cp config_files/.env ./

# 编辑环境变量
nano .env
```

### 5. 启动服务
```bash
# 使用 PM2 配置文件
pm2 start config_files/ecosystem.config.js

# 或手动启动
pm2 start app.py --name flask-app --interpreter python3
pm2 start monitors/okx_tpsl_monitor.py --name okx-tpsl-monitor --interpreter python3
# ... (其他服务)

# 保存 PM2 配置
pm2 save

# 设置开机自启
pm2 startup
```

---

## 📋 PM2 服务完整列表

| ID | 服务名称 | 脚本路径 | 类型 | 端口 |
|----|---------|---------|------|------|
| 0 | flask-app | app.py | Web应用 | 9002 |
| 19 | okx-tpsl-monitor | monitors/okx_tpsl_monitor.py | 监控 | - |
| 30 | okx-percent-tpsl-monitor | okx_percent_tpsl_monitor.py | 监控 | - |
| 31 | okx-confirm-structure-monitor | okx_confirm_structure_monitor.py | 监控 | - |
| 23 | rsi-takeprofit-monitor | monitors/rsi_takeprofit_monitor.py | 监控 | - |
| 1 | signal-collector | code/python/collectors/signal_collector.py | 采集 | - |
| 2 | liquidation-1h-collector | code/python/collectors/liquidation_1h_collector.py | 采集 | - |
| 9 | okx-day-change-collector | code/python/collectors/okx_day_change_collector.py | 采集 | - |
| 10 | price-baseline-collector | code/python/collectors/price_baseline_collector.py | 采集 | - |
| 4 | v1v2-collector | code/python/collectors/v1v2_collector.py | 采集 | - |
| 5 | price-speed-collector | code/python/collectors/price_speed_collector.py | 采集 | - |
| 6 | sar-slope-collector | code/python/collectors/sar_slope_collector.py | 采集 | - |
| 7 | price-comparison-collector | code/python/collectors/price_comparison_collector.py | 采集 | - |
| 8 | financial-indicators-collector | code/python/collectors/financial_indicators_collector.py | 采集 | - |
| 3 | crypto-index-collector | code/python/collectors/crypto_index_collector.py | 采集 | - |
| 11 | sar-bias-stats-collector | code/python/collectors/sar_bias_stats_collector.py | 采集 | - |
| 12 | panic-wash-collector | code/python/collectors/panic_wash_collector.py | 采集 | - |
| 21 | market-sentiment-collector | code/python/collectors/market_sentiment_collector.py | 采集 | - |
| 22 | price-position-collector | code/python/collectors/price_position_collector.py | 采集 | - |
| 27 | new-high-low-collector | code/python/collectors/new_high_low_collector.py | 采集 | - |
| 14 | data-health-monitor | code/python/monitors/data_health_monitor.py | 监控 | - |
| 15 | system-health-monitor | code/python/monitors/system_health_monitor.py | 监控 | - |
| 16 | liquidation-alert-monitor | code/python/liquidation_alert_monitor.py | 监控 | - |
| 24 | bottom-signal-long-monitor | monitors/bottom_signal_long_monitor.py | 监控 | - |
| 17 | dashboard-jsonl-manager | code/python/managers/dashboard_jsonl_manager.py | 管理 | - |
| 18 | gdrive-jsonl-manager | code/python/managers/gdrive_jsonl_manager.py | 管理 | - |
| 28 | sar-daily-stats-scheduler | code/python/schedulers/sar_daily_stats_scheduler.py | 调度 | - |
| 20 | okx-trade-history | monitors/okx_trade_history.py | 历史 | - |
| 25 | coin-change-predictor | code/python/coin_change_predictor.py | 预测 | - |
| 26 | coin-change-tracker | code/python/coin_change_tracker.py | 追踪 | - |
| 29 | coin-price-tracker | code/python/coin_price_tracker.py | 追踪 | - |

**总计**: 31 个服务

---

## 🔧 Flask 路由映射

### 主要页面
- `GET /` - 主页
- `GET /okx-trading` - OKX 交易界面

### API 端点
```python
# 止盈止损配置
POST /api/okx-trading/tpsl-settings/<account_id>
GET  /api/okx-trading/percent-tpsl-status/<account_id>

# 确认结构
GET  /api/okx-trading/confirm-structure-alerts/<account_id>

# 持仓和账户
POST /api/okx-trading/positions
POST /api/okx-trading/account-info
POST /api/okx-trading/close-position

# 市场数据
GET  /api/market-sentiment/latest
GET  /api/coin-change-tracker/latest
GET  /api/signals/latest

# ... (50+ API 端点)
```

---

## 📊 数据文件类型

### JSONL 数据文件 (2,089个)
```
data/
├── okx_tpsl_settings/      # 止盈止损配置
├── daily_predictions/      # 每日预测
├── market_sentiment/       # 市场情绪
├── signals/                # 交易信号
├── liquidation_1h/         # 1小时清算数据
├── panic_wash/             # 恐慌洗盘事件
├── sar_bias_stats/         # SAR 偏差统计
├── price_position/         # 价格仓位数据
├── new_high_low/           # 新高新低事件
├── financial_indicators/   # 金融指标
├── crypto_index/           # 加密货币指数
├── v1v2/                   # V1V2 数据
├── price_baseline/         # 价格基线
├── price_speed/            # 价格速度
├── price_comparison/       # 价格对比
└── ... (更多数据类型)
```

---

## 🔐 安全备注

### 敏感文件处理
- ✅ `.env` 文件已备份（包含 API 密钥）
- ✅ `*_credentials.json` 已备份（账户凭证）
- ⚠️ **重要**: 备份文件包含敏感信息，请妥善保管
- 🔒 **建议**: 加密备份文件或存储在安全位置

### 清理敏感信息（可选）
如需分享备份，请先清理：
```bash
# 解压
tar -xzf trading_system_backup_*.tar.gz
cd trading_system_backup_*/

# 删除敏感文件
rm config_files/.env
rm data/okx_tpsl_settings/*_credentials.json

# 重新打包
cd ..
tar -czf trading_system_backup_clean.tar.gz trading_system_backup_*/
```

---

## 📦 备份文件管理

### 存储建议
1. **本地存储**: `/tmp/` 或 `/backups/`
2. **云存储**: AWS S3, Google Cloud Storage, 阿里云 OSS
3. **备份服务器**: 定期同步到远程服务器
4. **版本控制**: 保留最近 3-5 个备份版本

### 备份周期建议
- **每日增量**: 只备份当天数据文件
- **每周完整**: 完整系统备份
- **每月归档**: 长期存储备份

### 自动备份脚本
```bash
# 添加到 crontab
0 2 * * * /home/user/webapp/backup_full_system.sh

# 每天凌晨 2 点执行完整备份
```

---

## ✅ 验证清单

部署后请验证：

- [ ] Python 3.8+ 已安装
- [ ] Node.js 16+ 已安装
- [ ] PM2 全局安装
- [ ] 所有 Python 依赖已安装（235 个包）
- [ ] 环境变量已配置（.env）
- [ ] Flask 应用运行正常（端口 9002）
- [ ] 31 个 PM2 服务全部 online
- [ ] 数据文件完整（2,089 个 JSONL）
- [ ] API 端点测试通过
- [ ] 日志正常输出

---

## 📞 技术支持

### 文档
- **部署指南**: DEPLOYMENT_GUIDE.md
- **备份清单**: BACKUP_MANIFEST.txt
- **此说明**: BACKUP_README.md

### 脚本工具
- **备份脚本**: backup_full_system.sh
- **验证脚本**: verify_backup.sh

### 验证命令
```bash
# 验证备份文件
bash verify_backup.sh /tmp/trading_system_backup_*.tar.gz

# 查看备份内容
tar -tzf /tmp/trading_system_backup_*.tar.gz | less

# 提取部署指南
tar -xzf /tmp/trading_system_backup_*.tar.gz "*/DEPLOYMENT_GUIDE.md"
```

---

## 📈 系统规模

### 代码规模
- Python 代码: ~50,000 行
- JavaScript 代码: ~20,000 行
- HTML/CSS: ~30,000 行

### 数据规模
- JSONL 文件: 2,089 个
- 数据量: 3.1 GB
- 时间跨度: 所有历史数据

### 服务规模
- PM2 服务: 31 个
- API 端点: 50+ 个
- 数据采集器: 20+ 个
- 监控服务: 6 个

---

## 🎉 备份成功！

备份文件已成功创建并验证：

```
📦 /tmp/trading_system_backup_20260228_171211.tar.gz
💾 大小: 253 MB
📊 文件数: 2,598
✅ 完整性: 已验证
🔐 安全: 包含敏感信息，请妥善保管
```

**下一步**: 
1. 将备份文件移动到安全位置
2. 测试恢复流程（可选）
3. 设置自动备份计划

---

**更新日期**: 2026-02-28  
**备份版本**: 20260228_171211  
**文档版本**: 1.0
