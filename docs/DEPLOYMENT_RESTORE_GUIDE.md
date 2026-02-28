# WebApp 系统完整部署与恢复指南

## 📋 文档信息

- **创建日期**: 2026-02-07
- **适用版本**: WebApp v1.0+
- **备份格式**: .tar.gz 归档文件
- **目标系统**: Ubuntu/Debian Linux

---

## 📦 备份文件结构

备份归档 `webapp-backup-YYYYMMDD_HHMMSS.tar.gz` 包含以下内容：

```
webapp-backup-YYYYMMDD_HHMMSS/
├── code/                           # 核心代码
│   ├── python-code.tar.gz         # Python 代码（app.py, source_code/, major-events-system/, etc.）
│   └── templates-static.tar.gz    # HTML 模板和静态文件
├── configs/                        # 配置文件
│   └── app-configs.tar.gz         # 所有配置文件（configs/, *.json, .env, etc.）
├── data/                          # 数据
│   ├── databases.tar.gz           # SQLite 数据库文件
│   └── recent-data-7days.tar.gz  # 最近7天的 JSONL 数据文件
├── pm2/                           # PM2 进程管理
│   ├── pm2-process-list.txt      # PM2 进程列表（文本格式）
│   ├── pm2-apps-detail.json      # PM2 应用详细配置（JSON格式）
│   ├── dump.pm2                  # PM2 自动恢复文件
│   └── pm2/ (directory)          # PM2 生态配置文件
├── system/                        # 系统信息
│   ├── python-version.txt        # Python 版本
│   ├── pip-packages.txt          # 已安装的 Python 包列表
│   ├── requirements.txt          # pip freeze 输出（可直接安装）
│   ├── node-version.txt          # Node.js 版本
│   ├── npm-global-packages.txt   # 全局 npm 包
│   ├── systemd-services.txt      # Systemd 服务状态
│   ├── git-recent-commits.txt    # 最近的 Git 提交
│   ├── git-status.txt            # Git 工作区状态
│   └── git-remotes.txt           # Git 远程仓库配置
├── docs/                          # 文档
│   └── markdown-docs.tar.gz      # 所有 Markdown 文档
└── BACKUP_INFO.txt                # 备份元数据和文件清单
```

---

## 🚀 快速恢复步骤

### 前置条件

1. **系统要求**:
   - Ubuntu 20.04+ 或 Debian 11+
   - 至少 4GB RAM
   - 至少 20GB 磁盘空间

2. **必需软件**:
   - Python 3.8+
   - Node.js 16+
   - PM2（全局安装）
   - Git

### 步骤 1: 系统准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础依赖
sudo apt install -y python3 python3-pip python3-venv \
    nodejs npm git curl wget build-essential \
    sqlite3 supervisor nginx

# 安装 PM2（全局）
sudo npm install -g pm2

# 确认版本
python3 --version
node --version
pm2 --version
```

### 步骤 2: 下载并解压备份

```bash
# 假设备份文件已上传到服务器
cd /tmp

# 解压备份（替换 YYYYMMDD_HHMMSS 为实际时间戳）
tar -xzf webapp-backup-YYYYMMDD_HHMMSS.tar.gz

# 验证 MD5（可选但推荐）
md5sum -c webapp-backup-YYYYMMDD_HHMMSS.tar.gz.md5
```

### 步骤 3: 恢复代码和配置

```bash
# 创建目标目录
sudo mkdir -p /home/user/webapp
sudo chown -R $USER:$USER /home/user/webapp
cd /home/user/webapp

# 解压 Python 代码
tar -xzf /tmp/webapp-backup-YYYYMMDD_HHMMSS/code/python-code.tar.gz -C /home/user/webapp/

# 解压 HTML 模板和静态文件
tar -xzf /tmp/webapp-backup-YYYYMMDD_HHMMSS/code/templates-static.tar.gz -C /home/user/webapp/

# 解压配置文件
tar -xzf /tmp/webapp-backup-YYYYMMDD_HHMMSS/configs/app-configs.tar.gz -C /home/user/webapp/
```

### 步骤 4: 恢复数据

```bash
# 解压数据库
tar -xzf /tmp/webapp-backup-YYYYMMDD_HHMMSS/data/databases.tar.gz -C /home/user/webapp/

