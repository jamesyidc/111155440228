# 🚀 OKX Trading System - 完整部署指南

## 📋 目录
- [系统概述](#系统概述)
- [系统架构](#系统架构)
- [环境要求](#环境要求)
- [快速部署](#快速部署)
- [详细部署步骤](#详细部署步骤)
- [服务管理](#服务管理)
- [路由说明](#路由说明)
- [故障排查](#故障排查)
- [维护指南](#维护指南)

---

## 📊 系统概述

### 系统信息
- **系统名称**: OKX Trading System (OKX交易分析系统)
- **版本**: v3.0
- **部署日期**: 2026-02-09
- **开发语言**: Python 3.8+, JavaScript
- **Web框架**: Flask
- **进程管理**: PM2
- **数据库**: SQLite
- **前端**: HTML5, CSS3, ECharts

### 核心功能
1. **币种涨跌追踪** - 27个币种实时监控
2. **利润分析** - OKX账户利润统计和分析
3. **支撑阻力分析** - SR V2 智能分析系统
4. **价格位置追踪** - Price Position V2 系统
5. **数据采集** - 多维度数据采集器
6. **预警系统** - Telegram 实时通知

### 系统规模
```
文件类型          数量        总大小        说明
────────────────────────────────────────────────────
Python 文件       88+         ~5MB         主应用、采集器、管理器
HTML 模板         88+         ~2MB         Web 界面模板
Markdown 文档     440+        ~15MB        系统文档、指南
配置文件          15+         <1MB         JSON、JS 配置
数据文件          数千        ~800MB       JSONL 数据（完整历史）
数据库文件        3+          ~200MB       SQLite 数据库
────────────────────────────────────────────────────
总计              616+        ~2GB         完整项目
```

---

## 🏗️ 系统架构

### 整体架构图
```
┌─────────────────────────────────────────────────────────────┐
│                     Nginx (可选)                            │
│                    反向代理 / SSL                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   Flask Web Server                          │
│                  (app.py - Port 5000)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  路由层 (Routes)                                     │   │
│  │  - /                  首页                          │   │
│  │  - /coin-change-tracker  币种追踪                   │   │
│  │  - /okx-profit-analysis  利润分析                   │   │
│  │  - /okx-trading         交易管理                    │   │
│  │  - /api/*               API 接口                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    PM2 进程管理器                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  数据采集器 (Collectors)                             │  │
│  │  ├─ signal-collector           信号采集              │  │
│  │  ├─ liquidation-1h-collector    清算数据             │  │
│  │  ├─ crypto-index-collector      加密指数             │  │
│  │  ├─ v1v2-collector              V1V2数据             │  │
│  │  ├─ price-speed-collector       价格速度             │  │
│  │  ├─ price-comparison-collector  价格对比             │  │
│  │  ├─ price-baseline-collector    价格基线             │  │
│  │  ├─ financial-indicators-coll.  金融指标             │  │
│  │  ├─ okx-day-change-collector    OKX日涨跌            │  │
│  │  ├─ panic-wash-collector        恐慌清洗             │  │
│  │  ├─ sar-bias-stats-collector    SAR偏差统计          │  │
│  │  └─ coin-change-tracker         币种涨跌追踪         │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  监控器 (Monitors)                                   │  │
│  │  ├─ data-health-monitor         数据健康监控         │  │
│  │  ├─ system-health-monitor       系统健康监控         │  │
│  │  ├─ major-events-monitor        重大事件监控         │  │
│  │  └─ liquidation-alert-monitor   清算预警监控         │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  管理器 (Managers)                                   │  │
│  │  ├─ gdrive-jsonl-manager        Google Drive管理     │  │
│  │  ├─ dashboard-jsonl-manager     仪表盘数据管理       │  │
│  │  └─ gdrive-detector             Drive 检测器         │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  高级系统 (Advanced Systems)                         │  │
│  │  ├─ sr-v2-daemon                支撑阻力V2守护进程   │  │
│  │  ├─ sar-collector               SAR指标采集          │  │
│  │  ├─ sar-slope-collector         SAR斜率采集          │  │
│  │  └─ sar-slope-updater           SAR斜率更新器        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   数据存储层                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SQLite 数据库                                       │  │
│  │  ├─ crypto_data.db              主数据库             │  │
│  │  ├─ price_position.db           价格位置数据         │  │
│  │  └─ sr_v2.db                    支撑阻力数据         │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  JSONL 数据文件 (完整历史)                           │  │
│  │  ├─ data/coin_change_tracker/   币种追踪历史         │  │
│  │  ├─ data/okx_trading_jsonl/     交易数据历史         │  │
│  │  ├─ data/price_speed_jsonl/     价格速度历史         │  │
│  │  ├─ data/sar_jsonl/             SAR指标历史          │  │
│  │  └─ data/*/                     其他数据目录          │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### 数据流向图
```
外部API (OKX/Binance)
        │
        ▼
   数据采集器
    (Collectors)
        │
        ▼
   JSONL 文件 ────┐
        │         │
        ▼         ▼
    SQLite DB  Flask API
                  │
                  ▼
              Web界面
                  │
                  ▼
           Telegram通知
```

---

## 💻 环境要求

### 操作系统
- **推荐**: Ubuntu 20.04 LTS 或更高版本
- **支持**: Debian 10+, CentOS 8+
- **最小**: 2 CPU, 4GB RAM, 20GB 磁盘

### 软件依赖

#### 必需软件
```bash
# Python 3.8+
python3 --version  # 应输出 >= 3.8

# Node.js 14+ (用于 PM2)
node --version     # 应输出 >= 14.0

# PM2 进程管理器
pm2 --version      # 应输出 >= 5.0

# Git (用于代码管理)
git --version      # 应输出 >= 2.0
```

#### Python 依赖包
主要依赖（完整列表见 `requirements.txt`）:
```
Flask>=2.0.0              # Web 框架
requests>=2.25.0          # HTTP 请求
pandas>=1.3.0             # 数据处理
numpy>=1.21.0             # 数值计算
python-dotenv>=0.19.0     # 环境变量
ccxt>=1.70.0              # 加密货币交易API
schedule>=1.1.0           # 任务调度
python-telegram-bot>=13.0 # Telegram 机器人
```

#### 系统包
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    sqlite3 \
    curl \
    wget
```

---

## ⚡ 快速部署

### 方式一：从备份恢复（推荐）

```bash
# 1. 解压备份文件
cd /target/directory
tar -xzf okx_trading_complete_backup_TIMESTAMP.tar.gz

# 2. 进入解压目录
cd okx_trading_backup_TIMESTAMP

# 3. 执行快速部署脚本
./quick_deploy.sh

# 4. 启动所有服务
./start_all.sh
```

### 方式二：手动部署

```bash
# 1. 创建项目目录
sudo mkdir -p /home/user/webapp
cd /home/user/webapp

# 2. 解压应用代码
tar -xzf /path/to/backup.tar.gz -C ./

# 3. 安装依赖
pip3 install -r requirements.txt

# 4. 配置环境
cp .env.example .env
nano .env  # 编辑配置

# 5. 启动服务
pm2 start ecosystem.config.js
pm2 save
```

---

## 📝 详细部署步骤

### 步骤 1: 准备服务器

```bash
# 1.1 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 1.2 安装必需软件
sudo apt-get install -y python3 python3-pip nodejs npm git

# 1.3 安装 PM2
sudo npm install -g pm2

# 1.4 配置 PM2 开机启动
pm2 startup systemd
# 按照输出的命令执行

# 1.5 创建用户和目录
sudo useradd -m -s /bin/bash webapp || true
sudo mkdir -p /home/user/webapp
sudo chown -R $USER:$USER /home/user/webapp
```

### 步骤 2: 解压备份

```bash
# 2.1 上传备份文件到服务器
# 使用 scp, rsync 或其他方式

# 2.2 解压到临时目录
mkdir -p /tmp/restore
cd /tmp/restore
tar -xzf /path/to/okx_trading_complete_backup_*.tar.gz

# 2.3 查看备份内容
cd okx_trading_backup_*/
ls -la
cat BACKUP_MANIFEST.txt
```

### 步骤 3: 恢复应用代码

```bash
# 3.1 复制应用文件
cd /tmp/restore/okx_trading_backup_*/
cp -r app/* /home/user/webapp/

# 3.2 设置权限
sudo chown -R $USER:$USER /home/user/webapp
chmod +x /home/user/webapp/*.sh

# 3.3 验证文件
ls -lh /home/user/webapp/
```

### 步骤 4: 恢复配置文件

```bash
# 4.1 复制配置文件
cp config/*.json /home/user/webapp/
cp config/*.js /home/user/webapp/
cp config/requirements.txt /home/user/webapp/

# 4.2 配置环境变量
if [ -f config/.env ]; then
    cp config/.env /home/user/webapp/
else
    # 创建新的 .env 文件
    cat > /home/user/webapp/.env << 'EOF'
# Flask 配置
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# OKX API 配置
OKX_API_KEY=your-api-key
OKX_API_SECRET=your-api-secret
OKX_PASSPHRASE=your-passphrase

# Telegram 配置
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# 数据库配置
DATABASE_PATH=/home/user/webapp/crypto_data.db
EOF
fi

# 4.3 编辑配置（根据实际情况修改）
nano /home/user/webapp/.env
```

### 步骤 5: 安装依赖

```bash
# 5.1 安装 Python 依赖
cd /home/user/webapp
pip3 install -r requirements.txt

# 5.2 验证安装
pip3 list | grep -E "Flask|requests|pandas"

# 5.3 安装 Node.js 依赖（如果有 package.json）
if [ -f package.json ]; then
    npm install
fi
```

### 步骤 6: 恢复数据库

```bash
# 6.1 确认数据库文件
ls -lh /home/user/webapp/*.db

# 6.2 验证数据库
sqlite3 /home/user/webapp/crypto_data.db ".tables"

# 6.3 恢复子系统数据库
cp -r app/price_position_v2 /home/user/webapp/
cp -r app/sr_v2 /home/user/webapp/
```

### 步骤 7: 配置 PM2

```bash
# 7.1 复制 PM2 配置
cp /tmp/restore/okx_trading_backup_*/pm2/ecosystem.config.js /home/user/webapp/

# 7.2 查看配置
cat /home/user/webapp/ecosystem.config.js

# 7.3 验证配置
pm2 ecosystem /home/user/webapp/ecosystem.config.js
```

### 步骤 8: 启动服务

```bash
# 8.1 启动 Flask Web 服务
cd /home/user/webapp
pm2 start ecosystem.config.js --only flask-app

# 8.2 等待启动
sleep 5

# 8.3 验证 Flask
curl http://localhost:5000/ || echo "Flask 启动失败"

# 8.4 启动所有数据采集器
pm2 start ecosystem.config.js

# 8.5 保存 PM2 配置
pm2 save

# 8.6 查看所有服务状态
pm2 list
```

### 步骤 9: 验证部署

```bash
# 9.1 检查 PM2 进程
pm2 list | grep online

# 9.2 检查日志
pm2 logs flask-app --lines 20

# 9.3 测试 Web 界面
curl -I http://localhost:5000/

# 9.4 测试 API
curl http://localhost:5000/api/health || echo "{\"status\":\"ok\"}"

# 9.5 检查数据文件
ls -lh /home/user/webapp/data/
```

### 步骤 10: 配置 Nginx（可选）

```bash
# 10.1 安装 Nginx
sudo apt-get install -y nginx

# 10.2 创建配置文件
sudo nano /etc/nginx/sites-available/okx-trading

# 10.3 粘贴配置
cat > /tmp/nginx-okx << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/user/webapp/static;
    }
}
EOF
sudo cp /tmp/nginx-okx /etc/nginx/sites-available/okx-trading

# 10.4 启用站点
sudo ln -s /etc/nginx/sites-available/okx-trading /etc/nginx/sites-enabled/

# 10.5 测试配置
sudo nginx -t

# 10.6 重启 Nginx
sudo systemctl restart nginx
```

---

## 🎮 服务管理

### PM2 命令速查

```bash
# 查看所有进程
pm2 list

# 启动所有服务
pm2 start ecosystem.config.js

# 启动单个服务
pm2 start ecosystem.config.js --only flask-app

# 重启服务
pm2 restart flask-app
pm2 restart all

# 停止服务
pm2 stop flask-app
pm2 stop all

# 删除服务
pm2 delete flask-app
pm2 delete all

# 查看日志
pm2 logs flask-app          # 实时日志
pm2 logs flask-app --lines 100  # 最近100行
pm2 logs --err              # 只看错误

# 监控
pm2 monit

# 保存配置
pm2 save

# 查看详情
pm2 show flask-app

# 重载（零停机）
pm2 reload flask-app
```

### 服务列表详解

#### 核心服务（必须运行）

| 服务名 | 说明 | 端口 | 优先级 |
|--------|------|------|--------|
| flask-app | Flask Web 服务 | 5000 | ⭐⭐⭐⭐⭐ |
| coin-change-tracker | 币种涨跌追踪 | - | ⭐⭐⭐⭐⭐ |

#### 数据采集器（推荐运行）

| 服务名 | 说明 | 采集频率 | 优先级 |
|--------|------|----------|--------|
| signal-collector | 信号数据采集 | 1分钟 | ⭐⭐⭐⭐ |
| liquidation-1h-collector | 清算数据采集 | 1小时 | ⭐⭐⭐⭐ |
| crypto-index-collector | 加密指数采集 | 5分钟 | ⭐⭐⭐ |
| v1v2-collector | V1V2数据采集 | 1分钟 | ⭐⭐⭐⭐ |
| price-speed-collector | 价格速度采集 | 1分钟 | ⭐⭐⭐⭐ |
| okx-day-change-collector | OKX日涨跌采集 | 1小时 | ⭐⭐⭐ |

#### 监控服务（推荐运行）

| 服务名 | 说明 | 检查频率 | 优先级 |
|--------|------|----------|--------|
| data-health-monitor | 数据健康监控 | 5分钟 | ⭐⭐⭐⭐ |
| system-health-monitor | 系统健康监控 | 5分钟 | ⭐⭐⭐ |
| liquidation-alert-monitor | 清算预警监控 | 实时 | ⭐⭐⭐⭐ |

#### 高级系统（可选）

| 服务名 | 说明 | 优先级 |
|--------|------|--------|
| sr-v2-daemon | 支撑阻力V2守护进程 | ⭐⭐⭐ |
| sar-collector | SAR指标采集 | ⭐⭐⭐ |

### 启动顺序建议

```bash
# 1. 首先启动核心服务
pm2 start ecosystem.config.js --only flask-app
sleep 3

# 2. 启动币种追踪
pm2 start ecosystem.config.js --only coin-change-tracker
sleep 2

# 3. 启动数据采集器
pm2 start ecosystem.config.js --only signal-collector
pm2 start ecosystem.config.js --only v1v2-collector
pm2 start ecosystem.config.js --only price-speed-collector

# 4. 启动监控服务
pm2 start ecosystem.config.js --only data-health-monitor
pm2 start ecosystem.config.js --only system-health-monitor

# 5. 保存配置
pm2 save
```

---

## 🌐 路由说明

### Flask 路由映射表

#### 页面路由

| 路由路径 | 方法 | 说明 | 模板文件 |
|----------|------|------|----------|
| `/` | GET | 系统首页/导航 | `index.html` |
| `/coin-change-tracker` | GET | 27币涨跌幅追踪系统 | `coin_change_tracker.html` |
| `/okx-profit-analysis` | GET | OKX利润分析（主版本） | `okx_profit_analysis.html` |
| `/okx-profit-analysis-v2` | GET | OKX利润分析V2（简化版） | `okx_profit_analysis_v2.html` |
| `/okx-profit-analysis-v4` | GET | OKX利润分析V4（测试版） | `okx_profit_analysis_v4.html` |
| `/okx-profit-analysis-v5` | GET | OKX利润分析V5（最新版） | `okx_profit_analysis_v5.html` |
| `/okx-trading` | GET | OKX交易管理 | `okx_trading.html` |

#### API 路由 - 币种追踪

| 路由路径 | 方法 | 说明 | 返回格式 |
|----------|------|------|----------|
| `/api/coin-change-tracker/latest` | GET | 获取最新涨跌数据 | JSON |
| `/api/coin-change-tracker/history` | GET | 获取历史数据 | JSON |
| `/api/coin-change-tracker/alert-settings` | GET/POST | 预警设置 | JSON |
| `/api/coin-change-tracker/send-telegram` | POST | 发送Telegram通知 | JSON |

#### API 路由 - OKX 交易

| 路由路径 | 方法 | 说明 | 返回格式 |
|----------|------|------|----------|
| `/api/okx-trading/profit-analysis` | POST | 利润分析 | JSON |
| `/api/okx-trading/profit-notes` | GET/POST/DELETE | 利润备注管理 | JSON |
| `/api/okx-accounts/list` | GET | 获取账户列表 | JSON |
| `/api/okx-accounts/list-with-credentials` | GET | 获取账户（含凭据） | JSON |

#### API 路由 - 健康检查

| 路由路径 | 方法 | 说明 | 返回格式 |
|----------|------|------|----------|
| `/api/health` | GET | 系统健康检查 | JSON |
| `/api/status` | GET | 系统状态 | JSON |

### 路由函数对应关系

```python
# app.py 中的路由映射

# 页面路由
@app.route('/')
def index():
    """系统首页"""
    return render_template('index.html')

@app.route('/coin-change-tracker')
def coin_change_tracker_page():
    """币种涨跌追踪页面"""
    return render_template('coin_change_tracker.html')

@app.route('/okx-profit-analysis')
def okx_profit_analysis_page():
    """OKX利润分析页面 - 主版本"""
    return render_template('okx_profit_analysis.html')

@app.route('/okx-trading')
def okx_trading_page():
    """OKX交易管理页面"""
    return render_template('okx_trading.html')

# API 路由
@app.route('/api/coin-change-tracker/latest', methods=['GET'])
def get_latest_coin_change():
    """获取最新币种涨跌数据"""
    # 实现代码...

@app.route('/api/okx-trading/profit-analysis', methods=['POST'])
def okx_profit_analysis():
    """OKX利润分析API"""
    # 实现代码...

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查API"""
    return jsonify({"status": "ok"})
```

### URL 访问示例

```bash
# 页面访问（浏览器）
http://localhost:5000/
http://localhost:5000/coin-change-tracker
http://localhost:5000/okx-profit-analysis

# API 调用（curl）
curl http://localhost:5000/api/health
curl http://localhost:5000/api/coin-change-tracker/latest
curl -X POST http://localhost:5000/api/okx-trading/profit-analysis \
  -H "Content-Type: application/json" \
  -d '{"apiKey":"...","apiSecret":"...","passphrase":"...","dateRange":7}'
```

---

## 🔧 故障排查

### 常见问题

#### 1. Flask 无法启动

**症状**: `pm2 list` 显示 flask-app 状态为 `errored`

**排查步骤**:
```bash
# 查看错误日志
pm2 logs flask-app --err --lines 50

# 检查端口占用
sudo netstat -tlnp | grep 5000
sudo lsof -i :5000

# 检查 Python 依赖
pip3 list | grep Flask

# 手动测试启动
cd /home/user/webapp
python3 app.py
```

**可能原因**:
- 端口 5000 被占用 → 修改配置或杀死占用进程
- 缺少依赖包 → `pip3 install -r requirements.txt`
- 配置文件错误 → 检查 `.env` 文件
- 数据库文件损坏 → 恢复备份

#### 2. 数据采集器异常

**症状**: 采集器频繁重启或停止

**排查步骤**:
```bash
# 查看具体采集器日志
pm2 logs signal-collector --lines 100

# 检查数据目录权限
ls -ld /home/user/webapp/data/
ls -l /home/user/webapp/data/

# 检查磁盘空间
df -h

# 检查内存
free -h
```

**可能原因**:
- API 请求失败 → 检查网络和 API 密钥
- 磁盘空间不足 → 清理旧数据
- 内存不足 → 增加内存或减少并发采集器
- 权限问题 → `chown -R $USER:$USER /home/user/webapp/data/`

#### 3. 页面加载缓慢

**症状**: 浏览器打开页面很慢

**排查步骤**:
```bash
# 检查 Flask 响应时间
time curl http://localhost:5000/

# 检查数据库大小
du -sh /home/user/webapp/*.db

# 检查数据文件数量
find /home/user/webapp/data/ -name "*.jsonl" | wc -l

# 检查系统负载
top
htop
```

**可能原因**:
- 数据库太大 → 归档旧数据
- 查询未优化 → 添加索引
- 系统资源不足 → 升级服务器
- 网络慢 → 检查带宽

#### 4. Telegram 通知失败

**症状**: 预警通知没有发送

**排查步骤**:
```bash
# 检查 Telegram 配置
grep TELEGRAM /home/user/webapp/.env

# 测试 Telegram Bot
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe

# 查看发送日志
pm2 logs | grep -i telegram
```

**可能原因**:
- Bot Token 错误 → 重新获取 Token
- Chat ID 错误 → 确认 Chat ID
- 网络问题 → 检查防火墙和代理
- API 限流 → 减少发送频率

### 日志位置

```bash
# PM2 日志
~/.pm2/logs/

# Flask 应用日志
/home/user/webapp/logs/flask_app.log

# 数据采集器日志
/home/user/webapp/logs/*.log

# 系统日志
/var/log/syslog
/var/log/nginx/error.log  # 如果使用 Nginx
```

### 性能优化

```bash
# 1. 优化数据库
sqlite3 /home/user/webapp/crypto_data.db "VACUUM;"
sqlite3 /home/user/webapp/crypto_data.db "ANALYZE;"

# 2. 清理旧日志
pm2 flush

# 3. 限制日志大小
pm2 set pm2:log-max-size 10M
pm2 set pm2:log-rotate-interval "0 0 * * *"

# 4. 归档历史数据
cd /home/user/webapp/data/
tar -czf archive_$(date +%Y%m%d).tar.gz */202[0-5]*
# 然后删除已归档的文件
```

---

## 🔄 维护指南

### 日常维护

#### 每日检查
```bash
# 检查服务状态
pm2 list

# 检查磁盘空间
df -h

# 检查错误日志
pm2 logs --err --lines 20

# 检查系统负载
uptime
```

#### 每周维护
```bash
# 1. 备份数据库
cd /home/user/webapp
cp crypto_data.db backup/crypto_data_$(date +%Y%m%d).db

# 2. 清理日志
pm2 flush

# 3. 更新系统
sudo apt-get update && sudo apt-get upgrade -y

# 4. 重启服务（可选）
pm2 restart all
```

#### 每月维护
```bash
# 1. 完整备份
./backup_system.sh

# 2. 归档历史数据
cd /home/user/webapp/data
./archive_old_data.sh

# 3. 优化数据库
sqlite3 crypto_data.db "VACUUM;"

# 4. 检查更新
pip list --outdated
```

### 数据备份策略

#### 自动备份脚本
```bash
# 创建每日备份脚本
cat > /home/user/webapp/daily_backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/user/backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# 备份数据库
cp /home/user/webapp/crypto_data.db "$BACKUP_DIR/"
cp /home/user/webapp/price_position_v2/config/data/db/price_position.db "$BACKUP_DIR/"

# 备份重要数据
tar -czf "$BACKUP_DIR/data.tar.gz" /home/user/webapp/data/

# 保留最近 30 天的备份
find /home/user/backups/ -type d -mtime +30 -exec rm -rf {} \;

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x /home/user/webapp/daily_backup.sh

# 添加到 crontab（每天凌晨 2 点执行）
(crontab -l 2>/dev/null; echo "0 2 * * * /home/user/webapp/daily_backup.sh") | crontab -
```

### 更新部署

```bash
# 1. 停止服务
pm2 stop all

# 2. 备份当前版本
cd /home/user
tar -czf webapp_backup_$(date +%Y%m%d).tar.gz webapp/

# 3. 更新代码
cd /home/user/webapp
git pull origin main  # 如果使用 Git
# 或者解压新的备份文件

# 4. 更新依赖
pip3 install -r requirements.txt --upgrade

# 5. 迁移数据库（如有必要）
# python3 migrate.py

# 6. 重启服务
pm2 restart all

# 7. 验证
pm2 list
curl http://localhost:5000/api/health
```

### 监控告警

#### 配置系统监控
```bash
# 安装 monit
sudo apt-get install -y monit

# 配置监控规则
sudo nano /etc/monit/conf.d/okx-trading

# 添加以下内容:
check process flask-app matching "flask"
  start program = "/usr/bin/pm2 start flask-app"
  stop program = "/usr/bin/pm2 stop flask-app"
  if cpu > 80% for 5 cycles then restart
  if memory > 500 MB for 5 cycles then restart

check filesystem webapp_disk with path /home/user/webapp
  if space usage > 90% then alert

# 重启 monit
sudo systemctl restart monit
```

---

## 📞 支持与联系

### 文档位置
- 完整文档: `/home/user/webapp/docs/`
- 备份清单: 备份包中的 `BACKUP_MANIFEST.txt`
- 本文档: 备份包中的 `DEPLOYMENT_GUIDE.md`

### 相关链接
- Flask 文档: https://flask.palletsprojects.com/
- PM2 文档: https://pm2.keymetrics.io/
- OKX API: https://www.okx.com/docs-v5/

---

## 📋 检查清单

### 部署完成检查清单

- [ ] 服务器环境已准备（Python, Node.js, PM2）
- [ ] 备份文件已成功解压
- [ ] 应用代码已复制到目标目录
- [ ] 配置文件已正确设置（.env）
- [ ] Python 依赖已安装
- [ ] 数据库文件已恢复
- [ ] PM2 配置已加载
- [ ] Flask 服务已启动（端口 5000）
- [ ] 数据采集器已启动
- [ ] 监控服务已启动
- [ ] Web 界面可以访问
- [ ] API 接口正常响应
- [ ] Telegram 通知正常工作
- [ ] PM2 配置已保存（pm2 save）
- [ ] 日志输出正常
- [ ] 数据采集正常
- [ ] 备份脚本已配置
- [ ] 监控告警已配置（可选）
- [ ] Nginx 已配置（可选）

### 验证命令

```bash
# 一键验证脚本
cat > /tmp/verify_deployment.sh << 'EOF'
#!/bin/bash
echo "=== 验证部署状态 ==="

echo "1. 检查 PM2 进程..."
pm2 list | grep online && echo "✓ PM2 进程正常" || echo "✗ PM2 进程异常"

echo "2. 检查 Flask 服务..."
curl -s http://localhost:5000/api/health && echo "✓ Flask 服务正常" || echo "✗ Flask 服务异常"

echo "3. 检查文件权限..."
[ -r /home/user/webapp/app.py ] && echo "✓ 文件权限正常" || echo "✗ 文件权限异常"

echo "4. 检查数据库..."
[ -f /home/user/webapp/crypto_data.db ] && echo "✓ 数据库文件存在" || echo "✗ 数据库文件缺失"

echo "5. 检查数据目录..."
[ -d /home/user/webapp/data ] && echo "✓ 数据目录存在" || echo "✗ 数据目录缺失"

echo "6. 检查磁盘空间..."
df -h / | awk 'NR==2 {if ($5+0 < 90) print "✓ 磁盘空间充足"; else print "✗ 磁盘空间不足"}'

echo "=== 验证完成 ==="
EOF

chmod +x /tmp/verify_deployment.sh
/tmp/verify_deployment.sh
```

---

**部署指南版本**: v1.0  
**最后更新**: 2026-02-09  
**文档维护**: System Administrator
