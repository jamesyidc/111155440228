# 暴跌预警Telegram自动通知配置说明

## 📋 功能概述

系统检测到暴跌预警时，会自动发送Telegram消息，提醒**立即平掉所有多头持仓**。

## 🚨 预警规则

检测A点RSI总和连续递减模式：
- **模式1**：A1 > A2 > A3（连续3个A点递减）
- **模式2**：A2 > A3 > A4（后3个A点递减）

## 📱 Telegram消息内容

当检测到暴跌预警时，会发送包含以下信息的消息：

```
🚨🚨🚨 【紧急】暴跌风险预警 🚨🚨🚨

⏰ 检测时间: 2026-02-06 22:40:44
📅 监控日期: 2026-02-06
🔔 预警数量: 3 个

========================================

预警 1: A点递减_3波
📍 波峰: 1-2-3
⚠️ 信号: 即将暴跌
💡 操作: 逢高做空

📊 A点数据:
  • A1: 39.19 @ 2026-02-06 00:30:07
  • A2: -8.74 @ 2026-02-06 01:41:00
  • A3: -31.18 @ 2026-02-06 02:59:00

📉 递减对比:
  ✅ A2_vs_A1: -8.74 vs 39.19 (降幅: 122.30%)
  ✅ A3_vs_A2: -31.18 vs -8.74 (降幅: 256.75%)

========================================

🔴🔴🔴 【紧急操作建议】 🔴🔴🔴

⚠️ 立即平掉所有多头持仓！
⚠️ 市场即将暴跌，风险极高！
⚠️ 建议逢高做空或观望！

📌 操作提示：
  1. 检查所有多头仓位
  2. 立即平仓止损
  3. 等待市场稳定后再入场
  4. 可考虑逢高做空
```

## 🔧 配置方式

### 方法1：手动运行（测试用）

```bash
cd /home/user/webapp
python3 scripts/daily_crash_warning_monitor.py
```

### 方法2：定时任务（推荐）

使用cron每5分钟检查一次：

```bash
# 编辑crontab
crontab -e

# 添加以下行（每5分钟运行一次）
*/5 * * * * cd /home/user/webapp && python3 scripts/daily_crash_warning_monitor.py >> logs/crash-warning-monitor.log 2>&1
```

### 方法3：PM2定时任务

添加到PM2配置文件 `ecosystem.config.js`：

```javascript
{
  name: 'crash-warning-monitor',
  script: 'scripts/daily_crash_warning_monitor.py',
  interpreter: 'python3',
  cwd: '/home/user/webapp',
  cron_restart: '*/5 * * * *',  // 每5分钟运行
  autorestart: false,
  watch: false,
  max_memory_restart: '200M',
  error_file: '/home/user/webapp/logs/crash-warning-error.log',
  out_file: '/home/user/webapp/logs/crash-warning-out.log'
}
```

然后重启PM2：

```bash
pm2 reload ecosystem.config.js
pm2 save
```

## 🔑 Telegram配置

**Bot Token**: `8437045462:AAFePnwdC21cqeWhZISMQHGGgjmroVqE2H0`  
**Chat ID**: `-1003227444260`

配置位置：`scripts/daily_crash_warning_monitor.py` 第24-25行

## 📂 数据文件

### 输入数据
- 波峰数据：`data/coin_change_tracker/wave_peaks/wave_peaks_YYYYMMDD.json`

### 输出数据
- 预警记录：`data/daily_crash_warnings/crash_warning_YYYYMMDD.json`

### 日志文件
- PM2日志：`logs/crash-warning-monitor.log`
- 错误日志：`logs/crash-warning-error.log`
- 输出日志：`logs/crash-warning-out.log`

## ✅ 测试

使用历史数据测试（2026-02-06有暴跌预警）：

```bash
cd /home/user/webapp
python3 scripts/daily_crash_warning_monitor.py 20260206
```

预期输出：
- ✅ 检测到3个暴跌预警
- ✅ Telegram消息发送成功
- ✅ 预警信息已保存

## 📊 监控状态

查看PM2进程状态：

```bash
pm2 list | grep crash
pm2 logs crash-warning-monitor --lines 50
```

查看最近的预警记录：

```bash
ls -lht data/daily_crash_warnings/ | head -10
cat data/daily_crash_warnings/crash_warning_$(date +%Y%m%d).json
```

## 🔔 重要说明

1. **无论任何行情**，只要检测到暴跌风险就会发送TG消息
2. 消息会明确提示：**立即平掉所有多头持仓**
3. 建议配置为每5分钟运行一次，及时捕捉暴跌信号
4. 检测需要至少3个完整波峰（A、B、C点都存在）
5. 如果当天没有检测到预警，不会发送消息

## 📝 修改配置

如需修改Telegram Bot或Chat ID：

```bash
# 编辑脚本
nano scripts/daily_crash_warning_monitor.py

# 修改第24-25行
TELEGRAM_BOT_TOKEN = "你的Bot Token"
TELEGRAM_CHAT_ID = "你的Chat ID"
```

## 🆘 故障排查

### Telegram消息发送失败

1. 检查Bot Token和Chat ID是否正确
2. 检查网络连接
3. 查看错误日志：`logs/crash-warning-error.log`

### 未检测到预警

1. 确认当天有波峰数据：`ls data/coin_change_tracker/wave_peaks/`
2. 检查完整波峰数量（需要≥3个）
3. 手动运行脚本查看详细输出

### PM2进程异常

```bash
pm2 restart crash-warning-monitor
pm2 logs crash-warning-monitor --err
```

## 📅 更新日志

- **2026-02-24**: 新增暴跌预警Telegram自动通知功能
  - 检测到暴跌风险时自动发TG消息
  - 提醒立即平掉所有多头持仓
  - 提供详细的A点递减数据和操作建议

## 🔗 相关文件

- 监控脚本：`scripts/daily_crash_warning_monitor.py`
- PM2配置：`ecosystem.config.js`
- 预警数据：`data/daily_crash_warnings/`
- 波峰数据：`data/coin_change_tracker/wave_peaks/`

## 💡 使用建议

1. 建议使用cron或PM2定时任务，每5分钟自动检查
2. 及时查看Telegram通知，快速响应
3. 定期查看预警记录，总结暴跌规律
4. 可以结合前端暴跌预警模块一起使用
