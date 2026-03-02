#!/bin/bash
#
# 完整交易系统备份脚本
# 备份所有代码、配置、数据、依赖到 /tmp/trading_system_backup_YYYYMMDD_HHMMSS.tar.gz
# 
# 使用方法: bash backup_full_system.sh
#

set -e  # 遇到错误立即退出

# 配置
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="trading_system_backup_${TIMESTAMP}"
BACKUP_DIR="/tmp/${BACKUP_NAME}"
BACKUP_FILE="/tmp/${BACKUP_NAME}.tar.gz"
SOURCE_DIR="/home/user/webapp"

echo "============================================================"
echo "🔄 开始完整系统备份"
echo "============================================================"
echo "📅 时间戳: ${TIMESTAMP}"
echo "📁 源目录: ${SOURCE_DIR}"
echo "💾 备份目录: ${BACKUP_DIR}"
echo "📦 备份文件: ${BACKUP_FILE}"
echo "============================================================"
echo ""

# 1. 创建临时备份目录
echo "📁 [1/10] 创建备份目录..."
mkdir -p "${BACKUP_DIR}"
cd "${SOURCE_DIR}"

# 2. 备份核心 Python 代码和应用
echo "🐍 [2/10] 备份 Python 代码..."
mkdir -p "${BACKUP_DIR}/python_core"
cp -v *.py "${BACKUP_DIR}/python_core/" 2>/dev/null || true
echo "   ✅ 主目录 Python 文件: $(ls -1 *.py 2>/dev/null | wc -l) 个"

# 3. 备份 source_code 目录
echo "📚 [3/10] 备份 source_code/ 目录..."
if [ -d "source_code" ]; then
    cp -r source_code "${BACKUP_DIR}/"
    echo "   ✅ source_code/ 大小: $(du -sh source_code | awk '{print $1}')"
else
    echo "   ⚠️  source_code/ 不存在"
fi

# 4. 备份 panic 系统
echo "⚠️  [4/10] 备份 panic 系统目录..."
if [ -d "panic_paged_v2" ]; then
    cp -r panic_paged_v2 "${BACKUP_DIR}/"
    echo "   ✅ panic_paged_v2/ 大小: $(du -sh panic_paged_v2 | awk '{print $1}')"
fi
if [ -d "panic_v3" ]; then
    cp -r panic_v3 "${BACKUP_DIR}/"
    echo "   ✅ panic_v3/ 大小: $(du -sh panic_v3 | awk '{print $1}')"
fi

# 5. 备份其他核心目录
echo "📂 [5/10] 备份核心目录..."
for dir in code config monitors scripts tests static templates; do
    if [ -d "$dir" ]; then
        cp -r "$dir" "${BACKUP_DIR}/"
        echo "   ✅ ${dir}/ 大小: $(du -sh $dir | awk '{print $1}')"
    fi
done

