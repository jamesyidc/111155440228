# OKX 止盈止损监控服务 - 完整配置指南

## 📋 问题诊断

### 问题现象
用户报告止盈止损没有触发，检查发现：
- `okx-tpsl-monitor` 服务状态为 **stopped**（已停止）
- 服务缺少 API 凭证（apiKey, apiSecret, passphrase）
- 监控日志显示：`Request header OK-ACCESS-KEY can not be empty.`

### 根本原因
1. **服务未运行**：监控服务处于停止状态，未进行持仓检查
2. **API凭证缺失**：账户API凭证仅存储在浏览器localStorage中，服务器端无法访问

---

## 🔧 解决方案

### 技术实现
1. **新增API端点**：`POST /api/okx-trading/save-account-credentials/<account_id>`
2. **自动保存机制**：用户保存止盈止损设置时，前端自动上传API凭证
3. **凭证存储位置**：`data/okx_auto_strategy/{account_id}.json`
4. **监控服务**：已启动 `okx-tpsl-monitor`（PM2 ID: 32）

### 配置文件示例
```json
{
  "enabled": true,
  "triggerPrice": 66000,
  "strategyType": "bottom_performers",
  "lastExecutedTime": null,
  "executedCount": 0,
  "max_order_size": 5,
  "apiKey": "YOUR_API_KEY",
  "apiSecret": "YOUR_API_SECRET",
  "passphrase": "YOUR_PASSPHRASE",
  "lastUpdated": "2026-02-17 14:48:00"
}
```

---

## 🚀 用户操作步骤

### 1️⃣ 第一步：启动监控服务（已完成）
```bash
pm2 start okx-tpsl-monitor
pm2 logs okx-tpsl-monitor  # 查看日志
```

**当前状态**：✅ 服务已启动，每60秒检查一次

---

### 2️⃣ 第二步：保存止盈止损设置（上传API凭证）

**重要提示**：您需要在OKX交易页面点击**"保存设置"**按钮，系统会自动：
1. 保存止盈止损阈值（如：止盈12%，止损-8%）
2. 保存最大持仓限制（如：5 USDT）
3. **同时上传API凭证到服务器**（apiKey, apiSecret, passphrase）

**操作路径**：
1. 打开 https://9002-iou7okyaq15h840cyuitp-c07dda5e.sandbox.novita.ai/okx-trading
2. 选择您的账户（如：account_main）
3. 在**止盈止损设置面板**中：
   - 设置止盈阈值（例如：12 USDT）
   - 设置止损阈值（例如：-8 USDT）
   - 设置最大持仓限制（例如：5.0 USDT）
   - 开启止盈/止损开关（绿色表示已启用）
4. **点击"保存设置"按钮**

**保存后会发生什么**：
- ✅ 止盈止损配置保存到 `data/okx_tpsl_settings/account_xxx_tpsl.jsonl`
- ✅ API凭证自动保存到 `data/okx_auto_strategy/account_xxx.json`
- ✅ 前端显示：`✅ 账户「xxx」的止盈止损设置已保存到服务器！`
- ✅ 控制台日志：`✅ 账户 xxx API凭证已保存到服务器`

---

### 3️⃣ 第三步：验证凭证已保存

保存设置后，可在服务器端验证：
```bash
# 检查账户配置文件是否包含API凭证
cat data/okx_auto_strategy/account_main.json | jq

# 预期输出应包含 apiKey, apiSecret, passphrase 字段
```

---

### 4️⃣ 第四步：重启监控服务（应用凭证）

凭证保存后，重启监控服务以应用新配置：
```bash
pm2 restart okx-tpsl-monitor
sleep 3
pm2 logs okx-tpsl-monitor --nostream --lines 20
```

