# 🚀 加密货币数据分析系统 - 完整部署文档

## 📦 备份信息

### 备份文件
- **路径**: `/tmp/webapp_full_backup_20260216_173656.tar.gz`
- **大小**: 490MB (压缩后)
- **原始大小**: ~6.3GB (未压缩)
- **创建时间**: 2026-02-16 17:36:56
- **备份范围**: 完整项目（所有数据、代码、配置）

### 备份内容
```
webapp/
├── data/               # 2.9GB - 所有JSONL数据文件
├── source_code/        # 460KB - Python采集器和管理器
├── templates/          # 6.0MB - HTML模板文件  
├── price_position_v2/  # 价格位置数据库和配置
├── logs/               # 日志文件（不包含在备份中）
├── app.py              # 876KB - Flask主应用
├── *.py                # 88个Python文件
├── *.md                # 440个Markdown文档
└── 其他配置文件
```

---

## 🏗️ 系统架构

### 核心组件

#### 1. Flask Web应用
- **文件**: `app.py` (876KB, 24000+行代码)
- **端口**: 9002
- **功能**: 提供Web界面和RESTful API
- **PM2进程名**: `flask-app`

#### 2. 数据采集器 (23个)
所有采集器位于 `source_code/` 目录

| 进程名 | 脚本文件 | 功能 | 采集频率 |
|--------|----------|------|----------|
| coin-change-tracker | coin_change_tracker.py | 币种涨跌追踪 | 1分钟 |
| crypto-index-collector | crypto_index_collector.py | 加密货币指数 | 5分钟 |
| dashboard-jsonl-manager | dashboard_jsonl_manager.py | 仪表盘数据管理 | 实时 |
| financial-indicators-collector | financial_indicators_collector.py | 财务指标采集 | 5分钟 |
| gdrive-jsonl-manager | gdrive_jsonl_manager.py | Google Drive数据管理 | 实时 |
| liquidation-1h-collector | liquidation_1h_collector.py | 1小时爆仓数据 | 3分钟 |
| liquidation-alert-monitor | liquidation_alert_monitor.py | 爆仓告警监控 | 实时 |
| new-high-low-collector | new_high_low_collector.py | 新高新低采集 | 5分钟 |
| okx-day-change-collector | okx_day_change_collector.py | OKX日涨跌 | 1分钟 |
| okx-trade-history-collector | okx_trade_history_collector.py | OKX交易历史 | 1分钟 |
| okx-trading-marks-collector | okx_trading_marks_collector.py | OKX交易标记 | 1分钟 |
| panic-wash-collector | panic_wash_collector.py | 恐慌洗盘指数 | 3分钟 |
| price-baseline-collector | price_baseline_collector.py | 价格基线 | 1分钟 |
| price-comparison-collector | price_comparison_collector.py | 价格对比 | 3分钟 |
| price-position-collector | price_position_collector.py | 价格位置 | 3分钟 |
| price-speed-collector | price_speed_10m_collector.py | 10分钟涨速 | 1分钟 |
| sar-bias-stats-collector | sar_bias_stats_collector.py | SAR乖离统计 | 3分钟 |
| sar-slope-collector | sar_slope_collector.py | SAR斜率 | 3分钟 |
| signal-collector | signal_collector.py | 信号采集（占位） | 1分钟 |
| signal-stats-collector | signal_stats_collector.py | 信号统计 | 3分钟 |
| system-health-monitor-v2 | system_health_monitor_v2.py | 系统健康监控 | 1分钟 |
| v1v2-collector | v1v2_collector.py | V1V2数据采集 | 5分钟 |

#### 3. 数据存储
```
data/
├── coin_change_tracker/    # 币种涨跌追踪数据
├── crypto_index/           # 加密货币指数数据
├── data_statistics.json    # 数据统计汇总
├── liquidation_1h/         # 1小时爆仓数据
├── new_high_low/           # 新高新低数据
├── okx_auto_strategy/      # OKX自动策略
├── okx_trading_history/    # OKX交易历史
├── okx_trading_jsonl/      # OKX交易JSONL
├── okx_trading_logs/       # OKX交易日志
├── panic_jsonl/            # 恐慌指数JSONL
│   └── panic_wash_index.jsonl  # 7747条记录（2026-02-01至今）
├── price_comparison/       # 价格对比数据
├── price_position/         # 价格位置数据
├── price_speed_10m/        # 10分钟涨速数据
├── sar_bias_stats/         # SAR乖离统计
├── sar_jsonl/              # SAR JSONL数据（28个币种）
├── signal_stats/           # 信号统计数据
└── support_resistance/     # 支撑压力数据
```