# 解压最近数据（可选，如果需要历史数据）
tar -xzf /tmp/webapp-backup-YYYYMMDD_HHMMSS/data/recent-data-7days.tar.gz -C /home/user/webapp/

# 创建数据目录（如果不存在）
mkdir -p /home/user/webapp/data/{coin_price_tracker,sar_jsonl,sar_bias_stats,escape_signal_stats,panic_data}
```

### 步骤 5: 安装 Python 依赖

```bash
cd /home/user/webapp

# 从备份的 requirements.txt 安装
pip3 install -r /tmp/webapp-backup-YYYYMMDD_HHMMSS/system/requirements.txt

# 或者安装常用依赖（如果 requirements.txt 不完整）
pip3 install flask flask-cors requests pytz schedule pandas numpy \
    ccxt websocket-client python-telegram-bot
```

### 步骤 6: 恢复 PM2 进程

```bash
# 复制 PM2 配置
cp -r /tmp/webapp-backup-YYYYMMDD_HHMMSS/pm2/* /home/user/webapp/pm2/ 2>/dev/null || true

# 复制 PM2 dump 文件到 PM2 目录
mkdir -p ~/.pm2
cp /tmp/webapp-backup-YYYYMMDD_HHMMSS/pm2/dump.pm2 ~/.pm2/ 2>/dev/null || true

# 恢复 PM2 进程
cd /home/user/webapp
pm2 resurrect

# 或者手动启动核心服务
pm2 start pm2/ecosystem.config.js

# 查看进程状态
pm2 list
pm2 logs
```

### 步骤 7: 启动 Flask 应用

```bash
cd /home/user/webapp

# 如果 PM2 已启动 flask-app，跳过此步骤
# 否则手动启动
pm2 start app.py --name flask-app --interpreter python3

# 重启所有服务
pm2 restart all

# 保存 PM2 配置
pm2 save

# 设置 PM2 开机自启
pm2 startup
# 按照提示执行 sudo 命令
```

### 步骤 8: 验证部署

```bash
# 检查 PM2 进程
pm2 status

# 测试 Flask 应用
curl http://localhost:5000/

# 查看日志
pm2 logs flask-app --lines 50
pm2 logs major-events-monitor --lines 50

# 检查数据库
sqlite3 /home/user/webapp/databases/sar_slope_data.db "SELECT COUNT(*) FROM sar_slope_points;"
```

---

## 📊 PM2 进程管理详解

### 核心进程列表

根据备份中的 `pm2-process-list.txt`，系统通常包含以下进程：

| 进程名 | 类型 | 入口文件 | 说明 |
|--------|------|----------|------|
| **flask-app** | Python | app.py | 主 Flask Web 应用 |
| **major-events-monitor** | Python | major_events_monitor.py | 重大事件监控系统 |
| **coin-change-tracker** | Python | coin_price_collector.py | 27币涨跌幅追踪 |
| **sar-slope-collector** | Python | sar_slope_collector.py | SAR 斜率数据收集 |
| **sar-bias-stats-collector** | Python | sar_bias_stats_collector.py | SAR 偏向统计 |
| **escape-signal-collector** | Python | escape_signal_collector.py | 逃顶信号收集 |
| **panic-collector** | Python | panic_collector.py | 恐慌指数收集 |
| **liquidation-1h-collector** | Python | liquidation_1h_collector.py | 1小时爆仓数据 |
| **price-baseline-collector** | Python | price_baseline_collector.py | 价格基准收集 |
| **anchor-profit-monitor** | Python | anchor_profit_monitor.py | 锚定收益监控 |

### PM2 常用命令

```bash
# 查看所有进程
pm2 list

# 查看进程详细信息
pm2 show flask-app

# 启动/停止/重启
pm2 start flask-app
pm2 stop flask-app
pm2 restart flask-app

# 重启所有进程
pm2 restart all

# 删除进程
pm2 delete flask-app

# 查看日志
pm2 logs                    # 所有进程
pm2 logs flask-app         # 特定进程
pm2 logs --lines 100       # 最近100行

# 监控
pm2 monit

# 保存当前进程列表
pm2 save

# 恢复已保存的进程
pm2 resurrect

# 清空日志
pm2 flush
```

---

## 🔧 配置文件说明

### 1. Flask 应用配置

**主配置文件**: `app.py`

- 端口: `5000`（默认）
- 调试模式: `DEBUG = False`（生产环境）
- CORS: 已启用跨域支持

**环境变量** (`.env` 文件):
```bash
FLASK_ENV=production
FLASK_APP=app.py
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_PATH=/home/user/webapp/databases
```

### 2. PM2 生态配置

**文件**: `pm2/ecosystem.config.js`

示例配置：
```javascript
module.exports = {
  apps: [
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
        NODE_ENV: 'production',
        PORT: 5000
      }
    },
    {
      name: 'major-events-monitor',
      script: 'major-events-system/major_events_monitor.py',
      interpreter: 'python3',
      cwd: '/home/user/webapp',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '300M'
    }
    // ... 其他进程配置
  ]
};
```

### 3. 数据库路径

- **SAR Slope**: `/home/user/webapp/databases/sar_slope_data.db`
- **其他数据**: JSONL 格式存储在 `/home/user/webapp/data/` 各子目录

---

## 🌐 Nginx 反向代理配置（可选）

如果需要通过域名访问，配置 Nginx：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

保存到 `/etc/nginx/sites-available/webapp`，然后：

```bash
sudo ln -s /etc/nginx/sites-available/webapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔍 故障排查

### 问题 1: Flask 应用无法启动

**症状**: `pm2 logs flask-app` 显示 `ModuleNotFoundError` 或类似错误

**解决方案**:
```bash
# 重新安装依赖
cd /home/user/webapp
pip3 install -r /tmp/webapp-backup-YYYYMMDD_HHMMSS/system/requirements.txt

# 检查 Python 路径
which python3
python3 --version

# 重启进程
pm2 restart flask-app
```

### 问题 2: PM2 进程频繁重启

**症状**: `pm2 list` 显示 `restart` 次数很高

**解决方案**:
```bash
# 查看错误日志
pm2 logs flask-app --err --lines 100

# 常见原因：
# 1. 端口被占用
sudo lsof -i :5000
# 杀死占用进程或更改端口

# 2. 内存不足
pm2 show flask-app
# 增加 max_memory_restart 限制

# 3. Python 模块缺失
# 重新安装依赖
```

### 问题 3: 数据库文件损坏

**症状**: SQLite 报错 "database disk image is malformed"

**解决方案**:
```bash
# 备份损坏的数据库
cp databases/sar_slope_data.db databases/sar_slope_data.db.corrupted

# 尝试修复
sqlite3 databases/sar_slope_data.db "PRAGMA integrity_check;"

# 如果无法修复，从备份恢复
tar -xzf /tmp/webapp-backup-YYYYMMDD_HHMMSS/data/databases.tar.gz -C /home/user/webapp/
```

### 问题 4: API 端点返回 500 错误

**症状**: 浏览器或 `curl` 访问 API 返回 500 Internal Server Error

**解决方案**:
```bash
# 查看 Flask 日志
pm2 logs flask-app --lines 200

# 检查数据文件是否存在
ls -lh /home/user/webapp/data/

# 检查文件权限
chmod -R 755 /home/user/webapp/data/
chown -R $USER:$USER /home/user/webapp/data/

# 重启 Flask
pm2 restart flask-app
```

---

## 📅 定期维护

### 每日任务

```bash
# 检查进程状态
pm2 status

# 清理旧日志（保留最近7天）
find /home/user/webapp/logs/ -name "*.log" -mtime +7 -delete

# 备份数据库
cp /home/user/webapp/databases/sar_slope_data.db \
   /home/user/webapp/backups/sar_slope_data_$(date +%Y%m%d).db
```

### 每周任务

```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 检查磁盘空间
df -h

# 清理 PM2 日志
pm2 flush

# 重启所有服务
pm2 restart all
```

### 每月任务

```bash
# 创建完整备份
cd /home/user/webapp
bash create_deployment_backup.sh

# 更新 Python 包
pip3 list --outdated
# 根据需要更新关键包

# 检查 Git 提交历史，确认代码同步
git log --oneline -10
```

---

## 🔐 安全建议

1. **环境变量**: 确保 `.env` 文件不被提交到 Git
   ```bash
   echo ".env" >> .gitignore
   ```

2. **数据库权限**: 限制数据库文件访问
   ```bash
   chmod 600 /home/user/webapp/databases/*.db
   ```

3. **防火墙**: 如果使用云服务器，配置安全组规则
   - 只开放必要端口（80, 443, SSH）
   - 5000 端口不要直接暴露到公网

4. **Telegram Bot Token**: 妥善保管，定期轮换

5. **定期更新**: 保持系统和依赖包最新版本

---

## 📞 支持信息

### 系统访问地址

- **主页**: `http://your-server-ip:5000/`
- **重大事件监控**: `http://your-server-ip:5000/major-events`
- **SAR 偏向趋势**: `http://your-server-ip:5000/sar-bias-trend`
- **恐慌指数**: `http://your-server-ip:5000/panic`
- **价格比较**: `http://your-server-ip:5000/price-comparison`
- **27币涨跌幅**: `http://your-server-ip:5000/coin-change-tracker`

### 关键 API 端点

- **当前状态**: `/api/major-events/current-status`
- **SAR 统计**: `/api/sar-slope/bias-stats`
- **爆仓数据**: `/api/panic/latest`
- **数据健康监控**: `/api/data-health-monitor/status`

### 日志位置

- **PM2 日志**: `~/.pm2/logs/`
- **应用日志**: `/home/user/webapp/logs/`
- **系统日志**: `/var/log/syslog` 或 `/var/log/messages`

---

## 📝 附录

### A. 从头开始部署（无备份文件）

如果没有备份，从 Git 仓库克隆：

```bash
# 克隆代码
git clone <your-repo-url> /home/user/webapp
cd /home/user/webapp

# 安装依赖
pip3 install -r requirements.txt

# 初始化数据库
python3 scripts/init_database.py

# 启动服务
pm2 start pm2/ecosystem.config.js
pm2 save
```

### B. 环境变量示例

创建 `.env` 文件：

```bash
# Flask 配置
FLASK_ENV=production
FLASK_APP=app.py
FLASK_DEBUG=False

# Telegram Bot
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=-1001234567890

# 数据库路径
DATABASE_PATH=/home/user/webapp/databases

# API 配置
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret

# 日志级别
LOG_LEVEL=INFO
```

### C. requirements.txt 示例

```txt
Flask==2.3.0
Flask-Cors==4.0.0
requests==2.31.0
pytz==2023.3
schedule==1.2.0
pandas==2.0.3
numpy==1.24.3
ccxt==4.0.0
websocket-client==1.6.1
python-telegram-bot==20.3
SQLAlchemy==2.0.19
```

---

## ✅ 部署检查清单

使用此清单确保部署完整：

- [ ] 系统依赖已安装（Python, Node.js, PM2）
- [ ] 备份文件已解压到正确位置
- [ ] 代码文件已恢复
- [ ] 配置文件已恢复（包括 .env）
- [ ] 数据库文件已恢复
- [ ] Python 依赖已安装（`pip3 list` 确认）
- [ ] PM2 进程已启动（`pm2 list` 确认）
- [ ] Flask 应用可访问（`curl http://localhost:5000/`）
- [ ] 所有收集器正常运行（检查 PM2 日志）
- [ ] 数据文件正在更新（检查最后修改时间）
- [ ] Telegram 通知功能正常（如果配置）
- [ ] Nginx 配置正确（如果使用）
- [ ] 防火墙规则已设置
- [ ] PM2 开机自启已配置（`pm2 startup`）

---

## 🎯 总结

本指南涵盖了 WebApp 系统的完整备份和恢复流程，包括：

1. ✅ 备份文件结构说明
2. ✅ 快速恢复步骤（8 步）
3. ✅ PM2 进程管理详解
4. ✅ 配置文件说明
5. ✅ 故障排查指南
6. ✅ 定期维护建议
7. ✅ 安全建议
8. ✅ 系统访问地址和 API 端点

遵循本指南，您可以在 **30 分钟内** 完成系统的完整恢复。

---

**最后更新**: 2026-02-07  
**文档版本**: 1.0  
**维护者**: WebApp Team
