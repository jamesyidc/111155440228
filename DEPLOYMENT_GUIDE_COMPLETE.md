# 完整项目部署指南

## 📋 目录
1. [系统要求](#系统要求)
2. [备份内容清单](#备份内容清单)
3. [部署步骤](#部署步骤)
4. [服务配置](#服务配置)
5. [数据恢复](#数据恢复)
6. [故障排查](#故障排查)

---

## 系统要求

### 操作系统
- **推荐**: Ubuntu 20.04 LTS 或更高版本
- **最低**: 任何支持Python 3.8+的Linux发行版

### 软件依赖

#### 必需软件
```bash
# Python 3.8+
python3 --version  # 应显示 >= 3.8

# pip（Python包管理器）
pip3 --version

# Node.js 14+ 和 npm（用于PM2）
node --version  # 应显示 >= 14.0
npm --version

# PM2（进程管理器）
npm install -g pm2
pm2 --version
```

#### 可选软件
```bash
# Git（版本控制）
git --version

# 树形目录显示
sudo apt install tree
```

### 硬件要求
- **CPU**: 2核或更多
- **内存**: 至少4GB RAM（推荐8GB+）
- **磁盘**: 至少10GB可用空间（数据目录会持续增长）

---

## 备份内容清单

### 📁 目录结构

```
webapp_complete_backup_YYYYMMDD_HHMMSS/
├── app.py                          # 主Flask应用（1MB+）
├── ecosystem.config.js             # PM2生态配置
├── requirements.txt                # Python依赖列表
├── .env                            # 环境变量配置
├── .gitignore                      # Git忽略规则
│
├── source_code/                    # 所有Python API文件
│   ├── coin_change_tracker_collector.py
│   ├── bottom_signal_long_monitor.py
│   ├── data_manager.py
│   └── ... (30+ Python文件)
│
├── panic_paged_v2/                 # 恐慌指标v2系统
│   ├── api_routes.py
│   ├── collector_1h.py
│   ├── collector_24h.py
│   └── data_manager.py
│
├── panic_v3/                       # 恐慌指标v3系统
│   ├── app.py
│   ├── collector.py
│   └── migrate.py
│
├── templates/                      # HTML模板（88个文件）
│   ├── index.html
│   ├── coin_change_tracker.html
│   ├── liquidation_monthly.html
│   └── ...
│
├── static/                         # 静态文件（CSS、JS、图片）
│   ├── css/
│   ├── js/
│   └── images/
│
├── config/                         # 配置文件目录
│   ├── configs/
│   │   ├── telegram_config.json
│   │   └── okx_accounts.json
│   └── ...
│
├── pm2/                            # PM2配置文件
│   └── ecosystem.config.json
│
├── monitors/                       # 监控脚本
│   ├── coin_change_prediction_monitor.py
│   └── ...
│
├── scripts/                        # 工具脚本
│   ├── backup_script.sh
│   └── ...
│
├── data/                           # 所有数据文件（~800MB）
│   ├── coin_change_tracker/
│   │   ├── coin_change_20260224.jsonl
│   │   ├── coin_change_20260225.jsonl
│   │   └── ... (按日期分文件)
│   ├── daily_predictions/
│   ├── liquidation_1h/
│   ├── market_sentiment/
│   └── ... (60+ 子目录)
│
├── docs/                           # 文档（440+ Markdown文件）
│   ├── DEPLOYMENT_GUIDE.md
│   ├── API_DOCUMENTATION.md
│   └── ...
│
├── tests/                          # 测试文件
│   └── ...
│
├── price_position_v2/              # 价格位置系统v2
│   └── ...
│
├── code/                           # 其他代码模块
│   └── ...
│
└── DEPLOYMENT_INFO.txt             # 备份信息（自动生成）
```

### 📊 文件统计

| 类型 | 数量 | 大小 | 说明 |
|------|------|------|------|
| Python文件 | 88 | ~5MB | 主应用、采集器、管理器、工具 |
| HTML模板 | 88 | ~2MB | Web界面模板 |
| Markdown文档 | 440+ | ~15MB | 系统文档、修复报告、使用指南 |
| JSON配置 | 15+ | <1MB | 各类配置文件 |
| JSONL数据 | 数千 | ~800MB | 所有历史数据 |
| **总计** | **616+** | **~2GB** | 完整项目 |

### ❌ 不包含的内容

这些目录/文件**不在备份中**（运行时生成或可重新安装）：

- `logs/` - 所有日志文件（65MB）
- `node_modules/` - Node.js依赖（34MB）
- `backups/` - 旧备份目录
- `__pycache__/` - Python缓存文件
- `.git/` - Git版本控制目录

---

## 部署步骤

### 第1步：解压备份

```bash
# 进入备份目录
cd /tmp

# 解压备份文件
tar -xzf webapp_complete_backup_YYYYMMDD_HHMMSS.tar.gz

# 进入解压目录
cd webapp_complete_backup_YYYYMMDD_HHMMSS

# 查看目录结构
ls -la
tree -L 2 -d  # 查看目录树（如果已安装tree）
```

### 第2步：移动到目标位置

```bash
# 创建目标目录
sudo mkdir -p /home/user/webapp

# 移动所有文件
sudo mv * /home/user/webapp/
sudo mv .* /home/user/webapp/ 2>/dev/null || true

# 设置权限
sudo chown -R user:user /home/user/webapp
cd /home/user/webapp
```

### 第3步：安装Python依赖

```bash
cd /home/user/webapp

# 升级pip
pip3 install --upgrade pip

# 安装所有Python依赖
pip3 install -r requirements.txt

# 验证安装
pip3 list
```

**主要依赖包**:
- `Flask` - Web框架
- `flask-cors` - 跨域支持
- `requests` - HTTP请求
- `pytz` - 时区处理
- `python-telegram-bot` - Telegram通知
- `ccxt` - 加密货币交易所API

### 第4步：配置环境变量

```bash
# 编辑.env文件
nano .env

# 或复制示例配置
cp .env.example .env  # 如果有
```

**必需环境变量**:
```bash
# Flask配置
FLASK_APP=app.py
FLASK_ENV=production
FLASK_PORT=9002

# Telegram配置（如需通知功能）
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# OKX API（如需交易功能）
OKX_API_KEY=your_api_key
OKX_SECRET_KEY=your_secret_key
OKX_PASSPHRASE=your_passphrase
```

### 第5步：安装PM2并启动服务

```bash
# 安装PM2（如果尚未安装）
npm install -g pm2

# 使用ecosystem.config.js启动所有服务
pm2 start ecosystem.config.js

# 查看服务状态
pm2 list

# 查看日志
pm2 logs --lines 50

# 设置PM2开机自启
pm2 startup
pm2 save
```

### 第6步：验证服务

```bash
# 检查Flask应用
curl http://localhost:9002/

# 检查API端点
curl http://localhost:9002/api/coin-change-tracker/latest

# 检查PM2进程
pm2 list
```

---

## 服务配置

### PM2 Ecosystem配置

`ecosystem.config.js` 包含所有服务的配置：

```javascript
module.exports = {
  apps: [
    {
      name: "flask-app",
      script: "python3",
      args: "app.py",
      cwd: "/home/user/webapp",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env: {
        PORT: 9002,
        FLASK_ENV: "production"
      }
    },
    {
      name: "coin-change-tracker",
      script: "python3",
      args: "source_code/coin_change_tracker_collector.py",
      cwd: "/home/user/webapp",
      instances: 1,
      autorestart: true
    },
    {
      name: "coin-change-predictor",
      script: "python3",
      args: "monitors/coin_change_prediction_monitor.py",
      cwd: "/home/user/webapp",
      instances: 1,
      autorestart: true
    }
    // ... 更多服务
  ]
};
```

### Flask路由映射

**主要路由**:

| 路由 | 说明 | 文件 |
|------|------|------|
| `/` | 主页 | `templates/index.html` |
| `/coin-change-tracker` | 27币涨跌幅追踪 | `templates/coin_change_tracker.html` |
| `/liquidation-monthly` | 爆仓月线图 | `templates/liquidation_monthly.html` |
| `/api/*` | API端点 | `app.py` |

**API端点示例**:
- `GET /api/coin-change-tracker/latest` - 获取最新数据
- `GET /api/coin-change-tracker/history` - 获取历史数据
- `POST /api/liquidation/mark-notify` - 爆仓通知

### 数据目录映射

| 数据类型 | 目录 | 文件格式 |
|---------|------|----------|
| 币种涨跌幅 | `data/coin_change_tracker/` | `coin_change_YYYYMMDD.jsonl` |
| 日常预判 | `data/daily_predictions/` | `prediction_YYYYMMDD.jsonl` |
| 爆仓数据 | `data/liquidation_1h/` | `liquidation_1h_YYYYMMDD.jsonl` |
| 市场情绪 | `data/market_sentiment/` | `sentiment_YYYYMMDD.jsonl` |
| RSI数据 | `data/coin_change_tracker/` | `rsi_YYYYMMDD.jsonl` |

---

## 数据恢复

### 完整数据恢复

备份已包含**所有历史数据**（非7天），直接解压即可使用。

### 验证数据完整性

```bash
cd /home/user/webapp/data

# 检查币种涨跌幅数据
ls -lh coin_change_tracker/
wc -l coin_change_tracker/*.jsonl

# 检查日常预判数据
ls -lh daily_predictions/
cat daily_predictions/prediction_$(date +%Y%m%d).jsonl | jq .

# 检查爆仓数据
ls -lh liquidation_1h/

# 统计数据总大小
du -sh .
```

### 数据目录权限

```bash
# 确保数据目录可读写
chmod -R 755 /home/user/webapp/data
chown -R user:user /home/user/webapp/data
```

---

## 故障排查

### 问题1: Flask应用无法启动

**症状**: PM2显示flask-app状态为`errored`

**排查步骤**:
```bash
# 查看错误日志
pm2 logs flask-app --lines 50

# 手动测试启动
cd /home/user/webapp
python3 app.py

# 检查端口占用
lsof -i :9002
netstat -tulpn | grep 9002
```

**常见原因**:
- 端口9002被占用
- Python依赖未安装
- 环境变量配置错误

### 问题2: 数据采集器不工作

**症状**: 数据文件不更新

**排查步骤**:
```bash
# 检查采集器状态
pm2 list | grep collector

# 查看采集器日志
pm2 logs coin-change-tracker --lines 50

# 手动运行采集器测试
cd /home/user/webapp
python3 source_code/coin_change_tracker_collector.py
```

### 问题3: Telegram通知不发送

**症状**: 不收到Telegram消息

**排查步骤**:
```bash
# 检查Telegram配置
cat config/configs/telegram_config.json

# 测试Telegram连接
python3 << EOF
import requests
TOKEN = "your_bot_token"
CHAT_ID = "your_chat_id"
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
data = {"chat_id": CHAT_ID, "text": "测试消息"}
response = requests.post(url, json=data)
print(response.json())
EOF
```

### 问题4: 权限错误

**症状**: 无法读写文件

**解决方案**:
```bash
# 修复所有权限
cd /home/user/webapp
sudo chown -R user:user .
chmod -R 755 .
chmod -R 777 data/
chmod -R 777 logs/
```

### 问题5: 内存不足

**症状**: 服务频繁重启

**解决方案**:
```bash
# 查看内存使用
free -h
pm2 list  # 查看每个进程的内存

# 调整PM2内存限制
pm2 delete all
pm2 start ecosystem.config.js --max-memory-restart 2G
```

---

## 快速命令参考

### PM2常用命令

```bash
# 启动所有服务
pm2 start ecosystem.config.js

# 停止所有服务
pm2 stop all

# 重启所有服务
pm2 restart all

# 删除所有服务
pm2 delete all

# 查看服务列表
pm2 list

# 查看实时日志
pm2 logs

# 查看特定服务日志
pm2 logs flask-app

# 监控服务
pm2 monit

# 保存PM2配置
pm2 save

# 设置开机自启
pm2 startup
```

### 数据管理命令

```bash
# 清理7天前的日志
find data/ -name "*.jsonl" -mtime +7 -delete

# 备份数据
tar -czf data_backup_$(date +%Y%m%d).tar.gz data/

# 查看数据统计
find data/ -name "*.jsonl" | wc -l
du -sh data/*
```

### Flask调试命令

```bash
# 手动启动Flask（调试模式）
cd /home/user/webapp
FLASK_ENV=development python3 app.py

# 测试API
curl http://localhost:9002/api/coin-change-tracker/latest | jq .

# 检查路由
python3 << EOF
from app import app
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule.rule}")
EOF
```

---

## 联系信息

如有问题，请参考以下文档：
- 📚 完整文档目录: `/home/user/webapp/docs/`
- 🔧 技术支持: 查看 `docs/` 目录下的相关文档
- 📖 API文档: 参考 `app.py` 中的注释

---

**文档版本**: 2.0  
**最后更新**: 2026-02-27  
**适用版本**: webapp v3.6+