# 6. 备份数据文件（所有数据，不只是7天）
echo "💾 [6/10] 备份数据目录（完整数据）..."
if [ -d "data" ]; then
    mkdir -p "${BACKUP_DIR}/data"
    echo "   🔄 正在复制数据文件（可能需要几分钟）..."
    cp -r data/* "${BACKUP_DIR}/data/" 2>/dev/null || true
    DATA_SIZE=$(du -sh "${BACKUP_DIR}/data" | awk '{print $1}')
    DATA_COUNT=$(find "${BACKUP_DIR}/data" -type f | wc -l)
    echo "   ✅ data/ 大小: ${DATA_SIZE}, 文件数: ${DATA_COUNT}"
fi

# 7. 备份配置文件
echo "⚙️  [7/10] 备份配置和依赖文件..."
mkdir -p "${BACKUP_DIR}/config_files"
for file in package.json package-lock.json requirements.txt ecosystem.config.js pm2.config.js .env .gitignore README.md; do
    if [ -f "$file" ]; then
        cp -v "$file" "${BACKUP_DIR}/config_files/"
    fi
done

# 8. 导出 PM2 配置
echo "🔧 [8/10] 导出 PM2 配置..."
pm2 save 2>/dev/null || true
if [ -f "$HOME/.pm2/dump.pm2" ]; then
    cp "$HOME/.pm2/dump.pm2" "${BACKUP_DIR}/config_files/pm2_dump.pm2"
    echo "   ✅ PM2 进程列表已导出"
fi

# 导出当前 PM2 列表为JSON
pm2 jlist > "${BACKUP_DIR}/config_files/pm2_processes.json" 2>/dev/null || true
echo "   ✅ PM2 进程详情已导出"

# 9. 备份系统依赖信息
echo "📦 [9/10] 记录系统依赖信息..."
mkdir -p "${BACKUP_DIR}/system_info"

# Python 依赖
pip3 list --format=freeze > "${BACKUP_DIR}/system_info/pip_freeze.txt" 2>/dev/null || true
echo "   ✅ Python 包列表: $(wc -l < ${BACKUP_DIR}/system_info/pip_freeze.txt) 个"

# APT 包（如果有权限）
dpkg -l > "${BACKUP_DIR}/system_info/apt_packages.txt" 2>/dev/null || true
echo "   ✅ APT 包列表已导出"

# Node 版本和 npm 全局包
node --version > "${BACKUP_DIR}/system_info/node_version.txt" 2>/dev/null || true
npm list -g --depth=0 > "${BACKUP_DIR}/system_info/npm_global_packages.txt" 2>/dev/null || true
echo "   ✅ Node.js 和 npm 信息已导出"

# 环境变量（过滤敏感信息）
env | grep -E "PATH|PYTHON|NODE|PM2" | sort > "${BACKUP_DIR}/system_info/environment_vars.txt" 2>/dev/null || true

# 10. 创建部署说明文档
echo "📝 [10/10] 生成部署说明文档..."
cat > "${BACKUP_DIR}/DEPLOYMENT_GUIDE.md" << 'DEPLOY_DOC'
# 交易系统完整部署指南

## 📦 备份内容说明

### 目录结构
```
trading_system_backup_YYYYMMDD_HHMMSS/
├── python_core/              # 主目录所有 Python 文件
├── source_code/              # Python API 源代码
├── panic_paged_v2/           # Panic 系统 v2
├── panic_v3/                 # Panic 系统 v3
├── code/                     # 代码工具目录
├── config/                   # 配置目录
├── monitors/                 # 监控脚本
├── scripts/                  # 工具脚本
├── tests/                    # 测试文件
├── static/                   # 静态资源
├── templates/                # HTML 模板
├── data/                     # 完整数据文件（所有历史数据）
├── config_files/             # 配置和依赖文件
│   ├── package.json
│   ├── requirements.txt
│   ├── ecosystem.config.js
│   ├── pm2_dump.pm2
│   ├── pm2_processes.json
│   └── .env
├── system_info/              # 系统依赖信息
│   ├── pip_freeze.txt
│   ├── apt_packages.txt
│   ├── npm_global_packages.txt
│   ├── node_version.txt
│   └── environment_vars.txt
└── DEPLOYMENT_GUIDE.md       # 本文档
```

---

## 🚀 部署步骤

### 1️⃣ 环境准备

#### 1.1 系统要求
- **操作系统**: Ubuntu 20.04+ / Debian 11+
- **Python**: 3.8+
- **Node.js**: 16.x+
- **内存**: 至少 4GB RAM
- **硬盘**: 至少 10GB 可用空间

#### 1.2 安装基础依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 和工具
sudo apt install -y python3 python3-pip python3-venv git curl wget

# 安装 Node.js 和 npm
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs

# 安装 PM2（全局）
sudo npm install -g pm2

# 验证安装
python3 --version
node --version
npm --version
pm2 --version
```

---

### 2️⃣ 解压和恢复备份

#### 2.1 上传备份文件
```bash
# 将备份文件上传到服务器（示例）
scp trading_system_backup_YYYYMMDD_HHMMSS.tar.gz user@server:/tmp/

# 或使用其他方式（SFTP、云存储等）
```

#### 2.2 解压备份
```bash
# 切换到目标目录
cd /home/user

# 解压备份
tar -xzf /tmp/trading_system_backup_YYYYMMDD_HHMMSS.tar.gz

# 重命名为工作目录
mv trading_system_backup_YYYYMMDD_HHMMSS webapp

# 进入目录
cd webapp
```

#### 2.3 恢复文件结构
```bash
# 将核心 Python 文件复制到主目录
cp python_core/*.py ./

# 确保脚本可执行
chmod +x *.py
find monitors/ -name "*.py" -exec chmod +x {} \;
find scripts/ -name "*.sh" -exec chmod +x {} \;
```

---

### 3️⃣ 安装 Python 依赖

```bash
# 切换到工作目录
cd /home/user/webapp

# 安装 Python 包
pip3 install -r config_files/requirements.txt

# 或使用 pip_freeze.txt（精确版本）
pip3 install -r system_info/pip_freeze.txt

# 常用的额外包（如果缺失）
pip3 install flask requests pandas numpy ccxt python-telegram-bot
```

---

### 4️⃣ 配置环境变量

#### 4.1 创建 .env 文件
```bash
# 复制备份的环境配置
cp config_files/.env ./ 2>/dev/null || true

# 手动编辑 .env 文件
nano .env
```

#### 4.2 必需的环境变量
```bash
# Telegram 配置
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# OKX API 配置（如果需要）
OKX_API_KEY=your_api_key
OKX_API_SECRET=your_api_secret
OKX_PASSPHRASE=your_passphrase

# Flask 配置
FLASK_ENV=production
FLASK_PORT=9002

# 数据库配置（如果使用）
# DATABASE_URL=...
```

---

### 5️⃣ 恢复 PM2 服务

#### 5.1 使用 PM2 配置文件（推荐）
```bash
# 如果有 ecosystem.config.js
pm2 start config_files/ecosystem.config.js

# 或使用 pm2.config.js
pm2 start config_files/pm2.config.js
```

#### 5.2 手动恢复 PM2 进程
```bash
# 查看备份的进程列表
cat config_files/pm2_processes.json

# 启动主应用
pm2 start app.py --name flask-app --interpreter python3

# 启动监控服务（示例）
pm2 start monitors/okx_tpsl_monitor.py --name okx-tpsl-monitor --interpreter python3
pm2 start monitors/okx_percent_tpsl_monitor.py --name okx-percent-tpsl-monitor --interpreter python3
pm2 start okx_confirm_structure_monitor.py --name okx-confirm-structure-monitor --interpreter python3

# 启动采集器（示例）
pm2 start code/python/collectors/signal_collector.py --name signal-collector --interpreter python3
pm2 start code/python/collectors/liquidation_1h_collector.py --name liquidation-1h-collector --interpreter python3

# 查看进程状态
pm2 list
pm2 status

# 保存 PM2 配置
pm2 save

# 设置 PM2 开机自启
pm2 startup
# 按照提示执行命令（需要 sudo）
```

#### 5.3 从备份恢复 PM2 列表
```bash
# 复制 PM2 dump 文件
mkdir -p ~/.pm2
cp config_files/pm2_dump.pm2 ~/.pm2/dump.pm2

# 恢复进程
pm2 resurrect
```

---

### 6️⃣ 验证部署

#### 6.1 检查服务状态
```bash
# 查看 PM2 进程
pm2 list
pm2 status

# 查看日志
pm2 logs flask-app --lines 50
pm2 logs --lines 20

# 检查 Flask 是否运行
curl http://localhost:9002/
curl http://localhost:9002/api/health
```

#### 6.2 检查数据文件
```bash
# 检查数据目录
ls -lh data/
du -sh data/*

# 检查 JSONL 文件数量
find data/ -name "*.jsonl" | wc -l

# 检查最新数据时间
ls -lt data/*/*.jsonl | head -10
```

#### 6.3 测试 API 端点
```bash
# 测试止盈止损配置
curl http://localhost:9002/api/okx-trading/percent-tpsl-status/account_main

