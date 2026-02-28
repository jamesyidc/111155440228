# OKX智能交易系统 - 完整部署指南

## 📦 备份内容清单

### 一、系统架构概览

```
webapp/
├── app.py                          # Flask主应用（903KB，核心路由）
├── ecosystem.config.js             # PM2进程管理配置
├── requirements.txt                # Python依赖包列表
├── .env                           # 环境变量配置
│
├── source_code/                    # 核心业务代码
│   ├── okx_tpsl_monitor.py        # 止盈止损监控服务
│   ├── market_sentiment_collector.py  # 市场情绪采集器
│   ├── coin_change_collector.py    # 币价涨跌采集器
│   └── rsi_collector.py           # RSI指标采集器
│
├── config/                        # 配置文件
│   ├── telegram_config.py         # Telegram通知配置
│   └── okx_api_config.py          # OKX API配置
│
├── templates/                     # HTML模板（88个文件）
│   ├── okx_trading.html           # OKX交易主页面
│   ├── coin_change_tracker.html   # 币价涨跌追踪页面
│   └── ...                        # 其他页面
│
├── data/                          # 数据文件（~800MB）
│   ├── coin_changes/              # 币价变化数据（每日JSONL）
│   ├── rsi_data/                  # RSI数据（每日JSONL）
│   ├── market_sentiment/          # 市场情绪数据
│   ├── okx_tpsl_settings/         # 止盈止损配置
│   ├── okx_strategies/            # 策略配置（16个JSONL文件）
│   └── ...                        # 其他数据目录（60+个）
│
└── docs/                          # 文档（440个MD文件）
    ├── DEPLOYMENT_GUIDE.md
    ├── TELEGRAM_NOTIFICATION_SETUP.md
    └── ...
```

---

## 🔧 系统依赖说明

### 1. 系统级依赖（APT包）

```bash
# 必需的系统包
apt-get update
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    git \
    curl \
    wget \
    build-essential
```

### 2. Python依赖（requirements.txt）

```txt
# Web框架
Flask==3.0.0
Flask-Cors==4.0.0

# HTTP请求
requests==2.31.0

# 加密相关
cryptography==41.0.7
pycryptodome==3.19.0

# 时间处理
python-dateutil==2.8.2
pytz==2023.3

# 数据处理
pandas==2.1.4
numpy==1.26.2

# 其他工具
python-dotenv==1.0.0
```

### 3. Node.js依赖（PM2进程管理）

```bash
# 全局安装PM2
npm install -g pm2

# PM2依赖
pm2 --version  # 确认版本 >= 5.0.0
```

---

## 🚀 完整部署步骤

### 步骤1：解压备份文件

```bash
# 解压到目标目录
cd /home/user
tar -xzf /tmp/okx_trading_system_full_backup_YYYYMMDD_HHMMSS.tar.gz

# 进入项目目录
cd webapp
```

### 步骤2：安装系统依赖

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip nodejs npm git

# CentOS/RHEL
sudo yum install -y python3 python3-pip nodejs npm git
```

### 步骤3：安装Python虚拟环境（可选但推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 步骤4：安装Python依赖

```bash
# 安装所有Python包
pip install -r requirements.txt

# 验证安装
pip list | grep Flask
pip list | grep requests
```

### 步骤5：安装PM2

```bash
# 全局安装PM2
sudo npm install -g pm2

# 验证安装
pm2 --version
```

### 步骤6：配置环境变量

```bash
# 编辑.env文件
nano .env

# 必需配置项：
OKX_API_KEY=your_api_key
OKX_SECRET_KEY=your_secret_key
OKX_PASSPHRASE=your_passphrase
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
FLASK_PORT=9002
```

### 步骤7：初始化数据目录

```bash
# 确保数据目录存在
mkdir -p data/{coin_changes,rsi_data,market_sentiment,okx_tpsl_settings,okx_strategies}

