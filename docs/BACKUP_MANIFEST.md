# 加密货币数据分析系统 - 备份清单

## 📋 备份信息

### 基本信息
- **备份文件**: `crypto_analysis_system_backup_20260208_000149.tar.gz`
- **备份路径**: `/tmp/crypto_analysis_system_backup_20260208_000149.tar.gz`
- **备份大小**: 224 MB (压缩后)
- **备份时间**: 2026-02-08 00:02:59
- **备份版本**: 20260208_000149
- **总文件数**: 1,145 个文件

---

## 📦 备份内容详细清单

### 1. 核心应用文件 (5 个)
```
✅ app.py                           # Flask 主应用 (~1.2MB, 20000+ 行)
✅ ecosystem.config.js              # PM2 进程配置
✅ requirements.txt                 # Python 依赖列表
✅ package.json                     # Node.js 依赖 (如果存在)
✅ config.py                        # 系统配置 (如果存在)
```

**重新部署说明**:
1. 将 `app.py` 复制到 `/home/user/webapp/`
2. 将 `ecosystem.config.js` 复制到 `/home/user/webapp/`
3. 安装依赖: `pip3 install -r requirements.txt`
4. 启动: `pm2 start ecosystem.config.js`

---

### 2. 源代码目录 (1002 个 Python 文件)

#### 2.1 数据采集器 (Collectors)
```
source_code/
├── sar_collector.py                    # SAR 指标采集器
├── sar_bias_stats_collector.py         # SAR 偏向统计采集器 (每5分钟)
├── sar_slope_collector.py              # SAR 斜率采集器
├── panic_wash_collector.py             # 恐慌清洗指数采集器
├── coin_change_tracker.py              # 币种涨跌追踪器
├── signal_collector.py                 # 信号采集器
├── signal_timeline_collector.py        # 信号时间线采集器
├── gdrive_detector.py                  # Google Drive 检测器
├── gdrive_jsonl_manager.py             # GDrive JSONL 管理器
├── crypto_index_collector.py           # 加密指数采集器
├── financial_indicators_collector.py   # 金融指标采集器
├── liquidation_1h_collector.py         # 1小时爆仓数据采集器
├── okx_day_change_collector.py         # OKX 日变化采集器
├── price_baseline_collector.py         # 价格基线采集器
├── price_speed_collector.py            # 价格速度采集器
├── price_development_collector.py      # 价格发展采集器
└── v1v2_collector.py                   # V1V2 采集器
```

**重新部署说明**:
1. 复制整个 `source_code/` 到 `/home/user/webapp/`
2. 使用 PM2 启动各采集器: `pm2 start ecosystem.config.js`
3. 验证: `pm2 list` 查看所有采集器状态

#### 2.2 数据管理器 (JSONL Managers)
```
source_code/
├── escape_signal_jsonl_manager.py      # 逃顶信号数据管理器 ✨ 新增
├── extreme_jsonl_manager.py            # 极值数据管理器
├── sar_jsonl_manager.py                # SAR 数据管理器
├── sar_slope_jsonl_manager.py          # SAR 斜率数据管理器
├── gdrive_jsonl_manager.py             # GDrive 数据管理器
├── query_jsonl_manager.py              # 查询数据管理器
├── dashboard_jsonl_manager.py          # 仪表板数据管理器
├── fear_greed_jsonl_manager.py         # 恐惧贪婪指数管理器
├── price_speed_jsonl_manager.py        # 价格速度管理器
├── v1v2_jsonl_manager.py               # V1V2 数据管理器
├── crypto_index_jsonl_manager.py       # 加密指数管理器
├── price_comparison_jsonl_manager.py   # 价格对比管理器
├── okx_trading_jsonl_manager.py        # OKX 交易管理器
└── extreme_daily_jsonl_manager.py      # 极值日数据管理器
```

**重新部署说明**:
1. 所有 JSONL Manager 都在 `source_code/` 目录
2. 它们会被 `app.py` 自动导入使用
3. 确保数据目录存在: `mkdir -p /home/user/webapp/data/{gdrive_jsonl,sar_jsonl,escape_signal_jsonl,...}`