# 测试持仓信息
curl -X POST http://localhost:9002/api/okx-trading/positions \
  -H "Content-Type: application/json" \
  -d '{"apiKey":"...","apiSecret":"...","passphrase":"..."}'
```

---

### 7️⃣ 路由和端口配置

#### 7.1 Flask 应用路由
主应用运行在端口 `9002`，主要路由包括：

```python
# 主页
GET /

# OKX 交易界面
GET /okx-trading

# API 端点
POST /api/okx-trading/tpsl-settings/<account_id>
GET  /api/okx-trading/percent-tpsl-status/<account_id>
GET  /api/okx-trading/confirm-structure-alerts/<account_id>
POST /api/okx-trading/positions
POST /api/okx-trading/account-info
...
```

#### 7.2 配置反向代理（可选）
如果需要通过 Nginx 代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:9002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

### 8️⃣ 监控和日志

#### 8.1 PM2 监控
```bash
# 实时监控
pm2 monit

# 查看资源使用
pm2 list

# 查看某个进程的详细信息
pm2 show flask-app
```

#### 8.2 日志管理
```bash
# 查看所有日志
pm2 logs

# 查看特定服务日志
pm2 logs flask-app
pm2 logs okx-tpsl-monitor

# 清理日志
pm2 flush

# 日志文件位置
ls -lh ~/.pm2/logs/
```

#### 8.3 应用日志
```bash
# 应用生成的日志（如果配置了）
ls -lh logs/
tail -f logs/flask_app.log
tail -f logs/monitor_*.log
```

---

## 📋 服务清单和对应关系

### PM2 服务列表

| 服务名称 | 脚本路径 | 说明 | 端口 |
|---------|---------|------|------|
| flask-app | app.py | 主 Flask 应用 | 9002 |
| okx-tpsl-monitor | monitors/okx_tpsl_monitor.py | 固定金额止盈止损监控 | - |
| okx-percent-tpsl-monitor | monitors/okx_percent_tpsl_monitor.py | 百分比止盈止损监控 | - |
| okx-confirm-structure-monitor | okx_confirm_structure_monitor.py | 确认结构监控 | - |
| rsi-takeprofit-monitor | monitors/rsi_takeprofit_monitor.py | RSI 止盈监控 | - |
| signal-collector | code/python/collectors/signal_collector.py | 信号采集 | - |
| liquidation-1h-collector | code/python/collectors/liquidation_1h_collector.py | 1小时清算数据 | - |
| okx-day-change-collector | code/python/collectors/okx_day_change_collector.py | 日涨跌幅采集 | - |
| price-baseline-collector | code/python/collectors/price_baseline_collector.py | 价格基线采集 | - |
| v1v2-collector | code/python/collectors/v1v2_collector.py | V1V2数据采集 | - |
| price-speed-collector | code/python/collectors/price_speed_collector.py | 价格速度采集 | - |
| sar-slope-collector | code/python/collectors/sar_slope_collector.py | SAR斜率采集 | - |
| price-comparison-collector | code/python/collectors/price_comparison_collector.py | 价格对比采集 | - |
| financial-indicators-collector | code/python/collectors/financial_indicators_collector.py | 金融指标采集 | - |
| crypto-index-collector | code/python/collectors/crypto_index_collector.py | 加密货币指数 | - |
| sar-bias-stats-collector | code/python/collectors/sar_bias_stats_collector.py | SAR偏差统计 | - |
| panic-wash-collector | code/python/collectors/panic_wash_collector.py | 恐慌洗盘采集 | - |
| data-health-monitor | code/python/monitors/data_health_monitor.py | 数据健康监控 | - |
| system-health-monitor | code/python/monitors/system_health_monitor.py | 系统健康监控 | - |
| liquidation-alert-monitor | code/python/liquidation_alert_monitor.py | 清算预警监控 | - |
| dashboard-jsonl-manager | code/python/managers/dashboard_jsonl_manager.py | 仪表板JSONL管理 | - |
| gdrive-jsonl-manager | code/python/managers/gdrive_jsonl_manager.py | Google Drive同步 | - |
| okx-trade-history | monitors/okx_trade_history.py | OKX交易历史 | - |
| market-sentiment-collector | code/python/collectors/market_sentiment_collector.py | 市场情绪采集 | - |
| price-position-collector | code/python/collectors/price_position_collector.py | 价格仓位采集 | - |
| bottom-signal-long-monitor | monitors/bottom_signal_long_monitor.py | 见底信号多单监控 | - |
| coin-change-predictor | code/python/coin_change_predictor.py | 币种涨跌预测 | - |
| coin-change-tracker | code/python/coin_change_tracker.py | 币种涨跌追踪 | - |
| new-high-low-collector | code/python/collectors/new_high_low_collector.py | 新高新低采集 | - |
| sar-daily-stats-scheduler | code/python/schedulers/sar_daily_stats_scheduler.py | SAR日统计调度 | - |
| coin-price-tracker | code/python/coin_price_tracker.py | 币价追踪 | - |

### 启动顺序建议
```bash
# 1. 主应用（优先）
pm2 start app.py --name flask-app --interpreter python3