# 设置权限
chmod -R 755 data/
```

### 步骤8：启动服务

```bash
# 使用PM2启动所有服务
pm2 start ecosystem.config.js

# 查看服务状态
pm2 status

# 查看日志
pm2 logs
```

### 步骤9：验证服务

```bash
# 检查Flask应用
curl http://localhost:9002/

# 检查API端点
curl http://localhost:9002/api/okx-trading/market-tickers

# 检查币价追踪
curl http://localhost:9002/coin-change-tracker
```

### 步骤10：配置开机自启动

```bash
# 保存PM2进程列表
pm2 save

# 生成开机自启脚本
pm2 startup

# 执行生成的命令（PM2会提示）
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u user --hp /home/user
```

---

## 📋 ecosystem.config.js 配置说明

```javascript
module.exports = {
  apps: [
    {
      name: 'flask-app',                    // Flask主应用
      script: 'app.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        FLASK_PORT: 9002,
        FLASK_ENV: 'production'
      }
    },
    {
      name: 'coin-change-collector',        // 币价采集器（每5分钟）
      script: 'source_code/coin_change_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      instances: 1,
      autorestart: true,
      watch: false
    },
    {
      name: 'rsi-collector',                // RSI采集器（每5分钟）
      script: 'source_code/rsi_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      instances: 1,
      autorestart: true,
      watch: false
    },
    {
      name: 'market-sentiment-collector',   // 市场情绪采集器（每15分钟）
      script: 'source_code/market_sentiment_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      instances: 1,
      autorestart: true,
      watch: false
    },
    {
      name: 'okx-tpsl-monitor',            // 止盈止损监控（每60秒）
      script: 'source_code/okx_tpsl_monitor.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      instances: 1,
      autorestart: true,
      watch: false
    }
  ]
};
```

---

## 🗂️ 关键文件路径对照表

| 功能模块 | 代码文件 | 配置文件 | 数据文件 |
|---------|---------|---------|---------|
| **Flask主应用** | `app.py` | `.env` | - |
| **币价采集** | `source_code/coin_change_collector.py` | - | `data/coin_changes/coin_changes_YYYYMMDD.jsonl` |
| **RSI采集** | `source_code/rsi_collector.py` | - | `data/rsi_data/rsi_data_YYYYMMDD.jsonl` |
| **市场情绪** | `source_code/market_sentiment_collector.py` | - | `data/market_sentiment/market_sentiment_YYYYMMDD.jsonl` |
| **止盈止损** | `source_code/okx_tpsl_monitor.py` | `data/okx_tpsl_settings/{account}_tpsl.jsonl` | `data/okx_tpsl_settings/{account}_execution.jsonl` |
| **BTC策略** | `app.py` (路由) | `data/okx_strategies/{account}_{strategy}.jsonl` | 同左 |
| **Telegram通知** | `config/telegram_config.py` | `.env` | - |
| **OKX API** | `config/okx_api_config.py` | `.env` | - |

---

## 🔄 数据文件说明

### 1. 币价变化数据（coin_changes/）
```
文件格式：coin_changes_20260219.jsonl
更新频率：每5分钟
字段：timestamp, coin, price, change_percent, open_price
保留时长：永久（需手动清理旧数据）
```

### 2. RSI数据（rsi_data/）
```
文件格式：rsi_data_20260219.jsonl
更新频率：每5分钟
字段：timestamp, coin, rsi, rsi_change
保留时长：永久
```

### 3. 市场情绪数据（market_sentiment/）
```
文件格式：market_sentiment_20260219.jsonl
更新频率：每15分钟（整点:00, :15, :30, :45）
字段：timestamp, sentiment, sentiment_type, reason, coin_change_data, rsi_data
保留时长：永久
```

### 4. 止盈止损配置（okx_tpsl_settings/）
```
配置文件：{account_id}_tpsl.jsonl
执行记录：{account_id}_execution.jsonl
历史记录：{account_id}_history.jsonl