#### 2.3 数据读取器 (Daily Readers)
```
source_code/
├── escape_signal_daily_reader.py       # 逃顶信号日数据读取
├── anchor_daily_reader.py              # 锚点日数据读取
├── extreme_daily_reader.py             # 极值日数据读取
└── sar_slope_daily_reader.py           # SAR 斜率日数据读取
```

#### 2.4 监控和工具
```
source_code/
├── system_health_monitor.py            # 系统健康监控
├── data_health_monitor.py              # 数据健康监控
├── major_events_monitor.py             # 重大事件监控
├── anchor_warning_monitor.py           # 锚点警告监控
└── 其他工具脚本...
```

---

### 3. Web 模板目录 (379 个 HTML 文件)

#### 3.1 主要页面
```
templates/
├── index.html                          # 首页 (系统入口)
├── panic_new.html                      # 恐慌清洗指数 (v2.9-自定义标签) ✨ 已优化
├── coin_change_tracker.html            # 27币涨跌追踪 ✨ 已修复 tooltip
├── monitor_charts.html                 # 监控图表集合
├── check_memory_leak.html              # 内存泄漏检测 ✨ 新增
├── sar_bias_trend.html                 # SAR 偏向趋势图 (24小时分页)
├── anchor_system_real.html             # 锚点系统 (实盘)
├── anchor_system_paper.html            # 锚点系统 (模拟)
├── signal_timeline.html                # 信号时间线
├── escape_signal.html                  # 逃顶信号
└── 其他页面... (30+)
```

**重新部署说明**:
1. 复制整个 `templates/` 到 `/home/user/webapp/`
2. Flask 会自动从 `templates/` 目录加载模板
3. 访问: `http://localhost:5000/` 查看首页

#### 3.2 页面路由对应关系
| 页面文件 | 访问路由 | 功能说明 |
|---------|---------|---------|
| `index.html` | `/` | 系统首页，所有模块入口 |
| `panic_new.html` | `/panic` | 恐慌指数，1小时爆仓数据可视化 |
| `coin_change_tracker.html` | `/coin-change-tracker` | 27币涨跌幅追踪 |
| `sar_bias_trend.html` | `/sar-bias-trend` | SAR偏多/偏空趋势，24小时分页 |
| `check_memory_leak.html` | `/check-memory-leak` | 系统内存和进程监控 |
| `monitor_charts.html` | `/monitor-charts` | 综合监控图表 |
| `anchor_system_real.html` | `/anchor-system-real` | 锚点系统（实盘） |
| `signal_timeline.html` | `/signal-timeline` | 信号时间线 |
| `escape_signal.html` | `/escape-signal` | 逃顶信号分析 |

---

### 4. 静态资源目录 (Static Files)
```
static/                                 # 如果存在
├── css/                                # 样式文件
├── js/                                 # JavaScript 文件
└── images/                             # 图片资源
```

**重新部署说明**:
1. 如果备份中有 `static/` 目录，复制到 `/home/user/webapp/`
2. Flask 会自动从 `/static` 路由提供静态文件

---

### 5. 数据文件 (Data - 最近7天)