#### 4. 数据库
```
price_position_v2/config/data/db/
└── price_position.db       # 9.1MB SQLite数据库
    ├── price_position      # 价格位置表
    └── signal_timeline     # 信号时间线表
```

---

## 🔧 依赖环境

### 系统依赖 (apt)
```bash
# Python 3 和 pip
apt-get install python3 python3-pip

# Node.js 和 npm (用于PM2)
apt-get install nodejs npm

# SQLite3 (数据库)
apt-get install sqlite3

# 其他工具
apt-get install curl wget git jq
```

### Python依赖 (pip)
```bash
# Flask核心
Flask==3.1.5
Werkzeug==3.1.5

# HTTP客户端
requests==2.31.0

# 数据处理
pandas==2.2.0
numpy==1.26.3

# 时区处理
pytz==2024.1

# 数据库
sqlite3 (Python内置)

# 加密货币相关
ccxt==4.2.0  # 交易所API

# 进程管理
supervisor==4.2.5  # (可选，部分场景使用)
```

### Node.js依赖 (npm)
```bash
# PM2进程管理器
npm install -g pm2
```

---

## 📋 完整部署步骤

### 步骤 1: 环境准备
```bash
# 1.1 安装系统依赖
sudo apt-get update
sudo apt-get install -y python3 python3-pip nodejs npm sqlite3 curl wget git jq

# 1.2 安装PM2
sudo npm install -g pm2

# 1.3 创建工作目录
mkdir -p /home/user
cd /home/user
```

### 步骤 2: 恢复备份
```bash
# 2.1 解压备份文件
cd /home/user
tar -xzf /tmp/webapp_full_backup_20260216_173656.tar.gz

# 2.2 验证解压
ls -lh webapp/
du -sh webapp/
```

### 步骤 3: 安装Python依赖
```bash
cd /home/user/webapp

# 3.1 升级pip
python3 -m pip install --upgrade pip

# 3.2 安装所有依赖
pip3 install Flask==3.1.5 Werkzeug==3.1.5 requests==2.31.0 \
             pandas==2.2.0 numpy==1.26.3 pytz==2024.1 ccxt==4.2.0
```

### 步骤 4: 配置PM2进程
```bash
cd /home/user/webapp

# 4.1 创建PM2配置文件
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'flask-app',
      script: 'python3',
      args: 'app.py',
      cwd: '/home/user/webapp',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        FLASK_APP: 'app.py',
        FLASK_ENV: 'production',
        PYTHONUNBUFFERED: '1'
      }
    },
    {
      name: 'coin-change-tracker',
      script: 'python3',
      args: 'source_code/coin_change_tracker.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'crypto-index-collector',
      script: 'python3',
      args: 'source_code/crypto_index_collector.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'dashboard-jsonl-manager',
      script: 'python3',
      args: 'source_code/dashboard_jsonl_manager.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'financial-indicators-collector',
      script: 'python3',
      args: 'source_code/financial_indicators_collector.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'gdrive-jsonl-manager',
      script: 'python3',
      args: 'source_code/gdrive_jsonl_manager.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'liquidation-1h-collector',
      script: 'python3',
      args: 'source_code/liquidation_1h_collector.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'liquidation-alert-monitor',
      script: 'python3',
      args: 'source_code/liquidation_alert_monitor.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'new-high-low-collector',
      script: 'python3',
      args: 'source_code/new_high_low_collector.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'okx-day-change-collector',
      script: 'python3',
      args: 'source_code/okx_day_change_collector.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'okx-trade-history-collector',
      script: 'python3',
      args: 'source_code/okx_trade_history_collector.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'okx-trading-marks-collector',
      script: 'python3',
      args: 'source_code/okx_trading_marks_collector.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'panic-wash-collector',
      script: 'python3',
      args: 'source_code/panic_wash_collector.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'price-baseline-collector',
      script: 'python3',
      args: 'source_code/price_baseline_collector.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'price-comparison-collector',
      script: 'python3',
      args: 'source_code/price_comparison_collector.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'price-position-collector',
      script: 'python3',
      args: 'source_code/price_position_collector.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'price-speed-collector',
      script: 'python3',
      args: 'source_code/price_speed_10m_collector.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'sar-bias-stats-collector',
      script: 'python3',
      args: 'source_code/sar_bias_stats_collector.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'sar-slope-collector',
      script: 'python3',
      args: 'source_code/sar_slope_collector.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'signal-collector',
      script: 'python3',
      args: 'source_code/signal_collector.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'signal-stats-collector',
      script: 'python3',
      args: 'source_code/signal_stats_collector.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'system-health-monitor-v2',
      script: 'python3',
      args: 'source_code/system_health_monitor_v2.py',
      cwd: '/home/user/webapp'
    },
    {
      name: 'v1v2-collector',
      script: 'python3',
      args: 'source_code/v1v2_collector.py',
      cwd: '/home/user/webapp'
    }
  ]
};
EOF

# 4.2 启动所有进程
pm2 start ecosystem.config.js

# 4.3 设置开机自启
pm2 startup
pm2 save
```

