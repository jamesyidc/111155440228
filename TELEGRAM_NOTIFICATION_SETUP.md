# Telegram 通知配置指南

## 📋 配置步骤

### 1. 创建Telegram Bot

1. 在Telegram中搜索 **@BotFather**
2. 发送 `/newbot` 命令
3. 按提示设置Bot名称和用户名
4. 获得Bot Token（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 2. 获取Chat ID

**方法1：通过 @userinfobot**
1. 在Telegram中搜索 **@userinfobot**
2. 点击Start或发送任意消息
3. Bot会返回你的Chat ID（格式：`123456789`）

**方法2：通过 @get_id_bot**
1. 在Telegram中搜索 **@get_id_bot**
2. 发送 `/start`
3. Bot会返回你的User ID

### 3. 配置环境变量

编辑 `/home/user/webapp/.env` 文件：

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

**示例：**
```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=6789012345:AAFGHijklMNOPQRstuvWXYZ1234567890AB
TELEGRAM_CHAT_ID=987654321
```

### 4. 重启服务

```bash
# 重启止盈止损监控服务以加载新配置
pm2 restart okx-tpsl-monitor
```

---

## 📱 通知消息格式

### 止盈通知（成功）

```
🎯 OKX 止盈止损通知

账户: account_main
交易对: BTC-USDT-SWAP
方向: 多单
类型: 止盈
开仓价: 95000.00 USDT
触发价: 106400.00 USDT
状态: ✅ 设置成功

时间: 2026-02-17 20:30:00
```

### 止损通知（成功）

```
🎯 OKX 止盈止损通知

账户: account_main
交易对: ETH-USDT-SWAP
方向: 空单
类型: 止损
开仓价: 3200.00 USDT
触发价: 3456.00 USDT
状态: ✅ 设置成功

时间: 2026-02-17 20:30:00
```

### 失败通知

```
⚠️ OKX 止盈止损失败

账户: account_main
交易对: BTC-USDT-SWAP
方向: 多单
类型: 止盈
状态: ❌ 设置失败
错误: Insufficient margin

时间: 2026-02-17 20:30:00
```

---

## 🔍 验证配置

### 方法1：查看环境变量

```bash
cd /home/user/webapp
grep TELEGRAM .env
```

**输出示例：**
```
TELEGRAM_BOT_TOKEN=6789012345:AAFGHijklMNOPQRstuvWXYZ1234567890AB
TELEGRAM_CHAT_ID=987654321
```

### 方法2：测试发送消息

创建测试脚本 `test_telegram.py`:

```python
#!/usr/bin/env python3
import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ Telegram未配置")
    print(f"BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:10]}..." if TELEGRAM_BOT_TOKEN else "未设置")
    print(f"CHAT_ID: {TELEGRAM_CHAT_ID}" if TELEGRAM_CHAT_ID else "未设置")
    exit(1)

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
message = "🧪 <b>Telegram配置测试</b>\n\n这是一条测试消息，如果你看到了，说明配置成功！✅"
payload = {
    'chat_id': TELEGRAM_CHAT_ID,
    'text': message,
    'parse_mode': 'HTML'
}

try:
    response = requests.post(url, json=payload, timeout=10)
    if response.status_code == 200:
        print("✅ Telegram配置正确，测试消息已发送！")
    else:
        print(f"❌ 发送失败: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ 异常: {e}")
```

运行测试：

```bash
cd /home/user/webapp
python3 test_telegram.py
```

---

## ⚠️ 常见问题

### 问题1：未收到通知

**排查步骤：**

1. **检查环境变量**
```bash
cd /home/user/webapp
cat .env | grep TELEGRAM
```

2. **检查PM2环境变量**
```bash
pm2 env okx-tpsl-monitor | grep TELEGRAM
```

3. **重启服务**
```bash
pm2 restart okx-tpsl-monitor --update-env
```

4. **查看日志**
```bash
pm2 logs okx-tpsl-monitor | grep Telegram
```

### 问题2：Bot Token无效

**错误消息：**
```
❌ 通知发送失败: 401
```

**解决方案：**
- 检查Token是否完整复制
- 确认Token中没有多余空格
- 重新从 @BotFather 获取Token

### 问题3：Chat ID错误

**错误消息：**
```
❌ 通知发送失败: 400
```

**解决方案：**
1. 确认Chat ID是纯数字
2. 重新从 @userinfobot 获取
3. 确保你已经向Bot发送过至少一条消息（点击Start）

### 问题4：PM2未加载环境变量

**解决方案：**

```bash
# 方法1：重启时更新环境变量
pm2 restart okx-tpsl-monitor --update-env

# 方法2：删除并重新添加
pm2 delete okx-tpsl-monitor
pm2 start source_code/okx_tpsl_monitor.py \
  --name okx-tpsl-monitor \
  --interpreter python3
```

---

## 🔧 高级配置

### 配置多个接收者（群组）

如果要发送到群组：

1. 创建Telegram群组
2. 将Bot添加到群组
3. 在群组中发送消息：`/my_id @your_bot_name`
4. 使用 @get_id_bot 或 @userinfobot 获取群组ID
5. 群组ID通常是负数，例如：`-123456789`

修改 `.env`:
```bash
TELEGRAM_CHAT_ID=-123456789
```

### 自定义消息模板

修改 `source_code/okx_tpsl_monitor.py` 中的消息内容：

```python
tg_message = (
    f"🎯 <b>自定义标题</b>\n\n"
    f"账户: <code>{self.account_id}</code>\n"
    f"交易对: <code>{inst_id}</code>\n"
    # ... 其他内容
)
```

### 禁用Telegram通知

**方法1：删除环境变量**
```bash
# 编辑.env，删除或注释掉TELEGRAM配置
# TELEGRAM_BOT_TOKEN=...
# TELEGRAM_CHAT_ID=...
```

**方法2：设置为空值**
```bash
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

然后重启服务：
```bash
pm2 restart okx-tpsl-monitor --update-env
```

---

## 📊 通知日志

所有Telegram通知都会记录在PM2日志中：

```bash
# 查看通知日志
pm2 logs okx-tpsl-monitor | grep Telegram

# 查看最近的通知
pm2 logs okx-tpsl-monitor --lines 100 | grep "✅\|❌"
```

**日志示例：**
```
[account_main] [Telegram] ✅ 通知发送成功
[account_fangfang12] [Telegram] 未配置，跳过通知
[account_poit_main] [Telegram] ❌ 通知发送失败: 401
```

---

## ✅ 配置检查清单

- [ ] 已从 @BotFather 创建Bot并获得Token
- [ ] 已从 @userinfobot 获得Chat ID
- [ ] 已在 `.env` 文件中配置Token和Chat ID
- [ ] 已重启 `okx-tpsl-monitor` 服务
- [ ] 已运行测试脚本验证配置
- [ ] 已收到测试消息
- [ ] 已在日志中看到"✅ 通知发送成功"

---

**文档版本：** 1.0  
**最后更新：** 2026-02-17 20:45:00  
**相关服务：** okx-tpsl-monitor