#### 5.1 数据目录结构
```
data/                                   # 总大小 ~2.7 GB (压缩后 ~800MB)
├── sar_bias_stats/                     # SAR 偏向统计 (~6 MB)
│   ├── bias_stats_20260201.jsonl       # 2026-02-01 数据
│   ├── bias_stats_20260202.jsonl       # 2026-02-02 数据
│   ├── bias_stats_20260203.jsonl
│   ├── bias_stats_20260204.jsonl
│   ├── bias_stats_20260205.jsonl
│   ├── bias_stats_20260206.jsonl
│   └── bias_stats_20260207.jsonl       # 最新数据
│
├── escape_signal_jsonl/                # 逃顶信号数据 (~12 MB)
│   ├── escape_signal_peaks.jsonl       # 峰值数据 (6.7KB)
│   ├── escape_signal_stats.jsonl       # 统计数据 (1.9MB, 7837条)
│   └── escape_signal_stats_backup_...  # 备份 (11MB)
│
├── sar_jsonl/                          # SAR 指标数据 (~100 MB)
│   ├── sar_*.jsonl                     # 按日期命名
│   └── ...
│
├── sar_slope_jsonl/                    # SAR 斜率数据 (~116 MB)
│   ├── sar_slope_*.jsonl
│   └── ...
│
├── panic_jsonl/                        # 恐慌指数数据
│   ├── panic_20260207.jsonl            # 最新恐慌数据
│   └── ...
│
├── coin_change_tracker/                # 币种变化追踪 (~34 MB)
│   ├── changes_20260207.jsonl
│   └── ...
│
├── gdrive_jsonl/                       # Google Drive 数据 (~87 MB)
│   └── ...
│
├── support_resistance_jsonl/           # 支撑/阻力数据 (~740 MB)
│   └── ...
│
├── support_resistance_daily/           # 支撑/阻力日数据 (~977 MB)
│   └── ...
│
├── anchor_daily/                       # 锚点日数据 (~191 MB)
│   └── ...
│
├── anchor_profit_stats/                # 锚点利润统计 (~163 MB)
│   └── ...
│
└── ... (其他数据目录)
```

**数据字段说明**:

**SAR 偏向统计** (`sar_bias_stats/*.jsonl`):
```json
{
  "timestamp": 1707292837,
  "timestamp_iso": "2026-02-07 00:00:37",
  "bullish_count": 0,
  "bearish_count": 2,
  "avg_bullish_ratio": 39.38,
  "avg_bearish_ratio": 60.62,
  "total_symbols": 27,
  "success_count": 27,
  "fail_count": 0,
  "bullish_symbols": [],
  "bearish_symbols": ["{BTC, 81.82}", "{AAVE, 81.82}", ...]
}
```

**逃顶信号统计** (`escape_signal_jsonl/escape_signal_stats.jsonl`):
```json
{
  "stat_time": "2026-02-07 08:39:04",
  "signal_24h_count": 27,
  "signal_2h_count": 0,
  "decline_strength_level": 0,
  "rise_strength_level": 0,
  "max_signal_24h": 27,
  "max_signal_2h": 0,
  "created_at": "2026-02-07 08:39:04"
}
```

**重新部署说明**:
1. 创建数据目录: `mkdir -p /home/user/webapp/data`
2. 解压后，复制所有数据: `cp -r data/* /home/user/webapp/data/`
3. 设置权限: `chmod -R 755 /home/user/webapp/data`
4. 验证数据:
   ```bash
   # 查看 SAR 偏向最新数据
   tail -1 /home/user/webapp/data/sar_bias_stats/bias_stats_20260207.jsonl
   
   # 查看逃顶信号统计
   tail -1 /home/user/webapp/data/escape_signal_jsonl/escape_signal_stats.jsonl
   
   # 统计数据文件数
   find /home/user/webapp/data -name "*.jsonl" | wc -l
   ```

---

### 6. 配置文件 (Config Files)

#### 6.1 已备份的配置
```
config_backup/
├── *.json                              # JSON 配置文件 (2个)
└── *.conf                              # Conf 配置文件 (如果存在)
```

#### 6.2 需要手动创建的配置 ⚠️
```
.env                                    # 环境变量 (未备份，包含敏感信息)
```

**.env 文件模板**:
```bash
# OKX API 配置
OKX_API_KEY=your_api_key_here
OKX_SECRET_KEY=your_secret_key_here
OKX_PASSPHRASE=your_passphrase_here

# Telegram Bot 配置
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# 服务器配置
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

# 数据路径
DATA_DIR=/home/user/webapp/data
```

**重新部署说明**:
1. 创建 `.env`: `nano /home/user/webapp/.env`
2. 填入上述配置
3. 设置权限: `chmod 600 /home/user/webapp/.env`
4. 验证: `cat /home/user/webapp/.env` (确保格式正确)