**正常日志示例**：
```
✓ 发现账户数: 4
  账户列表: account_main, account_poit, account_fangfang12, account_poit_main

第 1 次检查 - 2026-02-17 14:50:00
[account_main] ✓ 配置已启用
[account_main] ✓ 获取到 2 个持仓
[account_main] BTC-USDT-SWAP long: 持仓价值 3.2 USDT, 盈亏 -2.5% ❌ 未达止盈止损条件
[account_main] ETH-USDT-SWAP long: 持仓价值 4.1 USDT, 盈亏 +15.2% ✅ 触发止盈！
[account_main] [Telegram] ✅ 通知发送成功
```

---

## 📊 监控服务工作流程

### 每60秒执行一次：
1. **加载配置**：读取 `{account_id}_tpsl.jsonl` 抬头，检查 `enabled` 字段
2. **读取凭证**：从 `{account_id}.json` 加载 apiKey, apiSecret, passphrase
3. **获取持仓**：调用 OKX API `/api/v5/account/positions`
4. **计算盈亏**：持仓价值 = 持仓数量 × 当前价格
5. **检查阈值**：
   - 盈亏% ≥ 止盈阈值 → 触发止盈
   - 盈亏% ≤ 止损阈值 → 触发止损
   - 持仓价值 > max_position_value_usdt → 跳过（异常订单）
6. **防重复执行**：检查 `{account_id}_tpsl_execution.jsonl`，已执行则跳过
7. **执行止盈止损**：调用 OKX API `/api/v5/trade/order-algo` 设置条件单
8. **记录结果**：写入 execution 文件，发送 Telegram 通知

---

## ⚠️ 重要注意事项

### 1. API凭证安全
- API凭证存储在服务器端 `data/okx_auto_strategy/` 目录
- **请勿**将此目录添加到Git版本控制
- 建议设置 OKX API 权限为：**只读 + 交易**（不需要提币权限）

### 2. Telegram通知配置
编辑 `config/telegram_config.py`：
```python
TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'
```

### 3. 止盈止损计算
- **基于账户总未实现盈亏**（USDT），不是单币种百分比
- 示例：账户总未实现盈亏 = +15 USDT，止盈阈值 = +12 USDT → 触发止盈

### 4. 最大持仓限制
- 用于过滤异常大单（例如：错误开仓）
- 建议设置：账户余额 × 1.5% × 1.5
- 示例：300 USDT × 1.5% × 1.5 ≈ 6.75 USDT → 建议设置 5 USDT
- 超过此限制的持仓将被跳过，并发送 Telegram 警告

---

## 🔍 故障排查

### 问题1：服务未运行
```bash
pm2 list | grep okx-tpsl-monitor
# 如果显示 stopped，执行：
pm2 start okx-tpsl-monitor
```

### 问题2：API凭证未保存
```bash
# 检查配置文件是否包含 apiKey
cat data/okx_auto_strategy/account_main.json | grep -i apikey
# 如果为空，需在前端重新保存设置
```

### 问题3：止盈止损未触发
```bash
# 查看实时日志
pm2 logs okx-tpsl-monitor --lines 50

# 可能原因：
# - 配置中 enabled = false（需开启）
# - 盈亏未达到阈值
# - 持仓已执行过（检查 execution.jsonl）
# - 持仓价值超过 max_position_value_usdt
```

### 问题4：OKX API错误
常见错误码：
- `Request header OK-ACCESS-KEY can not be empty.` → API凭证未配置
- `Invalid OK-ACCESS-SIGN` → API Secret 错误
- `Invalid OK-ACCESS-PASSPHRASE` → Passphrase 错误
- `Insufficient permissions` → API权限不足，需开启交易权限

---

## 📱 联系与支持

- 监控服务状态：`pm2 status`
- 实时日志：`pm2 logs okx-tpsl-monitor`
- 服务管理：`pm2 start|stop|restart okx-tpsl-monitor`

---

**Git Commit**: `533cdde` - 自动保存API凭证功能
**更新时间**: 2026-02-17 14:50:00
**服务地址**: https://9002-iou7okyaq15h840cyuitp-c07dda5e.sandbox.novita.ai/okx-trading