### 步骤 5: 验证部署
```bash
# 5.1 检查所有进程状态
pm2 list

# 5.2 检查Flask应用
curl http://localhost:9002/

# 5.3 检查日志
pm2 logs flask-app --lines 50
pm2 logs panic-wash-collector --lines 20

# 5.4 检查数据文件
ls -lh data/panic_jsonl/panic_wash_index.jsonl
tail -5 data/panic_jsonl/panic_wash_index.jsonl | jq -r '.beijing_time'

# 5.5 检查数据库
sqlite3 price_position_v2/config/data/db/price_position.db "SELECT COUNT(*) FROM price_position;"
```

---

## 🌐 Flask路由映射

### 主要页面路由
```python
# 首页和仪表盘
/                           -> templates/index.html
/dashboard                  -> templates/dashboard.html

# 价格相关
/price-comparison           -> templates/price_comparison.html
/price-position             -> templates/price_position_unified.html
/price-speed-10m            -> templates/price_speed_10m_monitor.html

# 技术指标
/sar-bias                   -> templates/sar_bias_monitor.html
/support-resistance         -> templates/support_resistance.html

# 交易相关
/okx-auto-trade             -> templates/okx_auto_trade.html
/okx-trading-marks          -> templates/okx_trading_marks.html

# 恐慌指数
/panic                      -> templates/panic_new.html

# 爆仓数据
/liquidation-1h             -> templates/liquidation_1h.html
/liquidation-monthly        -> templates/liquidation_monthly.html

# 系统监控
/system-health              -> templates/system_health_v2.html
```

### API路由
```python
# 服务器信息
GET  /api/server-date                    # 获取服务器日期（北京时间）

# 价格位置API
GET  /api/price-position/list            # 价格位置列表
GET  /api/price-position/list-detailed   # 价格位置详细信息

# 恐慌指数API
GET  /api/panic/latest                   # 最新恐慌指数
GET  /api/panic/hour1-curve              # 1小时爆仓曲线
GET  /api/panic/history                  # 历史数据
GET  /api/panic/history-range            # 指定范围历史数据

# 信号API
GET  /api/signal-timeline/data           # 信号时间线数据
GET  /api/signal-timeline/computed-peaks # 后端计算峰值

# 爆仓API
GET  /api/liquidation-1h/latest          # 最新爆仓数据
GET  /api/liquidation-1h/history         # 历史爆仓数据

# SAR API
GET  /api/sar-bias/list                  # SAR乖离列表
GET  /api/sar-slope/latest               # SAR斜率最新数据

# OKX交易API
GET  /api/okx-trading/latest             # OKX最新交易
GET  /api/okx-day-change/latest          # OKX日涨跌
```

---

