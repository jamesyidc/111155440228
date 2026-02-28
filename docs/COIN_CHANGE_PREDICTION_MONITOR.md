# 币种涨跌预判监控器说明文档

## 📋 功能概述

自动监控每天0点至2点的币种走势，基于10分钟上涨占比分析，预判全天行情并发送Telegram预警消息。

## 🎯 分析规则

### 柱状图颜色定义
- 🟢 **绿色**: 上涨占比 > 55%
- 🔴 **红色**: 上涨占比 < 45%
- 🟡 **黄色**: 45% ≤ 上涨占比 ≤ 55%

### 四种市场情况

#### 情况1: 低吸机会 🟢🔴
- **条件**: 有绿色柱子 + 有红色柱子 + 无黄色柱子
- **预判**: 红色区间为低吸机会
- **操作**: TG消息 "低吸"

#### 情况2: 等待新低 🟢🔴🟡
- **条件**: 有绿色柱子 + 有红色柱子 + 有黄色柱子
- **预判**: 可能还有新低
- **操作**: TG消息 "等待新低"

#### 情况3: 做空信号 🔴
- **条件**: 只有红色柱子（无绿无黄）
- **预判**: 下跌的一天
- **操作**: 2点发TG消息 "做空"

#### 情况4: 诱多不参与 🟢
- **条件**: 全部绿色柱子（无红无黄）
- **预判**: 单边诱多行情
- **操作**: TG消息 "诱多不参与"

## 🕐 运行时间

- **监控时段**: 每天 00:00 - 02:00
- **分析频率**: 每10分钟分析一次
- **消息发送**: 实时发送预警消息

## 📁 文件位置

```
/home/user/webapp/
├── monitors/
│   └── coin_change_prediction_monitor.py    # 主监控程序
├── test_coin_change_prediction.py            # 测试脚本
└── telegram_notification_config.json         # TG配置
```

## 🚀 启动方法

### 方法1: PM2启动（推荐）

```bash
# 添加到PM2配置
cd /home/user/webapp

# 编辑ecosystem.config.js，添加:
{
  name: 'coin-change-predictor',
  script: '/home/user/webapp/monitors/coin_change_prediction_monitor.py',
  interpreter: 'python3',
  cwd: '/home/user/webapp',
  autorestart: true,
  watch: false,
  max_memory_restart: '200M'
}

# 启动
pm2 start ecosystem.config.js --only coin-change-predictor
pm2 save

# 查看状态
pm2 status coin-change-predictor

# 查看日志
pm2 logs coin-change-predictor --lines 50
```

### 方法2: Supervisor启动

```bash
# 创建配置文件
sudo vim /etc/supervisor/conf.d/coin_change_predictor.conf

# 添加内容:
[program:coin_change_predictor]
command=/usr/bin/python3 /home/user/webapp/monitors/coin_change_prediction_monitor.py
directory=/home/user/webapp
user=user
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/user/webapp/logs/coin_change_predictor.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3

# 启动
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start coin_change_predictor
```

### 方法3: 直接运行（调试用）

```bash
cd /home/user/webapp
python3 monitors/coin_change_prediction_monitor.py
```

## 🧪 测试方法

### 手动测试（不受时间限制）

```bash
cd /home/user/webapp
python3 test_coin_change_prediction.py
```

测试脚本功能:
- ✅ 获取最新币种数据
- ✅ 分析柱状图颜色分布
- ✅ 判断市场信号
- ✅ 显示前10个币种详情
- ✅ 可选发送测试TG消息

### 验证运行状态

```bash
# PM2状态
pm2 status coin-change-predictor

# 查看日志
pm2 logs coin-change-predictor

# 或Supervisor
sudo supervisorctl status coin_change_predictor
sudo supervisorctl tail -f coin_change_predictor
```

## 📊 消息示例

```
🔔 币种走势预判 - 2026-02-22 01:30

📊 柱状图颜色统计 (0-2点):
🟢 绿色: 45个 (上涨占比 > 55%)
🔴 红色: 28个 (上涨占比 < 45%)
🟡 黄色: 12个 (45% ≤ 占比 ≤ 55%)

🎯 预判信号: 等待新低
🟢🔴🟡 有绿有红有黄，可能还有新低，建议等待

📖 分析规则:
• 情况1: 有绿+有红+无黄 → 低吸机会
• 情况2: 有绿+有红+有黄 → 等待新低
• 情况3: 只有红色 → 做空信号
• 情况4: 全部绿色 → 诱多不参与

⏰ 分析时段: 0:00 - 2:00
📈 数据来源: 10分钟上涨占比
```