---

### 7. PM2 配置和进程管理

#### 7.1 PM2 配置文件
```
ecosystem.config.js                     # PM2 进程配置
pm2_config/
├── dump.pm2                            # PM2 进程快照
├── pm2_list.txt                        # 进程列表文本
└── pm2_prettylist.json                 # 进程列表 JSON
```

#### 7.2 PM2 进程列表 (25 个采集器)
```
1.  flask-app                           # Flask 主应用 (端口 5000)
2.  sar-collector                       # SAR 采集器
3.  sar-bias-stats-collector            # SAR 偏向统计 (每5分钟)
4.  sar-slope-collector                 # SAR 斜率采集器 (stopped)
5.  sar-slope-updater                   # SAR 斜率更新器
6.  panic-wash-collector                # 恐慌指数采集器
7.  coin-change-tracker                 # 币种变化追踪
8.  signal-collector                    # 信号采集器
9.  signal-timeline-collector           # 信号时间线
10. gdrive-detector                     # Google Drive 检测器
11. gdrive-jsonl-manager                # GDrive 数据管理
12. dashboard-jsonl-manager             # 仪表板数据管理
13. crypto-index-collector              # 加密指数采集
14. financial-indicators-collector      # 金融指标采集
15. liquidation-1h-collector            # 1小时爆仓采集
16. okx-day-change-collector            # OKX 日变化采集
17. price-baseline-collector            # 价格基线采集
18. price-speed-collector               # 价格速度采集
19. price-development-collector         # 价格发展采集
20. v1v2-collector                      # V1V2 采集器
21. sr-v2-daemon                        # 支撑阻力 V2 守护进程
22. system-health-monitor               # 系统健康监控
23. data-health-monitor                 # 数据健康监控
24. major-events-monitor                # 重大事件监控
25. (其他采集器...)
```

**重新部署说明**:
1. 安装 PM2: `npm install -g pm2`
2. 启动所有服务: `pm2 start ecosystem.config.js`
3. 保存进程列表: `pm2 save`
4. 设置开机启动: `pm2 startup`
5. 验证: `pm2 list`
6. 查看日志: `pm2 logs flask-app`

**PM2 内存限制配置**:
```javascript
// ecosystem.config.js 中的关键配置
{
  name: 'flask-app',
  max_memory_restart: '500M',  // 内存超过 500MB 自动重启
  autorestart: true,           // 崩溃后自动重启
  watch: false                 // 生产环境不监控文件变化
}
```

---

### 8. 文档和说明 (24+ 个 Markdown 文件)

#### 8.1 部署和使用文档
```
docs/
├── README.md                           # 项目说明
├── BACKUP_AND_DEPLOYMENT_GUIDE.md      # 备份和部署完整指南 ✨
├── BACKUP_MANIFEST.md                  # 备份清单 (本文档) ✨
├── DEPLOYMENT_SUCCESS.md               # 部署成功报告
└── CLAUDE.md                           # Claude AI 开发指令
```

#### 8.2 修复和优化报告
```
docs/
├── MODULE_FIX_REPORT.md                # 模块修复报告 ✨
├── SYSTEM_HEALTH_CHECK_REPORT.md       # 系统健康检查 ✨
├── MEMORY_LEAK_DIAGNOSTIC_REPORT.md    # 内存泄漏诊断 ✨
├── SAR_BIAS_COLLECTION_OPTIMIZATION.md # SAR 采集优化 ✨
├── GDRIVE_DETECTOR_COMPLETE_FIX_REPORT.md
├── LIQUIDATION_CHART_ENHANCEMENT.md
├── COIN_CHANGE_TRACKER_ENHANCEMENT.md
├── FIXES_REPORT_20260207.md
└── 其他修复报告...
```

#### 8.3 系统架构和功能文档
```
docs/
├── ESCAPE_SIGNAL_V2_REBUILD_PLAN.md
├── OKX_ACCOUNT_CONFIG_REPORT.md
└── 其他文档...
```

