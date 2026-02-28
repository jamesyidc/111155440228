# 🚨 1小时爆仓金额超级预警监控 - 使用指南

## 📋 功能概述

当1小时爆仓金额超过**1.5亿**时，自动发送**3次连续TG通知**进行超级预警。

## 🎯 核心特性

### 监控规则
- **监控指标**: 1小时爆仓金额（hour_1_amount）
- **告警阈值**: **1.5亿**（150,000万）
- **检查间隔**: **30分钟**
- **通知次数**: **3次连续通知**（每次间隔3秒）
- **冷却时间**: 30分钟（同一告警不重复发送）

### 通知内容
每次告警包含以下信息：
- 🚨 超级预警标题
- 💰 1小时爆仓金额
- 💵 24小时爆仓金额
- 😱 恐慌指数
- 🌊 清洗指数
- ⏰ 数据时间
- 🔗 月线图链接

## 🚀 快速开始

### 1. 查看监控状态

```bash
pm2 list | grep liquidation-alert-monitor
```

### 2. 查看实时日志

```bash
# 实时日志（持续输出）
pm2 logs liquidation-alert-monitor

# 最近20行日志
pm2 logs liquidation-alert-monitor --lines 20 --nostream
```

### 3. 重启监控器

```bash
pm2 restart liquidation-alert-monitor
```

### 4. 停止监控器

```bash
pm2 stop liquidation-alert-monitor
```

## 📊 监控器状态

### 检查运行状态

```bash
cd /home/user/webapp
pm2 info liquidation-alert-monitor
```

### 查看告警历史

```bash
# 查看日志文件
tail -100 logs/liquidation_alert_monitor.log

# 查看告警状态
cat data/liquidation_alert_state.json
```

### 告警状态文件格式

```json
{
  "last_alert_time": "2026-02-08T08:55:40+08:00",
  "last_alert_amount": 180000,
  "alert_count": 1
}
```

## 🧪 测试告警

### 方法1：使用测试脚本（推荐）

```bash
cd /home/user/webapp
python3 test_liquidation_alert.py
```

这会：
1. 写入一条测试数据（1小时爆仓金额：1.8亿）
2. 监控器在下次检查时会发现并发送告警

### 方法2：手动触发检查

```bash
# 临时运行一次检查（不启动持久监控）
cd /home/user/webapp
python3 -c "from liquidation_alert_monitor import check_and_alert; check_and_alert()"
```

### 方法3：修改阈值测试

临时降低阈值进行测试：

```python
# 编辑 liquidation_alert_monitor.py
# 将 ALERT_THRESHOLD = 150000 改为 ALERT_THRESHOLD = 100
# 然后重启: pm2 restart liquidation-alert-monitor
```

## 📝 日志文件

### 日志位置

```
/home/user/webapp/logs/liquidation_alert_monitor.log
```

### 查看日志

```bash
# 查看最近100行
tail -100 /home/user/webapp/logs/liquidation_alert_monitor.log

# 实时跟踪
tail -f /home/user/webapp/logs/liquidation_alert_monitor.log

# 搜索告警记录
grep "🚨" /home/user/webapp/logs/liquidation_alert_monitor.log

# 搜索发送成功记录
grep "✅ TG消息发送成功" /home/user/webapp/logs/liquidation_alert_monitor.log
```

### 日志内容示例

```
[2026-02-08 08:55:40] ============================================================
[2026-02-08 08:55:40] 🚀 启动1小时爆仓金额超级预警监控
[2026-02-08 08:55:40] ⏱️  检查间隔: 30分钟
[2026-02-08 08:55:40] 🎯 告警阈值: 1.5亿
[2026-02-08 08:55:40] 📢 通知次数: 3次/告警
[2026-02-08 08:55:40] ============================================================
[2026-02-08 08:55:40] 🔍 开始检查1小时爆仓金额...
[2026-02-08 08:55:40] 📊 当前1小时爆仓金额: 0.02亿 (阈值: 1.5亿)
[2026-02-08 08:55:40] ⏰ 数据时间: 2026-02-08 08:52:52
[2026-02-08 08:55:40] ✅ 金额正常（0.02亿 < 1.5亿）
[2026-02-08 08:55:40] 💤 下次检查: 30分钟后
```

## ⚙️ 配置说明

### 环境变量

监控器需要以下环境变量（已在 `.env` 中配置）：