## 🔧 配置说明

### Telegram配置

编辑 `telegram_notification_config.json`:

```json
{
  "enabled": true,
  "bot_token": "YOUR_BOT_TOKEN",
  "chat_id": "YOUR_CHAT_ID"
}
```

### 数据API

- **URL**: https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai/api/coin-change-tracker/latest
- **方法**: GET
- **返回**: JSON格式的币种涨跌数据

## 📝 日志说明

### 日志级别
- ✅ **成功**: 分析完成、消息发送成功
- ⚠️ **警告**: 配置未设置、不在分析时段
- ❌ **错误**: 数据获取失败、消息发送失败

### 日志示例

```
🚀 币种涨跌预判监控器启动
⏰ 监控时段: 每天 0:00 - 2:00
📊 分析指标: 10分钟上涨占比

⏳ 下次分析时间: 2026-02-23 00:00
💤 等待 16.5 小时...

⏰ 进入分析时段: 00:05:23
============================================================
🔍 币种涨跌预判分析 - 2026-02-23 00:05:23
============================================================

📊 柱状图颜色统计:
  🟢 绿色柱子: 42个 (上涨占比 > 55%)
  🔴 红色柱子: 30个 (上涨占比 < 45%)
  🟡 黄色柱子: 8个 (45% ≤ 上涨占比 ≤ 55%)

🎯 市场信号: 等待新低
📝 说明: 🟢🔴🟡 有绿有红有黄，可能还有新低，建议等待

✅ Telegram消息发送成功

✅ 分析完成
```

## 🐛 故障排查

### 问题1: 消息未发送

**检查步骤**:
```bash
# 1. 验证TG配置
cat /home/user/webapp/telegram_notification_config.json

# 2. 手动测试TG连接
python3 test_coin_change_prediction.py

# 3. 检查网络连接
curl -I https://api.telegram.org
```

### 问题2: 数据获取失败

**检查步骤**:
```bash
# 1. 测试API可达性
curl https://9002-iopxcqas7abbrajoi4k4x-2e77fc33.sandbox.novita.ai/api/coin-change-tracker/latest

# 2. 检查防火墙
sudo ufw status
```

### 问题3: 进程异常退出

**检查步骤**:
```bash
# PM2
pm2 logs coin-change-predictor --err --lines 100

# Supervisor
sudo supervisorctl tail coin_change_predictor stderr

# 手动运行查看错误
python3 /home/user/webapp/monitors/coin_change_prediction_monitor.py
```

## 📈 性能优化

### 资源占用
- **CPU**: < 1%（待机时）
- **内存**: ~50MB
- **网络**: 每10分钟约10KB

### 优化建议
1. 使用PM2或Supervisor保证自动重启
2. 日志文件定期清理（建议保留7天）
3. 监控进程健康状态

## 🔄 更新和维护

### 更新代码

```bash
cd /home/user/webapp
# 编辑监控器
vim monitors/coin_change_prediction_monitor.py

# 重启服务
pm2 restart coin-change-predictor
# 或
sudo supervisorctl restart coin_change_predictor
```

### 备份配置

```bash
# 备份TG配置
cp telegram_notification_config.json telegram_notification_config.json.bak

# 备份监控器
cp monitors/coin_change_prediction_monitor.py monitors/coin_change_prediction_monitor.py.bak
```

## 📞 技术支持

- **监控器版本**: v1.0
- **创建日期**: 2026-02-22
- **Python版本**: 3.8+
- **依赖**: requests, json, datetime

## 🎯 下一步改进

1. [ ] 添加历史分析数据存储
2. [ ] 增加胜率统计功能
3. [ ] 支持多时段分析（如4-6点、8-10点）
4. [ ] 添加Web界面实时监控
5. [ ] 支持自定义阈值配置

---

**最后更新**: 2026-02-22  
**作者**: OKX Trading System Team