配置字段：
- take_profit_enabled: bool
- take_profit_threshold: float (如12.0表示+12%)
- stop_loss_enabled: bool
- stop_loss_threshold: float (如-8.0表示-8%)
- rsi_take_profit_enabled: bool
- rsi_take_profit_threshold: float (如1900)
- sentiment_take_profit_enabled: bool
- sentiment_signals: array (如["见顶信号", "顶部背离"])
- max_position_value_usdt: float (仅用于开仓，默认5.0)
```

### 5. 策略配置（okx_strategies/）
```
4个账户 × 4个策略 = 16个文件

账户：account_main, account_fangfang12, account_poit, account_marks
策略：btc_top8, btc_bottom8, upratio0_top8, upratio0_bottom8

文件示例：account_main_btc_top8.jsonl
字段：
- enabled: bool
- trigger_price: float
- last_trigger_time: timestamp
- last_trigger_coins: array
```

---

## 🌐 Flask路由说明

### 主要路由列表

| 路由 | 方法 | 功能 | 文件位置 |
|------|------|------|---------|
| `/` | GET | 首页（重定向到OKX交易页面） | app.py:100 |
| `/okx-trading` | GET | OKX交易主页面 | app.py:150 |
| `/coin-change-tracker` | GET | 币价涨跌追踪页面 | app.py:200 |
| `/api/okx-trading/market-tickers` | GET | 获取实时行情 | app.py:500 |
| `/api/okx-trading/place-order` | POST | 下单接口 | app.py:15621 |
| `/api/okx-trading/tpsl-settings/<account_id>` | GET/POST | 止盈止损配置 | app.py:16188/16262 |
| `/api/coin-change/history` | GET | 币价历史数据 | app.py:2000 |
| `/api/market-sentiment/latest` | GET | 最新市场情绪 | app.py:3000 |

### API响应格式

```json
// 成功响应
{
  "success": true,
  "data": {...},
  "message": "操作成功"
}

// 错误响应
{
  "success": false,
  "error": "错误信息",
  "code": 400
}
```

---

## 🔐 安全配置

### 1. 环境变量保护

```bash
# .env文件权限
chmod 600 .env

# 确保不提交到Git
echo ".env" >> .gitignore
```

### 2. API密钥管理

```python
# config/okx_api_config.py
import os
from dotenv import load_dotenv

load_dotenv()

OKX_API_KEY = os.getenv('OKX_API_KEY')
OKX_SECRET_KEY = os.getenv('OKX_SECRET_KEY')
OKX_PASSPHRASE = os.getenv('OKX_PASSPHRASE')
```

### 3. Telegram配置

```python
# config/telegram_config.py
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
```

---

## 🐛 常见问题排查

### 问题1：Flask应用启动失败

```bash
# 检查端口占用
lsof -i :9002

# 检查Python依赖
pip list | grep Flask

# 查看详细错误
pm2 logs flask-app --lines 100
```

### 问题2：采集器无数据

```bash
# 检查采集器状态
pm2 status

# 检查采集器日志
pm2 logs coin-change-collector --lines 50

# 手动运行测试
cd /home/user/webapp
python3 source_code/coin_change_collector.py
```

### 问题3：止盈止损不触发

```bash
# 检查配置文件
cat data/okx_tpsl_settings/account_main_tpsl.jsonl

# 检查监控日志
pm2 logs okx-tpsl-monitor --lines 100

# 验证持仓
curl http://localhost:9002/api/okx-trading/positions?account_id=account_main
```

### 问题4：Telegram通知失败

```bash
# 测试Telegram连接
python3 test_telegram.py

# 检查Bot Token和Chat ID
cat .env | grep TELEGRAM

# 手动发送测试消息
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>&text=测试消息"
```

---

## 📊 性能优化建议

### 1. 数据清理策略

```bash
# 创建数据清理脚本
cat > scripts/clean_old_data.sh << 'SCRIPT'
#!/bin/bash
# 删除30天前的币价数据
find data/coin_changes/ -name "*.jsonl" -mtime +30 -delete

