# 完整项目部署恢复指南

## 📋 目录

1. [系统要求](#系统要求)
2. [快速开始](#快速开始)
3. [详细恢复步骤](#详细恢复步骤)
4. [目录结构说明](#目录结构说明)
5. [依赖安装](#依赖安装)
6. [配置文件](#配置文件)
7. [数据恢复](#数据恢复)
8. [服务启动](#服务启动)
9. [验证测试](#验证测试)
10. [常见问题](#常见问题)

---

## 系统要求

### 操作系统
- **推荐**: Ubuntu 20.04 LTS 或更高版本
- **最低**: Ubuntu 18.04 LTS
- **支持**: Debian 10+, CentOS 8+

### 硬件要求
- **CPU**: 2核心以上
- **内存**: 4GB以上（推荐8GB）
- **磁盘**: 至少10GB可用空间
- **网络**: 稳定的互联网连接

### 必需软件

#### 1. Python 3.8+
```bash
python3 --version  # 应显示 3.8 或更高
```

#### 2. Node.js 14+
```bash
node --version  # 应显示 v14 或更高
```

#### 3. PM2（进程管理器）
```bash
pm2 --version  # 应显示版本号
```

#### 4. Git
```bash
git --version  # 应显示版本号
```

---

## 快速开始

### 1. 解压备份
```bash
cd /tmp
tar -xzf webapp_complete_backup_YYYYMMDD_HHMMSS.tar.gz
cd webapp_complete_backup_YYYYMMDD_HHMMSS
```

### 2. 查看备份信息
```bash
cat BACKUP_INFO.txt
```

### 3. 运行恢复脚本
```bash
bash restore_project.sh
```

### 4. 启动服务
```bash
cd /home/user/webapp
pm2 start ecosystem.config.js
pm2 save
```

---

## 详细恢复步骤

### 步骤1: 准备系统环境

#### 1.1 更新系统
```bash
sudo apt update
sudo apt upgrade -y
```

#### 1.2 安装基础依赖
```bash
# 安装Python和pip
sudo apt install -y python3 python3-pip python3-venv

# 安装Node.js和npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装PM2
sudo npm install -g pm2

# 安装其他工具
sudo apt install -y git curl wget build-essential
```

### 步骤2: 创建项目目录

```bash
# 创建用户（如果不存在）
sudo useradd -m -s /bin/bash user

# 创建项目目录
sudo mkdir -p /home/user/webapp
sudo chown -R user:user /home/user/webapp

# 切换到项目目录
cd /home/user/webapp
```

### 步骤3: 解压并恢复文件

```bash
# 解压备份
cd /tmp
tar -xzf webapp_complete_backup_YYYYMMDD_HHMMSS.tar.gz
cd webapp_complete_backup_YYYYMMDD_HHMMSS

# 复制所有文件到项目目录
cp -r * /home/user/webapp/
cp -r .[!.]* /home/user/webapp/ 2>/dev/null || true

# 设置权限
sudo chown -R user:user /home/user/webapp
```

### 步骤4: 安装Python依赖

```bash
cd /home/user/webapp

# 创建虚拟环境（可选但推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 常用依赖列表（如果requirements.txt缺失）
pip install flask flask-cors requests pandas numpy pytz \
            schedule sqlalchemy psycopg2-binary pymongo redis \
            python-dotenv cryptography pyjwt bcrypt
```

### 步骤5: 安装Node.js依赖（如果需要）

```bash
cd /home/user/webapp

# 如果有package.json
if [ -f "package.json" ]; then
    npm install
fi
```

### 步骤6: 配置文件设置

#### 6.1 Telegram配置
```bash
cd /home/user/webapp/config/configs

# 编辑telegram_config.json
nano telegram_config.json

# 内容格式：
{
  "bot_token": "YOUR_BOT_TOKEN",
  "chat_id": "YOUR_CHAT_ID"
}
```

#### 6.2 OKX配置
```bash
# 编辑okx_config.json（如果使用OKX交易）
nano okx_config.json

# 内容格式：
{
  "api_key": "YOUR_API_KEY",
  "secret_key": "YOUR_SECRET_KEY",
  "passphrase": "YOUR_PASSPHRASE"
}
```

#### 6.3 数据库配置（如果使用）
```bash
# 编辑database_config.json
nano database_config.json
```

### 步骤7: 恢复PM2配置

```bash
cd /home/user/webapp

# 方法1: 使用ecosystem.config.js
pm2 start ecosystem.config.js

# 方法2: 从dump文件恢复
if [ -f "pm2_config/dump.pm2" ]; then
    cp pm2_config/dump.pm2 ~/.pm2/
    pm2 resurrect
fi

# 保存PM2配置
pm2 save

# 设置PM2开机自启
pm2 startup
# 执行命令输出的指令（需要sudo）
```

### 步骤8: 启动Flask应用

```bash
cd /home/user/webapp

# 方法1: 使用PM2启动
pm2 start app.py --name flask-app --interpreter python3

# 方法2: 直接运行（测试用）
python3 app.py

# 检查运行状态
pm2 status
pm2 logs flask-app --lines 50
```

### 步骤9: 启动所有采集器和监控器

```bash
cd /home/user/webapp

# 启动所有服务
pm2 start ecosystem.config.js

# 查看所有进程
pm2 list

# 常见进程列表：
# - flask-app (主应用)
# - signal-collector (信号采集)
# - liquidation-1h-collector (爆仓数据)
# - panic-wash-collector (恐慌清洗指数)
# - price-speed-collector (价格速度)
# - coin-change-tracker (币种变化跟踪)
# - bottom-signal-long-monitor (底部信号监控)
# 等...
```

---

## 目录结构说明

### 核心文件

```
/home/user/webapp/
├── app.py                          # 主Flask应用
├── requirements.txt                # Python依赖
├── package.json                    # Node.js依赖
├── ecosystem.config.js             # PM2配置
│
├── source_code/                    # 核心API代码 (700KB)
│   ├── wave_peak_detector.py      # 波峰检测器
│   ├── bottom_signal_detector.py  # 底部信号检测
│   └── ...
│
├── panic_paged_v2/                 # 爆仓分页系统v2 (140KB)
├── panic_v3/                       # 爆仓系统v3 (168KB)
├── code/                           # 通用代码库 (956KB)
│   └── source_code/               # 子代码目录
│
├── monitors/                       # 监控脚本 (180KB)
│   ├── intraday_pattern_realtime_monitor.py
│   └── ...
│
├── scripts/                        # 工具脚本 (244KB)
│   ├── system_health_check.py
│   ├── analyze_february_predictions.py
│   └── ...
│
├── config/                         # 配置文件 (172KB)
│   ├── configs/
│   │   ├── telegram_config.json   # Telegram配置
│   │   └── okx_config.json        # OKX配置
│   └── ...
│
├── templates/                      # HTML模板 (7.3MB)
│   ├── index.html
│   ├── coin_change_tracker.html
│   ├── liquidation_monthly.html
│   └── ...
│
├── static/                         # 静态资源 (384KB)
│   ├── css/
│   ├── js/
│   └── images/
│
├── docs/                           # 文档 (8.1MB)
│   ├── crash_warning_fix_report.md
│   ├── liquidation_telegram_notification.md
│   └── ...
│
├── data/                           # 数据文件 (~3GB)
│   ├── coin_change_tracker/       # 币种变化跟踪数据
│   ├── daily_predictions/         # 每日预测数据
│   ├── panic_daily/               # 爆仓每日数据
│   ├── okx_trading_history/       # OKX交易历史
│   ├── crash_warning_events/      # 暴跌预警事件
│   └── ...
│
└── tests/                          # 测试文件
    └── ...
```

### 数据目录详细说明

```
data/
├── coin_change_tracker/           # 币种涨跌变化数据
│   ├── coin_change_YYYYMMDD.jsonl # 按日期分区的JSONL文件
│   └── baseline_YYYYMMDD.json     # 基准数据
│
├── daily_predictions/             # 每日预测结果
│   └── prediction_YYYY-MM-DD.json
│
├── panic_daily/                   # 爆仓恐慌指数（按日期）
│   └── panic_YYYYMMDD.jsonl
│
├── okx_trading_history/           # OKX交易记录
│   └── okx_trades_YYYYMMDD.jsonl
│
├── crash_warning_events/          # 暴跌预警事件
│   └── february_analysis.json
│
├── crash_warning_notifications/   # 通知记录
│   └── telegram_sent_YYYYMMDD.json
│
├── daily_crash_warnings/          # 每日暴跌预警
│   └── crash_warning_YYYYMMDD.json
│
└── ...（其他数据目录）
```

---

## 依赖安装

### Python依赖

核心依赖包：

```txt
Flask==2.3.0
Flask-CORS==4.0.0
requests==2.31.0
pandas==2.0.3
numpy==1.24.3
pytz==2023.3
schedule==1.2.0
python-dotenv==1.0.0
```

安装命令：
```bash
pip install -r requirements.txt
```

### Node.js依赖（如果使用）

```bash
npm install
```

### 系统依赖

```bash
# Ubuntu/Debian
sudo apt install -y python3-dev build-essential

# 如果使用数据库
sudo apt install -y postgresql-client libpq-dev  # PostgreSQL
sudo apt install -y mysql-client libmysqlclient-dev  # MySQL
```

---

## 配置文件

### 必须配置的文件

#### 1. Telegram配置 (必需)
路径: `config/configs/telegram_config.json`

```json
{
  "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
  "chat_id": "-1001234567890"
}
```

获取方法：
1. 向 @BotFather 申请Bot Token
2. 向 @userinfobot 查询Chat ID

#### 2. OKX配置 (如果使用OKX交易)
路径: `config/configs/okx_config.json`

```json
{
  "accounts": {
    "main": {
      "api_key": "your-api-key",
      "secret_key": "your-secret-key",
      "passphrase": "your-passphrase"
    }
  }
}
```

### 可选配置

#### 3. Flask配置
路径: `config/flask_config.py`

```python
class Config:
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = 9002
    SECRET_KEY = 'your-secret-key'
```

---

## 数据恢复

### 数据完整性检查

```bash
cd /home/user/webapp

# 检查数据目录大小
du -sh data/

# 检查JSONL文件数量
find data -name "*.jsonl" | wc -l

# 检查JSON文件数量
find data -name "*.json" | wc -l

# 查看最新数据文件
ls -lt data/coin_change_tracker/ | head -10
```

### 数据迁移注意事项

1. **保持路径一致**: 数据路径必须是 `/home/user/webapp/data/`
2. **权限设置**: 确保数据文件可读写
3. **格式验证**: 确认JSONL文件格式正确

```bash
# 设置数据目录权限
chmod -R 755 /home/user/webapp/data
chown -R user:user /home/user/webapp/data

# 验证JSONL格式
head -1 data/coin_change_tracker/coin_change_20260226.jsonl | python3 -m json.tool
```

---

## 服务启动

### PM2 启动方式

#### 方法1: 使用 ecosystem.config.js
```bash
cd /home/user/webapp
pm2 start ecosystem.config.js
pm2 save
```

#### 方法2: 单独启动Flask
```bash
pm2 start app.py --name flask-app --interpreter python3 \
    --watch --ignore-watch="data logs" \
    --max-memory-restart 1G
```

#### 方法3: 手动启动所有服务
```bash
# Flask主应用
pm2 start app.py --name flask-app --interpreter python3

# 信号采集器
pm2 start signal_collector.py --name signal-collector --interpreter python3

# 爆仓数据采集
pm2 start liquidation_1h_collector.py --name liquidation-1h-collector --interpreter python3

# 恐慌指数采集
pm2 start panic_wash_collector.py --name panic-wash-collector --interpreter python3

# ... 更多服务
```

### PM2 常用命令

```bash
# 查看所有进程
pm2 list

# 查看详细信息
pm2 show flask-app

# 查看日志
pm2 logs flask-app --lines 100

# 重启服务
pm2 restart flask-app

# 停止服务
pm2 stop flask-app

# 删除服务
pm2 delete flask-app

# 保存配置
pm2 save

# 清空日志
pm2 flush
```

### 开机自启动

```bash
# 生成启动脚本
pm2 startup

# 执行输出的命令（需要sudo）
# 例如：sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u user --hp /home/user

# 保存当前进程列表
pm2 save
```

---

## 验证测试

### 1. 检查Flask应用

```bash
# 检查端口监听
netstat -tlnp | grep 9002

# 或使用ss
ss -tlnp | grep 9002

# 测试API
curl http://localhost:9002/

# 测试具体API
curl http://localhost:9002/api/coin-change-tracker/wave-peaks?date=2026-02-26
```

### 2. 检查PM2进程

```bash
# 查看所有进程状态
pm2 list

# 检查是否有错误进程
pm2 list | grep error

# 查看内存使用
pm2 monit
```

### 3. 检查数据采集

```bash
# 查看最新数据文件
ls -lt /home/user/webapp/data/coin_change_tracker/ | head -5

# 检查文件更新时间
stat /home/user/webapp/data/coin_change_tracker/coin_change_$(date +%Y%m%d).jsonl

# 查看日志
pm2 logs signal-collector --lines 20
```

### 4. 访问Web界面

```bash
# 获取服务URL（如果在sandbox）
# 或直接访问
firefox http://localhost:9002/
```

主要页面：
- 首页: `http://localhost:9002/`
- 币种变化跟踪: `http://localhost:9002/coin-change-tracker`
- 爆仓月线图: `http://localhost:9002/liquidation-monthly`
- OKX交易标记: `http://localhost:9002/okx-trading-marks`

### 5. 测试Telegram通知

```bash
# 测试暴跌预警通知
curl -X GET "http://localhost:9002/api/coin-change-tracker/wave-peaks?date=2026-02-26"

# 测试爆仓趋势通知
curl -X POST "http://localhost:9002/api/liquidation/mark-notify" \
  -H "Content-Type: application/json" \
  -d '{"mark_type": "long", "time": "2026-02-06T08:57:00+08:00", "amount": 15000}'
```

---

## 常见问题

### Q1: 端口被占用

**错误**: `Address already in use`

**解决**:
```bash
# 查看占用端口的进程
sudo lsof -i :9002

# 或使用
sudo netstat -tlnp | grep 9002

# 杀死进程
sudo kill -9 [PID]

# 修改Flask端口（在app.py中）
app.run(host='0.0.0.0', port=9003)
```

### Q2: Python模块找不到

**错误**: `ModuleNotFoundError: No module named 'xxx'`

**解决**:
```bash
# 确认Python版本
python3 --version

# 重新安装依赖
pip install -r requirements.txt

# 或单独安装
pip install flask requests pandas
```

### Q3: PM2启动失败

**错误**: `Error: Script not found`

**解决**:
```bash
# 检查文件是否存在
ls -l app.py

# 检查文件权限
chmod +x app.py

# 使用绝对路径
pm2 start /home/user/webapp/app.py --name flask-app --interpreter python3
```

### Q4: 数据文件权限问题

**错误**: `Permission denied`

**解决**:
```bash
# 修改数据目录权限
sudo chown -R user:user /home/user/webapp/data
chmod -R 755 /home/user/webapp/data

# 检查SELinux（如果使用）
sudo setenforce 0  # 临时禁用
```

### Q5: Telegram通知发送失败

**错误**: `Telegram配置不完整`

**解决**:
```bash
# 检查配置文件
cat /home/user/webapp/config/configs/telegram_config.json

# 测试Bot Token
curl "https://api.telegram.org/bot[YOUR_BOT_TOKEN]/getMe"

# 测试发送消息
curl -X POST "https://api.telegram.org/bot[YOUR_BOT_TOKEN]/sendMessage" \
  -d "chat_id=[YOUR_CHAT_ID]&text=Test"
```

### Q6: PM2进程自动重启

**原因**: 内存超限或错误退出

**解决**:
```bash
# 查看错误日志
pm2 logs flask-app --err --lines 100

# 增加内存限制
pm2 start app.py --name flask-app --max-memory-restart 2G

# 禁用自动重启（仅测试用）
pm2 start app.py --name flask-app --no-autorestart
```

### Q7: 数据库连接失败（如果使用）

**解决**:
```bash
# 检查数据库服务
sudo systemctl status postgresql
sudo systemctl status mysql

# 启动数据库
sudo systemctl start postgresql

# 测试连接
psql -h localhost -U username -d database_name
```

---

## 附录

### A. 完整的ecosystem.config.js示例

```javascript
module.exports = {
  apps: [
    {
      name: 'flask-app',
      script: 'app.py',
      interpreter: 'python3',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        PORT: 9002
      }
    },
    {
      name: 'signal-collector',
      script: 'signal_collector.py',
      interpreter: 'python3',
      instances: 1,
      autorestart: true,
      cron_restart: '0 */1 * * *'  // 每小时重启一次
    }
    // ... 更多服务配置
  ]
};
```

### B. 快速恢复检查清单

- [ ] 系统环境准备完成（Python、Node.js、PM2）
- [ ] 备份文件已解压到正确位置
- [ ] Python依赖已安装
- [ ] 配置文件已正确设置（Telegram等）
- [ ] 数据目录权限正确
- [ ] PM2服务已启动
- [ ] Flask应用运行正常（端口9002可访问）
- [ ] 数据采集器正常运行
- [ ] Web界面可以访问
- [ ] Telegram通知测试成功
- [ ] PM2开机自启已设置

### C. 性能优化建议

1. **使用Redis缓存**:
```bash
sudo apt install redis-server
pip install redis
```

2. **使用Nginx反向代理**:
```bash
sudo apt install nginx
# 配置 /etc/nginx/sites-available/webapp
```

3. **数据库索引优化**（如果使用数据库）

4. **日志轮转**:
```bash
# 配置logrotate
sudo nano /etc/logrotate.d/webapp
```

---

## 技术支持

### 获取帮助

1. 查看文档: `docs/` 目录
2. 查看日志: `pm2 logs`
3. 检查系统状态: `bash scripts/system_health_check.py`

### 联系方式

- 项目仓库: https://github.com/jamesyidc/1212335551
- 问题反馈: 提交Issue到GitHub仓库

---

**文档版本**: 1.0  
**更新时间**: 2026-02-27  
**适用备份**: webapp_complete_backup_*  
**维护者**: Genspark AI Developer