```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

### 修改配置

#### 修改告警阈值

```python
# 编辑 liquidation_alert_monitor.py
ALERT_THRESHOLD = 150000  # 改为你想要的值（单位：万）
```

#### 修改检查间隔

```python
# 编辑 liquidation_alert_monitor.py
# 在 run_monitor() 函数中
time.sleep(30 * 60)  # 改为你想要的秒数
```

#### 修改通知次数

```python
# 编辑 liquidation_alert_monitor.py
# 在 send_super_alert() 函数中
for i in range(3):  # 改为你想要的次数
```

### 重启生效

修改配置后需要重启监控器：

```bash
pm2 restart liquidation-alert-monitor
```

## 🔧 故障排除

### 问题1：监控器未运行

**症状**：`pm2 list` 中看不到 `liquidation-alert-monitor`

**解决方案**：
```bash
cd /home/user/webapp
pm2 start liquidation_alert_monitor.py --name liquidation-alert-monitor --interpreter python3
pm2 save
```

### 问题2：TG通知未发送

**症状**：日志显示检测到高额爆仓，但没有发送通知

**可能原因**：
1. TG配置未设置或错误
2. 网络问题
3. TG API限流

**解决方案**：
```bash
# 检查TG配置
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID

# 查看详细日志
pm2 logs liquidation-alert-monitor --lines 50

# 手动测试TG发送
python3 -c "
import os, requests
token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')
url = f'https://api.telegram.org/bot{token}/sendMessage'
r = requests.post(url, json={'chat_id': chat_id, 'text': '测试消息'})
print(r.json())
"
```

### 问题3：重复发送告警

**症状**：短时间内收到多次相同告警

**可能原因**：告警状态文件损坏或被删除

**解决方案**：
```bash
# 检查状态文件
cat data/liquidation_alert_state.json

# 如果文件损坏，删除并重启
rm data/liquidation_alert_state.json
pm2 restart liquidation-alert-monitor
```

### 问题4：监控器频繁重启

**症状**：`pm2 list` 显示重启次数不断增加

**可能原因**：代码异常或依赖缺失

**解决方案**：
```bash
# 查看错误日志
pm2 logs liquidation-alert-monitor --err --lines 50

# 手动运行测试
cd /home/user/webapp
python3 liquidation_alert_monitor.py
```

## 📈 监控指标

### 关键指标说明

| 指标 | 说明 | 单位 |
|------|------|------|
| hour_1_amount | 1小时爆仓金额 | 万（÷10000=亿） |
| hour_24_amount | 24小时爆仓金额 | 万（÷10000=亿） |
| panic_index | 恐慌指数 | 0-1 |
| wash_index | 清洗指数 | 浮点数 |

### 阈值建议

| 市场状况 | 建议阈值 | 说明 |
|----------|----------|------|
| 平静市场 | 1.5亿 | 标准阈值 |
| 波动市场 | 2.0亿 | 减少误报 |
| 剧烈波动 | 3.0亿 | 只关注极端情况 |

## 🔄 更新流程

### 更新监控脚本

```bash
cd /home/user/webapp

# 1. 编辑脚本
nano liquidation_alert_monitor.py

# 2. 测试运行
python3 liquidation_alert_monitor.py

# 3. 重启生效
pm2 restart liquidation-alert-monitor

# 4. 查看日志确认
pm2 logs liquidation-alert-monitor --lines 20
```

### 版本管理

```bash
# 提交更改
git add liquidation_alert_monitor.py
git commit -m "update: liquidation alert monitor configuration"

# 查看历史
git log --oneline -- liquidation_alert_monitor.py
```

## 📊 统计信息

### 查看告警统计

```bash
# 总告警次数
cat data/liquidation_alert_state.json | grep alert_count

# 最近10次告警
grep "🚨 准备发送超级预警" logs/liquidation_alert_monitor.log | tail -10

# 今天的告警次数
grep "$(date +%Y-%m-%d)" logs/liquidation_alert_monitor.log | grep "🚨" | wc -l
```

## 🎯 最佳实践

### 1. 定期检查
```bash
# 每天检查一次监控器状态
pm2 list | grep liquidation-alert-monitor
```

### 2. 日志轮转
```bash
# 定期清理旧日志（保留最近7天）
find /home/user/webapp/logs -name "liquidation_alert_monitor.log.*" -mtime +7 -delete
```

### 3. 告警测试
```bash
# 每周测试一次告警功能
python3 test_liquidation_alert.py
```

### 4. 配置备份
```bash
# 备份配置文件
cp liquidation_alert_monitor.py liquidation_alert_monitor.py.backup
```

## 🔗 相关链接

- **月线图页面**: https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/liquidation-monthly
- **恐慌指数页面**: https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/panic
- **主要事件监控**: https://5000-idfgz76cf9poiqtgzfhan-c81df28e.sandbox.novita.ai/major-events

## 📞 技术支持

如有问题，请查看：
1. 监控器日志: `pm2 logs liquidation-alert-monitor`
2. 系统日志: `logs/liquidation_alert_monitor.log`
3. 告警状态: `data/liquidation_alert_state.json`

---

**最后更新**: 2026-02-08  
**版本**: v1.0  
**状态**: ✅ 运行中