# 删除30天前的RSI数据
find data/rsi_data/ -name "*.jsonl" -mtime +30 -delete

# 保留市场情绪数据（永久）
# 保留止盈止损配置和执行记录（永久）
SCRIPT

chmod +x scripts/clean_old_data.sh

# 添加到crontab（每天凌晨3点执行）
crontab -e
# 添加：0 3 * * * /home/user/webapp/scripts/clean_old_data.sh
```

### 2. PM2内存限制

```javascript
// ecosystem.config.js
max_memory_restart: '1G',  // 内存超过1GB自动重启
```

### 3. 日志轮转

```bash
# PM2日志管理
pm2 install pm2-logrotate

# 配置日志轮转
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
```

---

## 🔄 备份与恢复

### 自动备份脚本

```bash
cat > scripts/auto_backup.sh << 'SCRIPT'
#!/bin/bash
BACKUP_DIR="/tmp/okx_backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="okx_trading_backup_${DATE}.tar.gz"

mkdir -p $BACKUP_DIR

cd /home/user
tar -czf ${BACKUP_DIR}/${BACKUP_NAME} \
  --exclude='webapp/venv' \
  --exclude='webapp/.git' \
  --exclude='webapp/__pycache__' \
  --exclude='webapp/*.log' \
  webapp/

echo "备份完成：${BACKUP_DIR}/${BACKUP_NAME}"
ls -lh ${BACKUP_DIR}/${BACKUP_NAME}
SCRIPT

chmod +x scripts/auto_backup.sh

# 添加到crontab（每天凌晨2点备份）
# 0 2 * * * /home/user/webapp/scripts/auto_backup.sh
```

### 快速恢复

```bash
# 停止所有服务
pm2 stop all

# 解压备份
cd /home/user
tar -xzf /tmp/okx_backups/okx_trading_backup_YYYYMMDD_HHMMSS.tar.gz

# 重启服务
cd webapp
pm2 restart all
```

---

## 📞 技术支持

### 系统版本信息
- **币价追踪系统**: V2.5 (2026-02-19)
- **OKX交易系统**: v2.6.4 (2026-02-19)

### 关键功能版本
- Flask: 3.0.0
- Python: 3.8+
- Node.js: 14+
- PM2: 5.0+

### 文档位置
- 部署指南：`docs/DEPLOYMENT_GUIDE.md`
- Telegram通知：`docs/TELEGRAM_NOTIFICATION_SETUP.md`
- 止盈止损：`docs/TPSL_MONITORING_SETUP_GUIDE.md`

---

## ✅ 部署检查清单

- [ ] 系统依赖安装（Python, Node.js, npm, PM2）
- [ ] Python依赖安装（requirements.txt）
- [ ] 环境变量配置（.env）
- [ ] 数据目录初始化
- [ ] PM2服务启动（5个进程全部running）
- [ ] Flask应用访问正常（http://localhost:9002）
- [ ] 币价追踪页面正常
- [ ] OKX交易页面正常
- [ ] API端点响应正常
- [ ] Telegram通知测试成功
- [ ] 止盈止损监控正常
- [ ] 开机自启配置完成
- [ ] 备份脚本配置完成

---

**部署完成后，访问地址**：
- 主页：http://your-server-ip:9002/
- OKX交易：http://your-server-ip:9002/okx-trading
- 币价追踪：http://your-server-ip:9002/coin-change-tracker

**部署成功标志**：
```bash
pm2 status
# 所有进程状态为 "online"
# 访问页面正常显示数据
# Telegram收到测试通知
```

---

**备份文件位置**：`/tmp/okx_trading_system_full_backup_YYYYMMDD_HHMMSS.tar.gz`

**备份大小**：约2GB（包含全部历史数据）

**部署时间**：约15-30分钟（取决于网络速度）