## 🔍 故障排查

### 问题 1: Flask无法启动
```bash
# 检查端口占用
lsof -i :9002

# 检查Python依赖
pip3 list | grep Flask

# 查看详细错误
pm2 logs flask-app --lines 100 --err
```

### 问题 2: 采集器停止工作
```bash
# 重启特定采集器
pm2 restart panic-wash-collector

# 重启所有采集器
pm2 restart all

# 查看错误日志
pm2 logs panic-wash-collector --err
```

### 问题 3: 数据文件缺失
```bash
# 检查数据目录
ls -lh data/

# 检查数据文件
tail data/panic_jsonl/panic_wash_index.jsonl

# 手动运行采集器测试
cd /home/user/webapp
python3 source_code/panic_wash_collector.py
```

### 问题 4: 数据库错误
```bash
# 检查数据库文件
ls -lh price_position_v2/config/data/db/price_position.db

# 检查数据库完整性
sqlite3 price_position_v2/config/data/db/price_position.db "PRAGMA integrity_check;"

# 查看表结构
sqlite3 price_position_v2/config/data/db/price_position.db ".schema"
```

---

## 📊 监控与维护

### 日常监控命令
```bash
# 查看所有进程状态
pm2 list

# 查看系统资源占用
pm2 monit

# 查看最近日志
pm2 logs --lines 50

# 查看特定进程日志
pm2 logs flask-app
pm2 logs panic-wash-collector

# 重启所有进程
pm2 restart all

# 重载所有进程（零停机）
pm2 reload all
```

### 数据备份脚本
```bash
#!/bin/bash
# backup.sh - 定期备份脚本

BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/webapp_backup_$DATE.tar.gz"

mkdir -p $BACKUP_DIR

# 创建备份
cd /home/user
tar -czf $BACKUP_FILE \
  --exclude='webapp/logs/*.log' \
  --exclude='webapp/__pycache__' \
  webapp/

# 保留最近7天的备份
find $BACKUP_DIR -name "webapp_backup_*.tar.gz" -mtime +7 -delete

echo "备份完成: $BACKUP_FILE"
ls -lh $BACKUP_FILE
```

### 数据清理脚本
```bash
#!/bin/bash
# cleanup.sh - 清理旧数据

# 清理30天前的日志
find /home/user/webapp/logs/ -name "*.log" -mtime +30 -delete

# 清理90天前的历史数据（可选）
# find /home/user/webapp/data/ -name "*.jsonl" -mtime +90 -delete

echo "数据清理完成"
```

---

## 🔐 安全建议

1. **设置防火墙规则**
```bash
# 只允许本地访问Flask
ufw allow from 127.0.0.1 to any port 9002

# 或使用nginx反向代理
ufw allow 80
ufw allow 443
```

2. **定期更新依赖**
```bash
pip3 list --outdated
pip3 install --upgrade Flask requests pandas
```

3. **日志轮转**
```bash
# 配置logrotate
cat > /etc/logrotate.d/webapp << EOF
/home/user/webapp/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF
```

---

## 📞 技术支持

- **备份位置**: `/tmp/webapp_full_backup_20260216_173656.tar.gz`
- **项目大小**: 6.3GB (未压缩), 490MB (压缩)
- **Python版本**: 3.12.11
- **Flask版本**: 3.1.5
- **PM2版本**: 最新稳定版

---

## ✅ 部署检查清单

- [ ] 系统依赖已安装 (Python, Node.js, SQLite)
- [ ] PM2已全局安装
- [ ] 备份文件已解压到 `/home/user/webapp`
- [ ] Python依赖已安装
- [ ] PM2配置文件已创建 (`ecosystem.config.js`)
- [ ] 所有23个进程已启动
- [ ] Flask应用可访问 (http://localhost:9002)
- [ ] 数据采集器正常工作
- [ ] 数据文件正常更新
- [ ] 数据库可正常访问
- [ ] PM2开机自启已设置
- [ ] 监控脚本已配置
- [ ] 备份策略已实施

---

**文档版本**: v1.0  
**创建日期**: 2026-02-16  
**最后更新**: 2026-02-17  
**维护者**: System Administrator