**重新部署说明**:
1. 所有文档都在备份的 `docs/` 目录
2. 建议将文档放在 `/home/user/webapp/docs/` 方便查阅
3. 首先阅读: `BACKUP_AND_DEPLOYMENT_GUIDE.md`

---

### 9. 系统信息快照
```
SYSTEM_INFO.txt                         # 系统配置快照
pip_packages.txt                        # Python 包列表
```

**包含信息**:
- 备份时间和版本
- 系统信息 (OS, 内核, 架构)
- 软件版本 (Python, Node, PM2, Git)
- Python 包完整列表
- PM2 进程状态
- 资源使用情况 (磁盘, 内存, CPU)
- 重要文件路径
- 数据目录结构

---

### 10. 自动部署脚本
```
deploy.sh                               # 自动部署脚本 (可执行)
```

**脚本功能**:
1. 检查目标目录
2. 复制核心文件
3. 复制源代码和模板
4. 恢复数据文件
5. 安装 Python 依赖
6. 检查/安装 PM2
7. 创建必要目录
8. 提供配置提示

**使用方法**:
```bash
# 解压备份
tar -xzf crypto_analysis_system_backup_20260208_000149.tar.gz
cd backup_temp_20260208_000149

# 运行自动部署
./deploy.sh

# 按提示完成后续配置
```

---

## 🚀 完整重新部署流程

### 第一步: 准备新服务器

#### 1.1 系统要求
- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- 最小 4GB RAM (推荐 8GB+)
- 最小 20GB 磁盘空间 (推荐 50GB+)
- Python 3.10+
- Node.js 18+

#### 1.2 安装基础软件
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3
sudo apt install python3 python3-pip python3-venv -y

# 安装 Node.js 和 npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# 安装 Git
sudo apt install git -y

# 安装其他依赖
sudo apt install build-essential curl wget -y

# 安装 PM2
sudo npm install -g pm2
```

---

### 第二步: 解压和部署备份

#### 2.1 传输备份文件
```bash
# 方法1: 使用 scp
scp crypto_analysis_system_backup_20260208_000149.tar.gz user@newserver:/tmp/

# 方法2: 使用 wget (如果备份在云端)
wget https://your-cloud-storage/crypto_analysis_system_backup_20260208_000149.tar.gz -P /tmp/
```

#### 2.2 解压备份
```bash
cd /tmp
tar -xzf crypto_analysis_system_backup_20260208_000149.tar.gz
cd backup_temp_20260208_000149
```

#### 2.3 运行自动部署
```bash
# 使用自动部署脚本
./deploy.sh
```

#### 2.4 或手动部署
```bash
# 创建项目目录
mkdir -p /home/user/webapp
cd /home/user/webapp

# 复制核心文件
cp /tmp/backup_temp_20260208_000149/app.py .
cp /tmp/backup_temp_20260208_000149/ecosystem.config.js .
cp /tmp/backup_temp_20260208_000149/requirements.txt .

# 复制目录
cp -r /tmp/backup_temp_20260208_000149/source_code .
cp -r /tmp/backup_temp_20260208_000149/templates .
cp -r /tmp/backup_temp_20260208_000149/data .

# 创建必要目录
mkdir -p logs
```

---

### 第三步: 安装依赖

#### 3.1 Python 依赖
```bash
cd /home/user/webapp

# 方法1: 使用虚拟环境 (推荐)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 方法2: 全局安装
pip3 install -r requirements.txt
```

#### 3.2 验证安装
```bash
# 验证关键包
python3 -c "import flask; print('Flask OK')"
python3 -c "import requests; print('Requests OK')"
python3 -c "from source_code.escape_signal_jsonl_manager import EscapeSignalJSONLManager; print('JSONL Manager OK')"
```

---

### 第四步: 配置系统

#### 4.1 创建 .env 文件
```bash
cd /home/user/webapp
cat > .env << 'EOF'
# OKX API 配置
OKX_API_KEY=your_api_key_here
OKX_SECRET_KEY=your_secret_key_here
OKX_PASSPHRASE=your_passphrase_here