# 2. 核心监控服务
pm2 start monitors/okx_tpsl_monitor.py --name okx-tpsl-monitor --interpreter python3
pm2 start monitors/okx_percent_tpsl_monitor.py --name okx-percent-tpsl-monitor --interpreter python3
pm2 start okx_confirm_structure_monitor.py --name okx-confirm-structure-monitor --interpreter python3

# 3. 数据采集服务
pm2 start code/python/collectors/signal_collector.py --name signal-collector --interpreter python3
pm2 start code/python/collectors/liquidation_1h_collector.py --name liquidation-1h-collector --interpreter python3

# 4. 其他服务
# ... 根据需要启动
```

---

## 🔧 常见问题

### Q1: 端口被占用
```bash
# 查找占用端口的进程
lsof -i :9002
netstat -tulpn | grep 9002

# 杀死进程
kill -9 <PID>
```

### Q2: PM2 服务无法启动
```bash
# 查看错误日志
pm2 logs <service-name> --err --lines 50

# 删除并重新创建
pm2 delete <service-name>
pm2 start <script-path> --name <service-name> --interpreter python3
```

### Q3: 数据文件损坏
```bash
# 检查 JSONL 文件格式
cat data/some_file.jsonl | jq . > /dev/null

# 如果格式错误，清理最后一行
sed -i '$ d' data/some_file.jsonl
```

### Q4: Python 依赖缺失
```bash
# 重新安装所有依赖
pip3 install -r config_files/requirements.txt --force-reinstall

