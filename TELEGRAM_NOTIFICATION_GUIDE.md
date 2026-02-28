# OKX 止盈止损 Telegram 通知配置指南

## 📱 功能说明

止盈止损系统会在以下情况自动发送Telegram通知：
1. ✅ **止盈/止损订单设置成功** - 订单已提交到OKX，等待市场触发
2. ❌ **止盈/止损订单设置失败** - API调用失败或参数错误

**注意：** 
- 通知的是"订单设置成功"，不是"平仓完成"
- 实际平仓需要等待市场价格触发订单
- OKX平仓完成后不会发送额外通知（需要OKX自己的通知功能）

---

## 🔧 配置步骤

### 第一步：创建Telegram Bot

1. 打开Telegram，搜索 `@BotFather`
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称和用户名
4. 获取 **Bot Token**（格式类似：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 第二步：获取Chat ID

**方法1：使用 @userinfobot**
1. 搜索 `@userinfobot`
2. 点击 Start
3. 它会返回你的 User ID（就是Chat ID）

**方法2：使用API获取**
1. 先给你的Bot发送任意消息
2. 访问: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. 在返回的JSON中找到 `"chat":{"id": 123456789}`

### 第三步：填写配置文件

编辑文件：`/home/user/webapp/config/telegram_config.py`

```python
# Telegram Bot Token (从 @BotFather 获取)
TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"

# Telegram Chat ID (您的用户 ID)
TELEGRAM_CHAT_ID = "123456789"
```

**保存文件后重启监控服务：**

```bash
pm2 restart okx-tpsl-monitor
```

---

## 📨 通知格式示例

### 止盈触发通知

```
🎯 OKX 止盈触发

📊 账户: account_main
💰 交易对: BTC-USDT-SWAP
📈 方向: 多单
💵 开仓价: 95000.00 USDT
🎲 触发价: 106400.00 USDT
📊 当前价: 106450.00 USDT
💹 当前盈亏: +12.05%
✅ 状态: 止盈订单已设置

⏰ 2026-02-17 20:30:15

ℹ️ 等待市场价格触发平仓...
```

### 止损触发通知

```
🛑 OKX 止损触发

📊 账户: account_main
💰 交易对: ETH-USDT-SWAP
📈 方向: 空单
💵 开仓价: 3200.00 USDT
🎲 触发价: 3456.00 USDT
📊 当前价: 3465.00 USDT
💹 当前盈亏: -8.28%
✅ 状态: 止损订单已设置

⏰ 2026-02-17 20:35:22

ℹ️ 等待市场价格触发平仓...
```

### 设置失败通知

```
⚠️ OKX 止盈止损失败

账户: account_main
交易对: BTC-USDT-SWAP
方向: 多单
类型: 止盈
状态: ❌ 设置失败
错误: Parameter tpTriggerPx error

时间: 2026-02-17 20:40:10
```

---

## 🧪 测试配置

配置完成后，可以使用测试脚本验证：

```bash
cd /home/user/webapp
python3 test_telegram.py
```

或者手动测试：

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "<YOUR_CHAT_ID>",
    "text": "🧪 测试消息 - OKX止盈止损监控系统",
    "parse_mode": "HTML"
  }'
```

如果收到消息，说明配置成功！

---

## 🔍 故障排查

### 问题1：未收到通知

**检查配置：**
```bash
cat /home/user/webapp/config/telegram_config.py
# 确认 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID 不为空
```

**检查日志：**
```bash
pm2 logs okx-tpsl-monitor --lines 50 | grep -i telegram
```

**常见原因：**
- Bot Token或Chat ID配置错误
- Bot未启动对话（需要先给Bot发送 `/start`）
- 网络问题（无法访问Telegram API）

---

### 问题2：通知内容乱码

**原因：** 可能是编码问题

**解决：** 确保配置文件使用UTF-8编码

```bash
file /home/user/webapp/config/telegram_config.py
# 应显示: UTF-8 Unicode text
```

---

### 问题3：频繁通知

**原因：** 监控服务检查频率太高

**解决：** 调整检查间隔

编辑 `source_code/okx_tpsl_monitor.py`，修改：

```python
CHECK_INTERVAL = 60  # 改为更长时间，如 300（5分钟）
```

---

## ⚙️ 高级配置

### 发送到群组

1. 创建Telegram群组
2. 将你的Bot添加到群组
3. 给群组发送任意消息
4. 访问: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
5. 找到群组的Chat ID（通常是负数，如 `-123456789`）
6. 在配置文件中使用群组的Chat ID

### 多账号通知

如果需要不同账户发送到不同Telegram，需要修改代码：

在 `okx_tpsl_monitor.py` 中：
1. 从账户配置文件读取专属的 `telegram_chat_id`
2. 每个账户使用自己的Chat ID发送通知

---

## 📊 通知内容说明

| 字段 | 说明 |
|------|------|
| 账户 | 触发的交易账户ID |
| 交易对 | 触发的合约交易对 |
| 方向 | 多单（long）或空单（short） |
| 开仓价 | 持仓的平均开仓价格 |
| 触发价 | 止盈/止损订单的触发价格 |
| 当前价 | 标记价格（市场当前价） |
| 当前盈亏 | 基于标记价格计算的浮动盈亏 |
| 状态 | 订单设置成功或失败 |

---

## ⚠️ 重要提醒

1. **通知≠平仓**
   - 收到通知表示订单已设置
   - 实际平仓需要等待市场价格触发
   - 可以在OKX网页/APP查看订单状态

2. **每个持仓只触发一次**
   - 防止重复通知
   - 执行记录保存在 `*_tpsl_execution.jsonl`

3. **保护Bot Token**
   - 不要公开分享Bot Token
   - 不要提交到公开仓库
   - 定期更换Token

4. **网络依赖**
   - Telegram API需要网络连接
   - 如果网络中断，通知会失败
   - 失败信息会记录在日志中

---

## 📚 相关文档

- **主文档**: `OKX_TPSL_MONITOR_SYSTEM.md`
- **监控脚本**: `source_code/okx_tpsl_monitor.py`
- **配置文件**: `config/telegram_config.py`

---

**最后更新：** 2026-02-17  
**版本：** 1.0