# Telegram Bot 配置
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# 服务器配置
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

# 数据路径
DATA_DIR=/home/user/webapp/data
EOF

# 设置权限
chmod 600 .env
```

#### 4.2 验证配置
```bash
# 检查 .env 文件
cat .env

# 测试配置加载
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('OKX_API_KEY')[:10] if os.getenv('OKX_API_KEY') else 'Not set')"
```

---

### 第五步: 启动服务

#### 5.1 使用 PM2 启动
```bash
cd /home/user/webapp

# 启动所有服务
pm2 start ecosystem.config.js

# 保存进程列表
pm2 save

# 设置开机启动
pm2 startup
# 按提示执行命令
```

#### 5.2 查看服务状态
```bash
# 查看所有进程
pm2 list

# 查看 Flask 日志
pm2 logs flask-app --lines 50

# 查看特定采集器
pm2 logs sar-bias-stats-collector --lines 20

# 实时监控
pm2 monit
```

---

### 第六步: 验证部署

#### 6.1 测试 Flask 服务
```bash
# 测试首页
curl http://localhost:5000/

# 测试 API
curl http://localhost:5000/api/latest
curl http://localhost:5000/api/sar-bias-trend
curl http://localhost:5000/api/coin-change-tracker/latest
curl http://localhost:5000/api/escape-signal-stats?limit=1
curl http://localhost:5000/api/system/memory
```

#### 6.2 验证数据采集
```bash
# 查看 SAR 偏向最新数据
cd /home/user/webapp
tail -1 data/sar_bias_stats/bias_stats_$(date +%Y%m%d).jsonl | python3 -m json.tool

# 查看逃顶信号最新数据
tail -1 data/escape_signal_jsonl/escape_signal_stats.jsonl | python3 -m json.tool

# 监控采集器日志
pm2 logs sar-bias-stats-collector --lines 20
```

#### 6.3 访问 Web 界面
使用浏览器访问以下页面:
- 首页: http://your-server:5000/
- 恐慌指数: http://your-server:5000/panic
- SAR 偏向: http://your-server:5000/sar-bias-trend
- 币种追踪: http://your-server:5000/coin-change-tracker
- 内存监控: http://your-server:5000/check-memory-leak

---

## 🔧 故障排除

### 常见问题及解决方案

#### 问题 1: Flask 无法启动
```bash
# 检查端口占用
sudo lsof -i :5000
# 如果被占用，杀掉进程
sudo kill -9 <PID>

# 检查 Python 版本
python3 --version  # 需要 3.10+

# 检查依赖
pip3 list | grep Flask

# 查看错误日志
pm2 logs flask-app --err --lines 100
```

#### 问题 2: 采集器频繁重启
```bash
# 查看重启原因
pm2 info sar-collector

# 检查内存使用
pm2 list  # 查看 memory 列

# 增加内存限制
pm2 stop sar-collector
pm2 delete sar-collector
pm2 start source_code/sar_collector.py --name sar-collector --interpreter python3 --max-memory-restart 500M
```

#### 问题 3: 数据不更新
```bash
# 检查采集器状态
pm2 list | grep collector

# 查看采集器日志
pm2 logs sar-bias-stats-collector --lines 50

# 手动运行测试
python3 source_code/sar_bias_stats_collector.py
```

#### 问题 4: API 返回 500 错误
```bash
# 查看错误日志
pm2 logs flask-app --err --lines 100

# 测试模块导入
python3 -c "from source_code.escape_signal_jsonl_manager import EscapeSignalJSONLManager"

# 测试 API
curl -v http://localhost:5000/api/escape-signal-stats?limit=1
```

#### 问题 5: 缺少数据文件
```bash
# 创建数据目录
mkdir -p /home/user/webapp/data/{sar_bias_stats,escape_signal_jsonl,panic_jsonl,coin_change_tracker}