# 安装缺失的特定包
pip3 install <package-name>
```

---

## 📊 数据文件说明

### 数据目录结构
```
data/
├── okx_tpsl_settings/          # 止盈止损配置
│   ├── account_main_percent_tpsl.jsonl
│   ├── account_main_tpsl.jsonl
│   ├── account_main_confirm_structure_alerts.jsonl
│   └── ...
├── daily_predictions/          # 每日预测
│   ├── prediction_20260228.jsonl
│   └── ...
├── market_sentiment/           # 市场情绪
│   ├── market_sentiment_20260228.jsonl
│   └── ...
├── signals/                    # 交易信号
│   ├── signals_20260228.jsonl
│   └── ...
├── liquidation_1h/             # 清算数据
│   ├── liquidation_1h_20260228.jsonl
│   └── ...
└── ... (其他数据目录)
```

### 数据保留策略
- **完整备份**: 包含所有历史数据
- **建议清理周期**: 根据存储空间，可保留最近 30-90 天数据
- **重要数据**: 配置文件、执行记录永久保留

---

## 🔐 安全建议

1. **环境变量保护**: 不要将 `.env` 文件提交到版本控制
2. **API 密钥安全**: 使用环境变量或加密存储
3. **防火墙配置**: 限制外部访问端口
4. **定期备份**: 建议每周自动备份一次
5. **日志审计**: 定期检查异常日志

---

## 📞 技术支持

- **文档更新**: 2026-02-28
- **备份版本**: YYYYMMDD_HHMMSS
- **系统版本**: 查看 `config_files/requirements.txt`

---

## ✅ 部署验证清单

- [ ] Python 3.8+ 已安装
- [ ] Node.js 16+ 已安装
- [ ] PM2 全局安装
- [ ] 所有 Python 依赖已安装
- [ ] 环境变量已配置
- [ ] Flask 应用运行正常（端口 9002）
- [ ] PM2 服务全部 online
- [ ] 数据文件完整
- [ ] API 端点测试通过
- [ ] 日志正常输出

---

**🎉 部署完成后，系统应该可以正常运行！**

DEPLOY_DOC

echo "   ✅ 部署说明文档已生成"

# 创建备份清单
cat > "${BACKUP_DIR}/BACKUP_MANIFEST.txt" << MANIFEST
========================================
交易系统完整备份清单
========================================
备份时间: ${TIMESTAMP}
源目录: ${SOURCE_DIR}
备份目录: ${BACKUP_DIR}

========================================
目录统计
========================================
MANIFEST

# 统计各目录大小和文件数
for dir in python_core source_code panic_paged_v2 panic_v3 code config monitors scripts tests static templates data config_files system_info; do
    if [ -d "${BACKUP_DIR}/${dir}" ]; then
        SIZE=$(du -sh "${BACKUP_DIR}/${dir}" 2>/dev/null | awk '{print $1}')
        COUNT=$(find "${BACKUP_DIR}/${dir}" -type f 2>/dev/null | wc -l)
        echo "✅ ${dir}/: ${SIZE}, ${COUNT} 个文件" >> "${BACKUP_DIR}/BACKUP_MANIFEST.txt"
    fi
done

cat >> "${BACKUP_DIR}/BACKUP_MANIFEST.txt" << MANIFEST

========================================
Python 文件统计
========================================
MANIFEST

find "${BACKUP_DIR}" -name "*.py" | wc -l >> "${BACKUP_DIR}/BACKUP_MANIFEST.txt"
echo " 个 Python 文件" >> "${BACKUP_DIR}/BACKUP_MANIFEST.txt"

cat >> "${BACKUP_DIR}/BACKUP_MANIFEST.txt" << MANIFEST

========================================
数据文件统计
========================================
MANIFEST

if [ -d "${BACKUP_DIR}/data" ]; then
    find "${BACKUP_DIR}/data" -name "*.jsonl" | wc -l >> "${BACKUP_DIR}/BACKUP_MANIFEST.txt"
    echo " 个 JSONL 数据文件" >> "${BACKUP_DIR}/BACKUP_MANIFEST.txt"
fi

cat >> "${BACKUP_DIR}/BACKUP_MANIFEST.txt" << MANIFEST

========================================
配置文件清单
========================================
MANIFEST

ls -lh "${BACKUP_DIR}/config_files/" >> "${BACKUP_DIR}/BACKUP_MANIFEST.txt" 2>/dev/null || true

cat >> "${BACKUP_DIR}/BACKUP_MANIFEST.txt" << MANIFEST

========================================
系统依赖清单
========================================
MANIFEST

ls -lh "${BACKUP_DIR}/system_info/" >> "${BACKUP_DIR}/BACKUP_MANIFEST.txt" 2>/dev/null || true

echo ""
echo "============================================================"
echo "📦 [压缩] 开始打包备份文件..."
echo "============================================================"

# 压缩备份目录
cd /tmp
tar -czf "${BACKUP_FILE}" "${BACKUP_NAME}"

# 计算压缩后大小
BACKUP_SIZE=$(du -sh "${BACKUP_FILE}" | awk '{print $1}')
echo ""
echo "============================================================"
echo "✅ 备份完成！"
echo "============================================================"
echo "📦 备份文件: ${BACKUP_FILE}"
echo "💾 文件大小: ${BACKUP_SIZE}"
echo "📁 包含内容:"
echo "   - Python 代码（主目录 + source_code + panic系统）"
echo "   - 配置文件（package.json, requirements.txt, .env等）"
echo "   - PM2 配置和进程列表"
echo "   - 系统依赖信息"
echo "   - 完整数据文件（所有历史数据）"
echo "   - 部署说明文档"
echo "   - 备份清单"
echo ""
echo "🔧 解压命令:"
echo "   tar -xzf ${BACKUP_FILE}"
echo ""
echo "📖 部署说明:"
echo "   解压后查看 DEPLOYMENT_GUIDE.md"
echo "============================================================"

# 清理临时目录
rm -rf "${BACKUP_DIR}"

# 显示备份清单
echo ""
echo "📋 备份清单预览:"
head -50 "/tmp/${BACKUP_NAME}/BACKUP_MANIFEST.txt" 2>/dev/null || cat "${BACKUP_FILE%.tar.gz}/BACKUP_MANIFEST.txt" 2>/dev/null || echo "（清单文件已打包）"

echo ""
echo "🎉 备份流程全部完成！"
