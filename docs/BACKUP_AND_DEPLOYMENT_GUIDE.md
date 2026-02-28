# 加密货币数据分析系统 - 完整备份与部署指南

## 📋 目录
1. [系统概览](#系统概览)
2. [备份清单](#备份清单)
3. [快速备份脚本](#快速备份脚本)
4. [完整部署流程](#完整部署流程)
5. [依赖安装](#依赖安装)
6. [配置说明](#配置说明)
7. [服务启动](#服务启动)
8. [验证测试](#验证测试)
9. [故障排除](#故障排除)

---

## 系统概览

### 📊 项目统计
- **Python 文件**: 1002 个（采集器、管理器、工具类）
- **Markdown 文档**: 1162 个（系统文档、修复报告）
- **HTML 模板**: 379 个（Web 界面）
- **配置文件**: 50+ 个（JSON、JS、环境配置）
- **数据文件**: 数千个（JSONL 格式）
- **项目总大小**: ~5.0 GB

### 🏗️ 系统架构
```
加密货币数据分析系统
├── Flask Web 应用 (主服务)
├── PM2 进程管理 (25+ 采集器)
├── 数据存储层 (JSONL)
├── 实时数据采集
└── Web 可视化界面
```

---

## 备份清单

### 1. 核心应用文件
```
app.py                          # Flask 主应用 (20000+ 行)
config.py                       # 系统配置
requirements.txt                # Python 依赖
package.json                    # Node.js 依赖 (PM2)
ecosystem.config.js             # PM2 进程配置
.env                           # 环境变量 (需手动配置)
```

### 2. 源代码目录
```
source_code/                    # 核心业务逻辑
├── *_collector.py             # 数据采集器 (25+)
├── *_jsonl_manager.py         # 数据管理器 (15+)
├── *_daily_reader.py          # 数据读取器
├── escape_signal_*.py         # 逃顶信号系统
└── utils/                     # 工具类
```

### 3. Web 模板
```
templates/                      # HTML 模板
├── index.html                 # 首页
├── panic_new.html             # 恐慌清洗指数
├── coin_change_tracker.html   # 币种涨跌追踪
├── monitor_charts.html        # 监控图表
├── check_memory_leak.html     # 内存监控
└── ...                        # 其他页面 (30+)
```

### 4. 静态资源
```
static/                         # 静态文件
├── css/                       # 样式文件
├── js/                        # JavaScript
└── images/                    # 图片资源
```

### 5. 数据文件
```
data/                          # 数据存储 (~3GB)
├── gdrive_jsonl/             # Google Drive 数据
├── sar_jsonl/                # SAR 指标数据
├── sar_slope_jsonl/          # SAR 斜率数据
├── sar_bias_stats/           # SAR 偏向统计 (~6MB)
│   ├── bias_stats_20260201.jsonl
│   ├── bias_stats_20260202.jsonl
│   └── ...
├── panic_jsonl/              # 恐慌指数数据
├── extreme_jsonl/            # 极值数据
├── escape_signal_jsonl/      # 逃顶信号数据 (~12MB)
├── coin_change_tracker/      # 币种变化追踪
└── ...
```

### 6. 配置和日志
```
logs/                          # 应用日志
├── app.log
├── collector_*.log
└── error_*.log

.pm2/                          # PM2 配置和日志
├── logs/                     # 进程日志
└── pids/                     # 进程 PID

ecosystem.config.js            # PM2 进程配置
supervisord.conf               # Supervisor 配置 (如果使用)
```

### 7. 文档和说明
```
README*.md                     # 项目说明
CLAUDE.md                      # Claude 指令
DEPLOYMENT_*.md                # 部署文档
*_FIX_REPORT.md               # 修复报告
*_OPTIMIZATION.md             # 优化文档
SYSTEM_HEALTH_*.md            # 系统健康报告
```

---

## 快速备份脚本

### 创建备份脚本
```bash
#!/bin/bash
# 文件: /home/user/webapp/create_backup.sh

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="crypto_analysis_system_backup_${BACKUP_DATE}.tar.gz"
BACKUP_DIR="/tmp"
WEBAPP_DIR="/home/user/webapp"

echo "🚀 开始创建完整系统备份..."
echo "备份时间: $(date)"
echo "备份路径: ${BACKUP_DIR}/${BACKUP_NAME}"

# 创建临时目录用于组织备份内容
TEMP_BACKUP_DIR="/tmp/backup_temp_${BACKUP_DATE}"
mkdir -p "$TEMP_BACKUP_DIR"

# 1. 备份核心代码
echo "📦 备份核心代码..."
cp -r "$WEBAPP_DIR/app.py" "$TEMP_BACKUP_DIR/"
cp -r "$WEBAPP_DIR/config.py" "$TEMP_BACKUP_DIR/" 2>/dev/null || echo "config.py not found"
cp -r "$WEBAPP_DIR/requirements.txt" "$TEMP_BACKUP_DIR/"
cp -r "$WEBAPP_DIR/package.json" "$TEMP_BACKUP_DIR/" 2>/dev/null || echo "package.json not found"
cp -r "$WEBAPP_DIR/ecosystem.config.js" "$TEMP_BACKUP_DIR/" 2>/dev/null || echo "ecosystem.config.js not found"

# 2. 备份源代码目录
echo "📦 备份 source_code..."
cp -r "$WEBAPP_DIR/source_code" "$TEMP_BACKUP_DIR/"

# 3. 备份模板
echo "📦 备份 templates..."
cp -r "$WEBAPP_DIR/templates" "$TEMP_BACKUP_DIR/"

# 4. 备份静态文件
echo "📦 备份 static..."
cp -r "$WEBAPP_DIR/static" "$TEMP_BACKUP_DIR/" 2>/dev/null || echo "static directory not found"

# 5. 备份数据文件（仅最近7天）
echo "📦 备份数据文件（最近7天）..."
mkdir -p "$TEMP_BACKUP_DIR/data"
find "$WEBAPP_DIR/data" -type f -mtime -7 -name "*.jsonl" -exec cp --parents {} "$TEMP_BACKUP_DIR/" \; 2>/dev/null

# 6. 备份配置
echo "📦 备份配置文件..."
mkdir -p "$TEMP_BACKUP_DIR/config_backup"
cp "$WEBAPP_DIR"/*.json "$TEMP_BACKUP_DIR/config_backup/" 2>/dev/null || true
cp "$WEBAPP_DIR"/*.conf "$TEMP_BACKUP_DIR/config_backup/" 2>/dev/null || true
cp "$WEBAPP_DIR/.env" "$TEMP_BACKUP_DIR/config_backup/" 2>/dev/null || echo ".env not found (需手动配置)"

# 7. 备份文档
echo "📦 备份文档..."
mkdir -p "$TEMP_BACKUP_DIR/docs"
cp "$WEBAPP_DIR"/*.md "$TEMP_BACKUP_DIR/docs/" 2>/dev/null || true

# 8. 备份 PM2 配置
echo "📦 备份 PM2 配置..."
mkdir -p "$TEMP_BACKUP_DIR/pm2_config"
pm2 save
cp ~/.pm2/dump.pm2 "$TEMP_BACKUP_DIR/pm2_config/" 2>/dev/null || echo "PM2 dump not found"
pm2 list > "$TEMP_BACKUP_DIR/pm2_config/pm2_list.txt"

# 9. 创建系统信息快照
echo "📦 创建系统信息快照..."
cat > "$TEMP_BACKUP_DIR/SYSTEM_INFO.txt" << EOF
系统备份信息
============
备份时间: $(date)
备份版本: ${BACKUP_DATE}
主机名: $(hostname)
系统: $(uname -a)
Python 版本: $(python3 --version)
Node 版本: $(node --version 2>/dev/null || echo "Not installed")
PM2 版本: $(pm2 --version 2>/dev/null || echo "Not installed")

Python 包列表:
$(pip3 list)

PM2 进程列表:
$(pm2 list)

磁盘使用:
$(df -h)

内存使用:
$(free -h)
EOF

# 10. 创建部署脚本
echo "📦 创建自动部署脚本..."
cat > "$TEMP_BACKUP_DIR/deploy.sh" << 'EOF'
#!/bin/bash
# 自动部署脚本
set -e

DEPLOY_DIR="/home/user/webapp"
BACKUP_DIR=$(pwd)

echo "🚀 开始部署加密货币数据分析系统..."

# 1. 检查目标目录
if [ ! -d "$DEPLOY_DIR" ]; then
    echo "创建部署目录: $DEPLOY_DIR"
    mkdir -p "$DEPLOY_DIR"
fi

# 2. 复制文件
echo "📦 复制核心文件..."
cp -r app.py source_code templates "$DEPLOY_DIR/"
cp -r requirements.txt "$DEPLOY_DIR/"
[ -f config.py ] && cp config.py "$DEPLOY_DIR/"
[ -f ecosystem.config.js ] && cp ecosystem.config.js "$DEPLOY_DIR/"
[ -d static ] && cp -r static "$DEPLOY_DIR/"

# 3. 复制数据文件
echo "📦 恢复数据文件..."
if [ -d "data" ]; then
    cp -r data/* "$DEPLOY_DIR/data/"
fi

# 4. 安装 Python 依赖
echo "📦 安装 Python 依赖..."
cd "$DEPLOY_DIR"
pip3 install -r requirements.txt

# 5. 安装 PM2
echo "📦 安装 PM2..."
if ! command -v pm2 &> /dev/null; then
    npm install -g pm2
fi

# 6. 创建必要的目录
echo "📦 创建必要目录..."
mkdir -p logs data

# 7. 设置环境变量提示
echo "⚠️  请手动配置以下文件:"
echo "   - $DEPLOY_DIR/.env (环境变量)"
echo "   - OKX API 配置"
echo "   - Telegram Bot Token"

echo "✅ 部署完成！"
echo "下一步: 请参考 BACKUP_AND_DEPLOYMENT_GUIDE.md 完成配置和启动"
EOF
chmod +x "$TEMP_BACKUP_DIR/deploy.sh"

# 11. 复制部署指南
cp "$WEBAPP_DIR/BACKUP_AND_DEPLOYMENT_GUIDE.md" "$TEMP_BACKUP_DIR/" 2>/dev/null || echo "创建中..."

# 12. 压缩备份
echo "🗜️  压缩备份文件..."
cd /tmp
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}" "backup_temp_${BACKUP_DATE}"

# 清理临时目录
rm -rf "$TEMP_BACKUP_DIR"

# 输出备份信息
BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}" | cut -f1)
echo ""
echo "✅ 备份创建完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 备份文件: ${BACKUP_NAME}"
echo "📍 备份路径: ${BACKUP_DIR}/${BACKUP_NAME}"
echo "📦 备份大小: ${BACKUP_SIZE}"
echo "⏰ 备份时间: $(date)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "解压命令:"
echo "  tar -xzf ${BACKUP_NAME}"
echo ""
echo "部署命令:"
echo "  cd backup_temp_${BACKUP_DATE}"
echo "  ./deploy.sh"
echo ""
```

---

## 完整部署流程

### 第一步: 系统准备

#### 1.1 安装基础软件
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.10+
sudo apt install python3 python3-pip python3-venv -y

# 安装 Node.js 和 npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# 安装 Git
sudo apt install git -y

# 安装其他依赖
sudo apt install build-essential curl wget -y
```

#### 1.2 安装 PM2
```bash
# 全局安装 PM2
sudo npm install -g pm2

# 设置 PM2 开机自启动
pm2 startup
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u $(whoami) --hp $(eval echo ~$(whoami))
```

### 第二步: 解压和部署

#### 2.1 解压备份
```bash
# 解压备份文件
cd /tmp
tar -xzf crypto_analysis_system_backup_YYYYMMDD_HHMMSS.tar.gz

# 进入备份目录
cd backup_temp_YYYYMMDD_HHMMSS
```

#### 2.2 运行自动部署脚本
```bash
# 执行自动部署
./deploy.sh
```

#### 2.3 手动部署（如果自动脚本失败）
```bash
# 创建项目目录
mkdir -p /home/user/webapp
cd /home/user/webapp

# 复制核心文件
cp -r /tmp/backup_temp_*/app.py .
cp -r /tmp/backup_temp_*/source_code .
cp -r /tmp/backup_temp_*/templates .
cp -r /tmp/backup_temp_*/requirements.txt .
cp -r /tmp/backup_temp_*/data .

# 复制配置文件（如果存在）
cp /tmp/backup_temp_*/config.py . 2>/dev/null || echo "config.py not in backup"
cp /tmp/backup_temp_*/ecosystem.config.js . 2>/dev/null || echo "ecosystem.config.js not in backup"
```

### 第三步: 安装依赖

#### 3.1 Python 依赖
```bash
cd /home/user/webapp

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 或者全局安装
pip3 install -r requirements.txt
```

#### 3.2 关键 Python 包
```bash
pip3 install flask flask-compress requests python-telegram-bot pytz pandas numpy ccxt
```

### 第四步: 配置系统

#### 4.1 创建环境变量文件
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

#### 4.2 创建 PM2 配置文件
```bash
cat > /home/user/webapp/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    // Flask 主应用
    {
      name: 'flask-app',
      script: 'app.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        FLASK_ENV: 'production',
        PYTHONUNBUFFERED: '1'
      },
      error_file: '/home/user/.pm2/logs/flask-app-error.log',
      out_file: '/home/user/.pm2/logs/flask-app-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // SAR 数据采集器
    {
      name: 'sar-collector',
      script: 'source_code/sar_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_memory_restart: '200M'
    },

    // SAR 偏向统计采集器
    {
      name: 'sar-bias-stats-collector',
      script: 'source_code/sar_bias_stats_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_memory_restart: '200M'
    },

    // 恐慌清洗指数采集器
    {
      name: 'panic-wash-collector',
      script: 'source_code/panic_wash_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_memory_restart: '200M'
    },

    // 币种变化追踪器
    {
      name: 'coin-change-tracker',
      script: 'source_code/coin_change_tracker.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_memory_restart: '200M'
    },

    // 信号采集器
    {
      name: 'signal-collector',
      script: 'source_code/signal_collector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_memory_restart: '200M'
    },

    // Google Drive 检测器
    {
      name: 'gdrive-detector',
      script: 'source_code/gdrive_detector.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      autorestart: true,
      max_memory_restart: '200M'
    },

    // 其他采集器...（根据需要添加）
  ]
};
EOF
```

### 第五步: 数据目录初始化

```bash
cd /home/user/webapp

# 创建所有必要的数据目录
mkdir -p data/{gdrive_jsonl,sar_jsonl,sar_slope_jsonl,sar_bias_stats,panic_jsonl,extreme_jsonl,escape_signal_jsonl,coin_change_tracker,support_resistance_daily,anchor_daily,price_speed_jsonl}

# 创建日志目录
mkdir -p logs

# 设置权限
chmod -R 755 data logs
```

### 第六步: 启动服务

#### 6.1 启动所有服务
```bash
cd /home/user/webapp

# 使用 PM2 启动所有服务
pm2 start ecosystem.config.js

# 或者逐个启动
pm2 start app.py --name flask-app --interpreter python3
pm2 start source_code/sar_collector.py --name sar-collector --interpreter python3
pm2 start source_code/sar_bias_stats_collector.py --name sar-bias-stats-collector --interpreter python3
# ... 其他服务
```

#### 6.2 保存 PM2 配置
```bash
# 保存当前 PM2 进程列表
pm2 save

# 设置开机自启
pm2 startup
```

#### 6.3 查看服务状态
```bash
# 查看所有服务
pm2 list

# 查看特定服务日志
pm2 logs flask-app

# 查看内存使用
pm2 monit
```

### 第七步: 验证部署

#### 7.1 检查 Flask 服务
```bash
# 测试 Flask 是否运行
curl http://localhost:5000/

# 测试 API 端点
curl http://localhost:5000/api/latest
curl http://localhost:5000/api/sar-bias-trend
curl http://localhost:5000/api/coin-change-tracker/latest
```

#### 7.2 检查数据采集
```bash
# 查看最新的 SAR 偏向数据
cd /home/user/webapp
ls -lh data/sar_bias_stats/
tail -1 data/sar_bias_stats/bias_stats_$(date +%Y%m%d).jsonl

# 查看采集器日志
pm2 logs sar-bias-stats-collector --lines 50
```

#### 7.3 访问 Web 界面
```bash
# 如果在本地
http://localhost:5000/

# 关键页面:
# 首页: /
# 恐慌指数: /panic
# SAR 偏向: /sar-bias-trend
# 币种追踪: /coin-change-tracker
# 内存监控: /check-memory-leak
```

---

## 依赖安装

### Python 核心依赖
```txt
# requirements.txt
Flask==3.0.0
flask-compress==1.14
requests==2.31.0
python-telegram-bot==20.7
pytz==2023.3
pandas==2.1.4
numpy==1.26.2
ccxt==4.1.91
python-dateutil==2.8.2
schedule==1.2.0
```

### 系统依赖
```bash
sudo apt install -y \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-setuptools \
    python3-pip
```

---

## 配置说明

### 1. OKX API 配置
```python
# app.py 或 config.py 中
OKX_CONFIG = {
    'apiKey': os.getenv('OKX_API_KEY'),
    'secret': os.getenv('OKX_SECRET_KEY'),
    'password': os.getenv('OKX_PASSPHRASE'),
    'enableRateLimit': True
}
```

### 2. Telegram Bot 配置
```python
TELEGRAM_CONFIG = {
    'token': os.getenv('TELEGRAM_BOT_TOKEN'),
    'chat_id': os.getenv('TELEGRAM_CHAT_ID')
}
```

### 3. 数据路径配置
```python
BASE_DIR = '/home/user/webapp'
DATA_DIR = os.path.join(BASE_DIR, 'data')

# 各数据源路径
SAR_JSONL_DIR = os.path.join(DATA_DIR, 'sar_jsonl')
SAR_BIAS_STATS_DIR = os.path.join(DATA_DIR, 'sar_bias_stats')
PANIC_JSONL_DIR = os.path.join(DATA_DIR, 'panic_jsonl')
# ... 其他路径
```

### 4. 采集器配置
```python
# SAR 偏向统计采集器
COLLECTION_INTERVAL = 300  # 5 分钟
SYMBOLS = ['BTC-USDT-SWAP', 'ETH-USDT-SWAP', ...]  # 27个币种

# 恐慌指数采集器
PANIC_COLLECTION_INTERVAL = 60  # 1 分钟

# 币种变化追踪
CHANGE_TRACKER_INTERVAL = 60  # 1 分钟
```

---

## 服务启动

### PM2 常用命令
```bash
# 启动所有服务
pm2 start ecosystem.config.js

# 启动单个服务
pm2 start app.py --name flask-app --interpreter python3

# 重启服务
pm2 restart flask-app
pm2 restart all

# 停止服务
pm2 stop flask-app
pm2 stop all

# 删除服务
pm2 delete flask-app

# 查看日志
pm2 logs                    # 所有日志
pm2 logs flask-app          # 特定服务
pm2 logs --lines 100        # 最近100行

# 清空日志
pm2 flush

# 监控
pm2 monit                   # 实时监控
pm2 list                    # 进程列表
pm2 info flask-app          # 详细信息

# 保存配置
pm2 save                    # 保存进程列表
pm2 startup                 # 设置开机启动
```

### 手动启动（调试用）
```bash
# 启动 Flask
cd /home/user/webapp
python3 app.py

# 启动采集器（在新终端）
python3 source_code/sar_collector.py
python3 source_code/sar_bias_stats_collector.py
python3 source_code/panic_wash_collector.py
```

---

## 验证测试

### 1. 系统健康检查
```bash
# 检查服务状态
pm2 list

# 检查内存使用
free -h

# 检查磁盘空间
df -h

# 检查端口
netstat -tulpn | grep 5000
```

### 2. API 测试
```bash
# 测试主要 API
curl http://localhost:5000/api/latest
curl http://localhost:5000/api/sar-bias-trend
curl http://localhost:5000/api/panic/latest
curl http://localhost:5000/api/coin-change-tracker/latest
curl http://localhost:5000/api/system/memory
curl http://localhost:5000/api/system/processes
```

### 3. 数据验证
```bash
# 检查数据文件
cd /home/user/webapp/data

# SAR 偏向统计
ls -lh sar_bias_stats/
tail -5 sar_bias_stats/bias_stats_$(date +%Y%m%d).jsonl | jq .

# 恐慌指数
ls -lh panic_jsonl/
tail -5 panic_jsonl/panic_$(date +%Y%m%d).jsonl | jq .

# 币种变化
ls -lh coin_change_tracker/
tail -5 coin_change_tracker/changes_$(date +%Y%m%d).jsonl | jq .
```

### 4. Web 界面测试
访问以下页面确认正常显示：
- http://localhost:5000/ (首页)
- http://localhost:5000/panic (恐慌指数)
- http://localhost:5000/sar-bias-trend (SAR 偏向)
- http://localhost:5000/coin-change-tracker (币种追踪)
- http://localhost:5000/check-memory-leak (内存监控)

---

## 故障排除

### 问题 1: Flask 无法启动
```bash
# 检查端口占用
sudo lsof -i :5000
sudo kill -9 <PID>

# 检查 Python 依赖
pip3 list | grep -i flask

# 查看错误日志
pm2 logs flask-app --err --lines 100
```

### 问题 2: 采集器频繁重启
```bash
# 查看重启原因
pm2 info sar-collector

# 检查内存限制
pm2 list  # 查看 memory 列

# 增加内存限制
pm2 delete sar-collector
pm2 start source_code/sar_collector.py --name sar-collector --interpreter python3 --max-memory-restart 500M
```

### 问题 3: 数据不更新
```bash
# 检查采集器状态
pm2 list | grep collector

# 查看采集器日志
pm2 logs sar-bias-stats-collector --lines 50

# 手动运行测试
cd /home/user/webapp
python3 source_code/sar_bias_stats_collector.py
```

### 问题 4: API 返回 500 错误
```bash
# 查看 Flask 错误日志
pm2 logs flask-app --err --lines 100

# 检查缺少的模块
python3 -c "from source_code.escape_signal_jsonl_manager import EscapeSignalJSONLManager"

# 测试 API
curl -v http://localhost:5000/api/escape-signal-stats?limit=1
```

### 问题 5: 内存泄漏
```bash
# 访问内存监控页面
http://localhost:5000/check-memory-leak

# 查看系统内存
free -h

# 查看进程内存
ps aux --sort=-%mem | head -20

# 重启高内存服务
pm2 restart flask-app
```

### 问题 6: PM2 进程异常
```bash
# 完全清理 PM2
pm2 kill

# 删除 PM2 配置
rm -rf ~/.pm2

# 重新初始化
pm2 start ecosystem.config.js
pm2 save
```

---

## 📝 重要注意事项

### ⚠️ 配置文件
- `.env` 文件包含敏感信息，**不在备份中**，需手动创建
- OKX API 密钥需重新配置
- Telegram Bot Token 需重新配置

### 📊 数据说明
- 备份仅包含最近 7 天的数据文件
- 完整历史数据需单独备份
- 数据文件大小约 3GB，备份后约 800MB

### 🔧 PM2 配置
- `max_memory_restart`: 设置内存限制，防止内存泄漏
- `autorestart`: 自动重启崩溃的进程
- `watch`: 生产环境建议设置为 `false`

### 🚀 性能优化
- Flask 建议使用 Gunicorn + Nginx
- 数据采集间隔可根据需求调整
- PM2 cluster 模式可提高并发性能

### 🔒 安全建议
- 使用防火墙限制端口访问
- 定期更新依赖包
- 使用 HTTPS 加密通信
- 定期备份数据

---

## 📞 支持与联系

如有问题，请查看：
1. 系统日志: `pm2 logs`
2. 错误日志: `/home/user/.pm2/logs/*-error.log`
3. 健康监控: http://localhost:5000/check-memory-leak

---

**文档版本**: v1.0  
**最后更新**: 2026-02-07  
**适用系统**: 加密货币数据分析系统 v2.9+  