# 验证权限
chmod -R 755 /home/user/webapp/data

# 检查数据目录
ls -lh /home/user/webapp/data/
```

---

## 📊 系统监控

### 监控工具

#### 1. 内存监控页面
访问: http://your-server:5000/check-memory-leak
- 实时内存使用
- 进程重启统计
- 内存排行榜
- 自动告警

#### 2. PM2 监控
```bash
# 实时监控
pm2 monit

# 进程列表
pm2 list

# 日志查看
pm2 logs

# 清空日志
pm2 flush
```

#### 3. 系统资源监控
```bash
# 内存
free -h

# 磁盘
df -h

# CPU
top

# 网络
netstat -tulpn | grep LISTEN
```

---

## 📝 重要注意事项

### ⚠️ 配置文件
- `.env` 文件包含敏感信息，**未包含在备份中**
- 需要手动创建并配置 OKX API 和 Telegram Bot
- 设置正确的权限: `chmod 600 .env`

### 📊 数据说明
- 备份包含最近 7 天的数据文件
- 完整历史数据需单独备份
- 数据文件压缩前 ~2.7GB，压缩后 ~800MB

### 🔧 PM2 配置
- `max_memory_restart`: 内存限制，防止内存泄漏
- `autorestart`: 自动重启崩溃的进程
- `watch`: 生产环境应设置为 `false`

### 🚀 性能优化
- Flask 生产环境建议使用 Gunicorn + Nginx
- 数据采集间隔可根据需求调整
- PM2 cluster 模式可提高并发性能

### 🔒 安全建议
- 使用防火墙限制端口访问
- 定期更新依赖包
- 使用 HTTPS 加密通信
- 定期备份数据

---

## 📞 支持与文档

### 相关文档
1. **BACKUP_AND_DEPLOYMENT_GUIDE.md** - 详细部署指南
2. **MODULE_FIX_REPORT.md** - 模块修复报告
3. **SYSTEM_HEALTH_CHECK_REPORT.md** - 系统健康报告
4. **SAR_BIAS_COLLECTION_OPTIMIZATION.md** - SAR 采集优化

### 日志位置
- PM2 日志: `~/.pm2/logs/`
- 应用日志: `/home/user/webapp/logs/`
- 系统日志: `/var/log/syslog`

### 监控端点
- 内存监控: http://localhost:5000/check-memory-leak
- 系统 API: http://localhost:5000/api/system/memory
- 进程 API: http://localhost:5000/api/system/processes

---

## 📋 版本信息

- **备份版本**: 20260208_000149
- **创建日期**: 2026-02-08 00:02:59
- **备份大小**: 224 MB (压缩)
- **总文件数**: 1,145
- **系统版本**: 加密货币数据分析系统 v2.9+
- **最后更新**: 2026-02-08

---

## ✅ 检查清单

部署完成后，请确认以下事项:

- [ ] 基础软件已安装 (Python 3.10+, Node.js 18+, PM2)
- [ ] 备份文件已解压
- [ ] 核心文件已复制到 `/home/user/webapp/`
- [ ] Python 依赖已安装 (`pip3 install -r requirements.txt`)
- [ ] `.env` 文件已创建并配置
- [ ] 数据目录已恢复 (`data/` 目录存在)
- [ ] PM2 已安装 (`pm2 --version`)
- [ ] 所有服务已启动 (`pm2 list`)
- [ ] Flask 正常响应 (`curl http://localhost:5000/`)
- [ ] API 正常工作 (`curl http://localhost:5000/api/latest`)
- [ ] 数据采集正常 (查看日志 `pm2 logs`)
- [ ] Web 界面可访问 (浏览器打开)
- [ ] PM2 已设置开机启动 (`pm2 startup`)
- [ ] 进程列表已保存 (`pm2 save`)

---

**备份清单文档版本**: v1.0  
**文档更新日期**: 2026-02-08  
**适用系统**: 加密货币数据分析系统 v2.9+  
