# 加密货币监控系统完整部署指南

## 文档版本
- **版本**: 2.0
- **更新日期**: 2026-02-06
- **备份日期**: 2026-02-06 18:45
- **系统版本**: v2.1

---

## 📋 目录

1. [系统概述](#系统概述)
2. [系统架构](#系统架构)
3. [文件结构](#文件结构)
4. [依赖环境](#依赖环境)
5. [部署步骤](#部署步骤)
6. [PM2进程配置](#pm2进程配置)
7. [Flask路由映射](#flask路由映射)
8. [数据库与存储](#数据库与存储)
9. [配置文件说明](#配置文件说明)
10. [服务管理](#服务管理)
11. [故障排查](#故障排查)
12. [备份恢复](#备份恢复)

---

## 系统概述

### 项目信息
- **项目名称**: 加密货币监控与交易系统
- **主要功能**: 
  - 27个币种实时涨跌幅追踪
  - 9大重大事件监控与预警
  - SAR技术指标分析
  - 支撑压力线系统
  - 爆仓数据监控
  - 恐慌指数追踪
  - Telegram自动推送

### 技术栈
- **后端**: Python 3.12 + Flask
- **前端**: HTML + Tailwind CSS + ECharts
- **进程管理**: PM2
- **数据存储**: JSONL + SQLite
- **缓存**: 内存缓存
- **通知**: Telegram Bot API

### 系统规模
```
文件类型          数量    总大小    占比
─────────────────────────────────────
Python文件        88      ~5MB     核心逻辑
Markdown文档      440     ~15MB    系统文档
HTML模板          88      ~2MB     Web界面
配置文件          15+     <1MB     系统配置
数据文件          数千    ~9GB     历史数据
─────────────────────────────────────
总计              616+    ~9.3GB   完整项目
```

---

## 系统架构

### 整体架构图
```
┌─────────────────────────────────────────────────────────────┐
│                         用户浏览器                            │
│  (HTML Templates + ECharts + Tailwind CSS)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/HTTPS
┌──────────────────────┴──────────────────────────────────────┐
│                    Flask Web Server                          │
│  (app.py - 20000+ lines, 100+ routes)                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  API Endpoints                                         │ │
│  │  - /api/coin-change-tracker/*                          │ │
│  │  - /api/panic/*                                        │ │
│  │  - /api/sar-slope/*                                    │ │
│  │  - /api/major-events/*                                 │ │
│  │  - /api/anchor-system/*                                │ │
│  │  - /api/support-resistance/*                           │ │
│  │  - ... (100+ endpoints)                                │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                    PM2 Process Manager                        │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐  │
│  │ Flask App      │ │ Data Collectors│ │ Monitors       │  │
│  │ (port 5000)    │ │ (23 processes) │ │ (5 processes)  │  │
│  └────────────────┘ └────────────────┘ └────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                    Data Layer                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌────────────────┐ │
│  │ JSONL Files     │ │ SQLite DB       │ │ Cache          │ │
│  │ (~9GB)          │ │ (SAR data)      │ │ (Memory)       │ │
│  └─────────────────┘ └─────────────────┘ └────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                    External Services                          │
│  ┌─────────────────┐ ┌─────────────────┐ ┌────────────────┐ │
│  │ OKX Exchange    │ │ Telegram Bot    │ │ Google Drive   │ │
│  │ (Market Data)   │ │ (Notifications) │ │ (Backup)       │ │
│  └─────────────────┘ └─────────────────┘ └────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

### 进程架构
```
PM2 进程列表 (29个进程)
├── flask-app (主应用)
├── 数据采集器 (17个)
│   ├── coin-change-tracker (27币涨跌幅)
│   ├── coin-price-tracker (币价追踪)
│   ├── liquidation-1h-collector (1小时爆仓)
│   ├── panic-collector (恐慌指数)
│   ├── sar-collector (SAR指标)
│   ├── sar-bias-stats-collector (SAR偏向统计)
│   ├── support-resistance-snapshot (支撑压力线)
│   ├── anchor-profit-monitor (锚定系统)
│   ├── escape-signal-calculator (逃顶信号)
│   ├── extreme-value-tracker (极值追踪)
│   ├── financial-indicators-collector (金融指标)
│   ├── price-baseline-collector (价格基准)
│   ├── price-speed-collector (价格速度)
│   ├── crypto-index-collector (加密指数)
│   ├── okx-day-change-collector (OKX日涨跌)
│   ├── v1v2-collector (V1V2数据)
│   └── gdrive-txt-refresh (Google Drive刷新)
│
├── 监控系统 (5个)
│   ├── major-events-monitor (重大事件监控)
│   ├── data-health-monitor (数据健康监控)
│   ├── system-health-monitor (系统健康监控)
│   ├── escape-signal-monitor (逃顶信号监控)
│   └── fear-greed-collector (恐惧贪婪采集)
│
└── 其他服务 (7个)
    └── (可选服务)
```

---

## 文件结构

### 项目根目录 `/home/user/webapp`
```
webapp/
├── app.py                          # Flask主应用 (20000+ lines)
├── app_new.py                      # 备用应用
├── ecosystem.config.js             # PM2配置文件
├── requirements.txt                # Python依赖
├── package.json                    # Node.js依赖
│
├── templates/                      # HTML模板 (88个)
│   ├── index.html                  # 主页
│   ├── coin_change_tracker.html    # 27币追踪
│   ├── panic_new.html              # 恐慌指数
│   ├── major_events.html           # 重大事件
│   ├── anchor_system.html          # 锚定系统
│   ├── sar_bias_trend.html         # SAR偏向
│   ├── support_resistance.html     # 支撑压力
│   ├── telegram_notification_settings.html  # TG通知设置
│   └── ... (81个其他模板)
│
├── major-events-system/            # 重大事件系统
│   ├── major_events_monitor.py     # 9个事件监控核心
│   ├── major_events.html           # 事件页面
│   └── data/
│       ├── major_events.jsonl      # 事件记录
│       └── monitor_state.json      # 监控状态
│
├── data/                           # 数据目录 (~9GB)
│   ├── coin_change_tracker/        # 27币涨跌幅数据
│   ├── coin_price_tracker/         # 币价数据
│   ├── liquidation_1h/             # 1小时爆仓数据
│   ├── panic_daily/                # 恐慌指数数据
│   ├── sar_jsonl/                  # SAR数据 (27个币种)
│   ├── sar_bias_stats/             # SAR偏向统计
│   ├── support_resistance_daily/   # 支撑压力数据
│   ├── anchor_daily/               # 锚定系统数据
│   ├── anchor_profit_stats/        # 盈利统计
│   ├── escape_signal_jsonl/        # 逃顶信号数据
│   ├── extreme_tracking/           # 极值追踪数据
│   ├── financial_indicators/       # 金融指标数据
│   ├── price_comparison_jsonl/     # 价格对比数据
│   ├── price_speed_jsonl/          # 价格速度数据
│   ├── crypto_index_jsonl/         # 加密指数数据
│   ├── okx_trading_jsonl/          # OKX交易数据
│   ├── v1v2_jsonl/                 # V1V2数据
│   ├── data_health_monitor_state.json
│   └── system_health_state.json
│
├── databases/                      # SQLite数据库
│   └── sar_slope_data.db           # SAR斜率数据库
│
├── logs/                           # 日志目录
│   ├── flask_app.log
│   ├── coin_change_tracker.log
│   ├── major_events.log
│   └── ... (各个服务的日志)
│
├── source_code/                    # 核心源代码
│   ├── coin_change_tracker.py
│   ├── panic_collector.py
│   ├── sar_collector.py
│   ├── support_resistance_snapshot.py
│   ├── anchor_profit_monitor.py
│   ├── escape_signal_calculator.py
│   ├── extreme_value_tracker.py
│   ├── data_health_monitor.py
│   ├── system_health_monitor.py
│   └── templates/
│
├── docs/                           # 文档目录 (440+ MD文件)
│   ├── 系统实现报告/
│   ├── 功能更新文档/
│   ├── 修复报告/
│   ├── 部署指南/
│   └── API文档/
│
├── config/                         # 配置文件
│   ├── telegram_config.json
│   ├── telegram_notification_config.json
│   └── system_config.json
│
└── test/                           # 测试脚本
    ├── test_event*.py
    ├── test_telegram*.py
    └── ...
```

---

## 依赖环境

### 系统要求
- **操作系统**: Ubuntu 20.04+ / Debian 11+
- **Python**: 3.12+
- **Node.js**: 16+ (用于PM2)
- **内存**: 最低4GB，推荐8GB+
- **磁盘**: 最低20GB可用空间

### Python依赖 (requirements.txt)
```txt
Flask==3.1.0
flask-cors==4.0.0
requests==2.32.3
pandas==2.2.3
numpy==2.1.3
python-dateutil==2.9.0
pytz==2024.2
ccxt==4.4.28
schedule==1.2.2
APScheduler==3.10.4
google-api-python-client==2.154.0
google-auth-httplib2==0.2.0
google-auth-oauthlib==1.2.1
sqlite3 (内置)
```

### 系统依赖
```bash
# APT包
sudo apt-get update
sudo apt-get install -y \
    python3.12 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    git \
    curl \
    wget \
    supervisor \
    nginx (可选)
```

### Node.js依赖
```bash
npm install -g pm2
pm2 install pm2-logrotate  # 日志轮转
```

---

## 部署步骤

### 步骤1: 环境准备
```bash
# 1.1 创建工作目录
sudo mkdir -p /home/user
cd /home/user

# 1.2 恢复备份
cd /tmp
tar -xzf webapp_complete_backup_20260206.tar.gz -C /home/user/

# 1.3 进入项目目录
cd /home/user/webapp

# 1.4 设置权限
sudo chown -R $USER:$USER /home/user/webapp
chmod +x *.py
chmod +x source_code/*.py
```

### 步骤2: 安装Python依赖
```bash
# 2.1 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 2.2 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 2.3 验证安装
python -c "import flask; print(flask.__version__)"
python -c "import pandas; print(pandas.__version__)"
```

### 步骤3: 配置PM2
```bash
# 3.1 安装PM2（如果未安装）
npm install -g pm2

# 3.2 启动所有服务
cd /home/user/webapp
pm2 start ecosystem.config.js

# 3.3 设置开机自启动
pm2 startup
pm2 save

# 3.4 验证服务状态
pm2 list
pm2 logs --lines 20
```

### 步骤4: 配置Telegram
```bash
# 4.1 编辑Telegram配置
nano config/telegram_config.json

# 配置内容:
{
    "bot_token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID",
    "enabled": true
}

# 4.2 测试Telegram连接
python test/test_telegram_webhook.py
```

### 步骤5: 验证部署
```bash
# 5.1 检查Flask应用
curl http://localhost:5000/
curl http://localhost:5000/api/health

# 5.2 检查数据采集器
pm2 logs coin-change-tracker --lines 20
pm2 logs major-events-monitor --lines 20

# 5.3 检查数据文件
ls -lh data/coin_change_tracker/
ls -lh data/major-events-system/data/
```

### 步骤6: 配置反向代理（可选）
```nginx
# /etc/nginx/sites-available/webapp
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# 启用站点
sudo ln -s /etc/nginx/sites-available/webapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## PM2进程配置

### ecosystem.config.js 完整配置
```javascript
module.exports = {
  apps: [
    // ==================== Flask Web Server ====================
    {
      name: 'flask-app',
      script: 'app.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '2G',
      env: {
        FLASK_APP: 'app.py',
        FLASK_ENV: 'production',
        PYTHONUNBUFFERED: '1'
      },
      error_file: '/home/user/webapp/logs/flask-app-error.log',
      out_file: '/home/user/webapp/logs/flask-app-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss'
    },

    // ==================== 数据采集器 ====================
    {
      name: 'coin-change-tracker',
      script: 'source_code/coin_change_tracker.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_memory_restart: '512M'
    },
    
    {
      name: 'coin-price-tracker',
      script: 'source_code/coin_price_tracker.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_memory_restart: '256M'
    },

    {
      name: 'liquidation-1h-collector',
      script: 'source_code/liquidation_1h_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_memory_restart: '256M'
    },

    {
      name: 'panic-collector',
      script: 'source_code/panic_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_memory_restart: '256M'
    },

    {
      name: 'sar-collector',
      script: 'source_code/sar_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_memory_restart: '512M'
    },

    {
      name: 'sar-bias-stats-collector',
      script: 'source_code/sar_bias_stats_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_memory_restart: '256M'
    },

    {
      name: 'support-resistance-snapshot',
      script: 'source_code/support_resistance_snapshot.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_memory_restart: '512M'
    },

    {
      name: 'anchor-profit-monitor',
      script: 'source_code/anchor_profit_monitor.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_memory_restart: '512M'
    },

    // ==================== 监控系统 ====================
    {
      name: 'major-events-monitor',
      script: 'major-events-system/major_events_monitor.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_memory_restart: '512M'
    },

    {
      name: 'data-health-monitor',
      script: 'source_code/data_health_monitor.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_memory_restart: '256M'
    },

    // ... 其他进程配置 ...
  ]
};
```

### PM2命令速查
```bash
# 启动服务
pm2 start ecosystem.config.js          # 启动所有服务
pm2 start ecosystem.config.js --only flask-app  # 只启动特定服务

# 管理服务
pm2 stop all                           # 停止所有服务
pm2 restart all                        # 重启所有服务
pm2 reload all                         # 0秒停机重载
pm2 delete all                         # 删除所有服务

# 查看状态
pm2 list                               # 列出所有进程
pm2 status                             # 查看状态
pm2 monit                              # 实时监控

# 查看日志
pm2 logs                               # 查看所有日志
pm2 logs flask-app                     # 查看特定服务日志
pm2 logs --lines 100                   # 查看最后100行
pm2 flush                              # 清空日志

# 保存配置
pm2 save                               # 保存当前进程列表
pm2 startup                            # 生成开机自启动脚本
```

---

## Flask路由映射

### 主要页面路由 (40+)
```python
# 主页和导航
@app.route('/')                        # 系统主页
@app.route('/index')                   # 主页别名

# 核心监控页面
@app.route('/coin-change-tracker')     # 27币涨跌幅追踪
@app.route('/panic')                   # 恐慌清洗指数
@app.route('/major-events')            # 9大重大事件
@app.route('/anchor-system')           # 锚定系统
@app.route('/sar-bias-trend')          # SAR偏向趋势
@app.route('/support-resistance')      # 支撑压力线
@app.route('/price-comparison')        # 比价系统
@app.route('/escape-signal')           # 逃顶信号
@app.route('/extreme-tracking')        # 极值追踪

# 管理和设置
@app.route('/telegram-notification-settings')  # TG通知设置
@app.route('/telegram-dashboard')              # TG推送历史
@app.route('/data-health-monitor')             # 数据健康监控
@app.route('/system-status')                   # 系统状态
@app.route('/control-center')                  # 控制中心
```

### API路由分类 (100+)

#### 1. 币价与涨跌幅 API
```python
# 27币涨跌幅追踪
GET  /api/coin-change-tracker/latest          # 最新数据
GET  /api/coin-change-tracker/history         # 历史数据
GET  /api/coin-change-tracker/chart-data      # 图表数据

# 币价追踪
GET  /api/coin-price/latest                   # 最新价格
GET  /api/coin-price/history                  # 历史价格
GET  /api/coin-price/30min                    # 30分钟数据
```

#### 2. 爆仓与恐慌 API
```python
# 恐慌清洗指数
GET  /api/panic/latest                        # 最新恐慌指数
GET  /api/panic/history                       # 历史记录
GET  /api/panic/hour1-curve                   # 1小时爆仓曲线

# 爆仓数据
GET  /api/liquidation/1h                      # 1小时爆仓金额
GET  /api/liquidation/history                 # 历史爆仓数据
```

#### 3. SAR指标 API
```python
# SAR斜率
GET  /api/sar-slope/latest                    # 最新SAR数据
GET  /api/sar-slope/history/<symbol>          # 历史SAR数据
GET  /api/sar-slope/bias-stats                # 偏向统计
GET  /api/sar-slope/bias-trend-by-date        # 按日期统计
GET  /api/sar-slope/current-cycle/<symbol>    # 当前周期
GET  /api/sar-slope/conversions               # 多空转换点
```

#### 4. 重大事件 API
```python
# 9大事件监控
GET  /api/major-events/current-status         # 当前状态
GET  /api/major-events/history                # 历史事件
GET  /api/major-events/stats                  # 统计数据
GET  /api/major-events/latest-triggers        # 最近触发
```

#### 5. 支撑压力线 API
```python
# 支撑压力
GET  /api/support-resistance/latest           # 最新数据
GET  /api/support-resistance/history          # 历史数据
GET  /api/support-resistance/stats            # 统计信息
```

#### 6. 锚定系统 API
```python
# 锚定盈利系统
GET  /api/anchor-system/profit-stats          # 盈利统计
GET  /api/anchor-system/profit-history        # 盈利历史
GET  /api/anchor-system/positions             # 持仓信息
GET  /api/anchor-system/profit-records        # 盈利记录
```

#### 7. Telegram API
```python
# 通知管理
GET  /api/telegram/notification-config        # 获取通知配置
POST /api/telegram/notification-config        # 更新通知配置
GET  /api/telegram/status                     # Telegram状态
GET  /api/telegram/history                    # 推送历史
GET  /api/telegram/signals/*                  # 各类信号数据
```

#### 8. 系统监控 API
```python
# 数据健康
GET  /api/data-health-monitor/status          # 健康状态
GET  /api/data-health-monitor/logs            # 健康日志
POST /api/data-health-monitor/restart         # 重启服务

# 系统状态
GET  /api/system/health                       # 系统健康
GET  /api/system/status                       # 系统状态
GET  /api/system/metrics                      # 系统指标
```

### 路由与进程对应关系
```
页面路由                     →  API端点                          →  数据源进程
─────────────────────────────────────────────────────────────────────────────
/coin-change-tracker        →  /api/coin-change-tracker/*      →  coin-change-tracker
/panic                      →  /api/panic/*                    →  panic-collector + liquidation-1h-collector
/major-events               →  /api/major-events/*             →  major-events-monitor
/sar-bias-trend             →  /api/sar-slope/*                →  sar-collector + sar-bias-stats-collector
/support-resistance         →  /api/support-resistance/*       →  support-resistance-snapshot
/anchor-system              →  /api/anchor-system/*            →  anchor-profit-monitor
/price-comparison           →  /api/price-comparison/*         →  price-baseline-collector
/telegram-notification-settings  →  /api/telegram/*            →  各个监控系统
/data-health-monitor        →  /api/data-health-monitor/*      →  data-health-monitor
```

---

## 数据库与存储

### JSONL数据文件
```
数据类型                文件路径                              更新频率    保留期限
───────────────────────────────────────────────────────────────────────────
27币涨跌幅              data/coin_change_tracker/            1分钟       永久
                       coin_change_YYYYMMDD.jsonl

币价数据                data/coin_price_tracker/             30秒        永久
                       coin_prices_30min.jsonl

1小时爆仓               data/liquidation_1h/                 1分钟       永久
                       liquidation_1h.jsonl

恐慌指数                data/panic_daily/                    1分钟       永久
                       panic_YYYYMMDD.jsonl

SAR数据                 data/sar_jsonl/                      5分钟       永久
                       {SYMBOL}.jsonl (27个文件)

SAR偏向统计             data/sar_bias_stats/                 1分钟       永久
                       bias_stats_YYYYMMDD.jsonl

支撑压力                data/support_resistance_daily/       1小时       永久
                       support_resistance_YYYYMMDD.jsonl

锚定系统                data/anchor_daily/                   实时        永久
                       anchor_data_YYYYMMDD.jsonl

                       data/anchor_profit_stats/            实时        永久
                       anchor_profit_stats.jsonl

重大事件                major-events-system/data/            实时        永久
                       major_events.jsonl

监控状态                major-events-system/data/            实时        永久
                       monitor_state.json
```

### SQLite数据库
```
数据库                  路径                                  用途
─────────────────────────────────────────────────────────────
SAR斜率数据             databases/sar_slope_data.db          存储SAR斜率历史数据
                                                             支持高效查询和聚合
```

### 数据目录结构
```
/home/user/webapp/data/
├── coin_change_tracker/        # 每日一个文件
│   ├── coin_change_20260206.jsonl
│   └── ...
├── panic_daily/                # 每日一个文件
│   ├── panic_20260206.jsonl
│   └── ...
├── sar_jsonl/                  # 每个币种一个文件
│   ├── BTC.jsonl
│   ├── ETH.jsonl
│   ├── XRP.jsonl
│   └── ... (27个币种)
└── [其他数据目录]/
```

### 数据清理策略
```bash
# 清理30天前的数据（谨慎操作）
find /home/user/webapp/data/ -name "*.jsonl" -mtime +30 -delete

# 清理日志文件（保留7天）
find /home/user/webapp/logs/ -name "*.log" -mtime +7 -delete

# 压缩历史数据
find /home/user/webapp/data/ -name "*.jsonl" -mtime +7 -exec gzip {} \;
```

---

## 配置文件说明

### 1. Telegram配置
**文件**: `config/telegram_config.json`
```json
{
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "chat_id": "YOUR_CHAT_ID_HERE",
    "enabled": true,
    "retry_count": 3,
    "timeout": 10
}
```

### 2. Telegram通知开关配置
**文件**: `telegram_notification_config.json`
```json
{
    "major_events": {
        "event1": {"name": "高强度见顶诱多", "enabled": true},
        "event2": {"name": "一般强度见顶诱多", "enabled": true},
        "event3": {"name": "强空头爆仓", "enabled": true},
        "event4": {"name": "弱空头爆仓", "enabled": false},
        "event5": {"name": "绿色信号转红色信号", "enabled": true},
        "event6": {"name": "红色信号转绿色信号", "enabled": true},
        "event7": {"name": "一般逃顶事件", "enabled": true},
        "event8": {"name": "一般抄底事件", "enabled": true},
        "event9": {"name": "超强爆仓之后的主跌", "enabled": true}
    },
    "extreme_tracking": {"enabled": false, "name": "极值追踪系统提醒"},
    "support_resistance": {"enabled": true, "name": "支撑压力线系统"},
    "alert_system": {"enabled": true, "name": "计次预警系统"},
    "trading_signals": {"enabled": true, "name": "交易信号系统"}
}
```

### 3. PM2生态系统配置
**文件**: `ecosystem.config.js`
- 详见"PM2进程配置"章节

### 4. Flask应用配置
**文件**: `app.py` 中的配置部分
```python
# 开发/生产环境切换
DEBUG = False
HOST = '0.0.0.0'
PORT = 5000

# 数据目录配置
DATA_DIR = '/home/user/webapp/data'
LOG_DIR = '/home/user/webapp/logs'

# 缓存配置
CACHE_TIMEOUT = 60  # 秒

# 时区配置
TIMEZONE = 'Asia/Shanghai'
```

---

## 服务管理

### Flask应用管理
```bash
# 启动/停止/重启
pm2 start flask-app
pm2 stop flask-app
pm2 restart flask-app

# 查看日志
pm2 logs flask-app --lines 100

# 查看详细信息
pm2 show flask-app

# 监控资源使用
pm2 monit
```

### 数据采集器管理
```bash
# 启动所有采集器
pm2 start ecosystem.config.js

# 重启特定采集器
pm2 restart coin-change-tracker
pm2 restart major-events-monitor

# 停止所有采集器（保留Flask）
pm2 stop all
pm2 start flask-app
```

### 日志管理
```bash
# 查看实时日志
pm2 logs --lines 50

# 查看特定服务日志
pm2 logs flask-app
pm2 logs major-events-monitor

# 清空日志
pm2 flush

# 配置日志轮转
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 100M
pm2 set pm2-logrotate:retain 7
```

### 数据备份
```bash
# 每日备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup"

# 备份数据目录
tar -czf ${BACKUP_DIR}/data_${DATE}.tar.gz /home/user/webapp/data/

# 备份数据库
cp /home/user/webapp/databases/sar_slope_data.db ${BACKUP_DIR}/sar_${DATE}.db

# 删除7天前的备份
find ${BACKUP_DIR} -name "*.tar.gz" -mtime +7 -delete
find ${BACKUP_DIR} -name "*.db" -mtime +7 -delete

# 添加到crontab
# 0 2 * * * /home/user/scripts/daily_backup.sh
```

---

## 故障排查

### 常见问题

#### 1. Flask应用无法启动
```bash
# 检查端口占用
netstat -tlnp | grep 5000
lsof -i:5000

# 检查Python依赖
pip list | grep Flask
python3 -c "import flask; print(flask.__version__)"

# 查看错误日志
pm2 logs flask-app --err --lines 50
tail -f /home/user/webapp/logs/flask-app-error.log

# 手动启动测试
cd /home/user/webapp
python3 app.py
```

#### 2. 数据采集器停止工作
```bash
# 检查进程状态
pm2 list
pm2 status coin-change-tracker

# 查看日志
pm2 logs coin-change-tracker --lines 100

# 重启服务
pm2 restart coin-change-tracker

# 检查数据文件更新时间
ls -lt /home/user/webapp/data/coin_change_tracker/ | head -5
```

#### 3. Telegram通知失败
```bash
# 测试Telegram配置
cd /home/user/webapp
python3 test/test_telegram_webhook.py

# 检查网络连接
curl https://api.telegram.org

# 验证配置文件
cat config/telegram_config.json
cat telegram_notification_config.json
```

#### 4. 内存占用过高
```bash
# 查看进程内存
pm2 list

# 重启内存占用高的进程
pm2 restart major-events-monitor

# 设置内存限制
pm2 restart flask-app --max-memory-restart 2G

# 清理缓存
pm2 flush
```

#### 5. 磁盘空间不足
```bash
# 检查磁盘使用
df -h
du -sh /home/user/webapp/data/*

# 清理日志
pm2 flush
find /home/user/webapp/logs/ -name "*.log" -mtime +7 -delete

# 压缩历史数据
find /home/user/webapp/data/ -name "*.jsonl" -mtime +30 -exec gzip {} \;
```

### 日志分析
```bash
# Flask应用日志
tail -f /home/user/webapp/logs/flask-app-out.log
tail -f /home/user/webapp/logs/flask-app-error.log

# PM2日志
pm2 logs flask-app --lines 100
pm2 logs --err --lines 50

# 系统日志
journalctl -u pm2-$USER --since today
```

---

## 备份恢复

### 完整备份
```bash
# 创建完整备份
cd /home/user
tar -czf webapp_complete_backup_$(date +%Y%m%d).tar.gz \
    --exclude='webapp/.git' \
    --exclude='webapp/__pycache__' \
    --exclude='webapp/*.pyc' \
    --exclude='webapp/venv' \
    webapp/

# 备份到远程（可选）
rsync -avz webapp_complete_backup_*.tar.gz user@remote:/backup/
```

### 仅备份数据
```bash
# 备份数据目录
tar -czf webapp_data_backup_$(date +%Y%m%d).tar.gz \
    /home/user/webapp/data/ \
    /home/user/webapp/databases/ \
    /home/user/webapp/major-events-system/data/
```

### 仅备份代码
```bash
# 备份代码和配置
tar -czf webapp_code_backup_$(date +%Y%m%d).tar.gz \
    --exclude='webapp/data' \
    --exclude='webapp/logs' \
    --exclude='webapp/__pycache__' \
    --exclude='webapp/*.pyc' \
    --exclude='webapp/venv' \
    /home/user/webapp/
```

### 恢复步骤
```bash
# 1. 停止所有服务
pm2 stop all

# 2. 备份当前数据（以防万一）
mv /home/user/webapp /home/user/webapp.old

# 3. 恢复备份
cd /home/user
tar -xzf /tmp/webapp_complete_backup_20260206.tar.gz

# 4. 恢复权限
chown -R $USER:$USER /home/user/webapp
chmod +x /home/user/webapp/*.py
chmod +x /home/user/webapp/source_code/*.py

# 5. 安装依赖
cd /home/user/webapp
pip install -r requirements.txt

# 6. 启动服务
pm2 start ecosystem.config.js
pm2 save

# 7. 验证恢复
pm2 list
curl http://localhost:5000/
```

---

## 附录

### A. 快速启动脚本
```bash
#!/bin/bash
# 文件: /home/user/scripts/start_all.sh

cd /home/user/webapp
pm2 start ecosystem.config.js
pm2 save
echo "✅ 所有服务已启动"
pm2 list
```

### B. 快速停止脚本
```bash
#!/bin/bash
# 文件: /home/user/scripts/stop_all.sh

pm2 stop all
echo "⏸️  所有服务已停止"
pm2 list
```

### C. 健康检查脚本
```bash
#!/bin/bash
# 文件: /home/user/scripts/health_check.sh

echo "检查Flask应用..."
curl -f http://localhost:5000/ > /dev/null 2>&1 && echo "✅ Flask正常" || echo "❌ Flask异常"

echo "检查PM2进程..."
pm2 list | grep online && echo "✅ PM2进程正常"

echo "检查磁盘空间..."
df -h / | tail -1
```

### D. 联系信息
- **技术支持**: support@example.com
- **文档更新**: 2026-02-06
- **系统版本**: v2.1

---

**文档结束**
