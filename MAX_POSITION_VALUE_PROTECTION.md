# OKX 最大持仓价值保护功能

## 📋 功能说明

为了防止**错误开单**导致的大额损失，系统增加了**最大持仓价值限制**功能。

### 🎯 使用场景

**示例：**
- 账户资金：300 USDT
- 正常杠杆：1.5%
- 正常单笔金额：300 × 1.5% = 4.5 USDT
- **设置保护：5 USDT**

**效果：**
- ✅ 正常订单（≤5U）：自动执行止盈止损
- ❌ 异常订单（>5U）：**跳过止盈止损**，发送Telegram警告

---

## ⚙️ 配置方法

### 方法1：直接编辑JSONL文件

文件：`data/okx_tpsl_settings/account_main_tpsl.jsonl`

```json
{
  "account_id": "account_main",
  "enabled": true,
  "take_profit_enabled": true,
  "take_profit_threshold": 12.0,
  "stop_loss_enabled": true,
  "stop_loss_threshold": -8.0,
  "max_position_value_usdt": 5.0,
  "last_updated": "2026-02-17 21:00:00",
  "comment": "止盈止损配置 - 最大单笔5U保护"
}
```

**关键字段：**
- `max_position_value_usdt`: 最大持仓价值（USDT）
- 默认：5.0 USDT

### 方法2：通过API（前端集成后）

```javascript
POST /api/okx-trading/tpsl-settings/account_main
{
  "takeProfitEnabled": true,
  "takeProfitThreshold": 12.0,
  "stopLossEnabled": true,
  "stopLossThreshold": -8.0,
  "maxPositionValueUsdt": 5.0,
  "enabled": true
}
```

---

## 🔍 工作原理

### 持仓价值计算

```
持仓价值(USDT) = 持仓数量 × 当前价格
```

**示例：**
- 持仓：0.001 BTC
- 当前价：95000 USDT
- **持仓价值 = 0.001 × 95000 = 95 USDT**

### 检查流程

```
1. 获取持仓信息
2. 计算持仓价值
3. 对比最大限制
   ├─ 持仓价值 ≤ 限制 → 正常执行止盈止损
   └─ 持仓价值 > 限制 → 跳过，发送警告
```

---

## 📨 Telegram通知

### 异常持仓警告

当检测到持仓价值超过限制时，会发送：

```
⚠️ 异常持仓检测

📊 账户: account_main
💰 交易对: BTC-USDT-SWAP
📈 方向: 多单
💵 持仓价值: 95.00 USDT
🛡️ 最大限制: 5.00 USDT
⚠️ 状态: 疑似错误订单，已跳过止盈止损

ℹ️ 持仓数量: 0.001
ℹ️ 当前价格: 95000.00 USDT
⏰ 2026-02-17 21:30:00

🔴 请手动检查此订单是否为错误开单！
```

### 日志示例

```
[account_main] 📊 当前持仓数: 2
[account_main] 🛡️  最大单笔限制: 5.0 USDT
[account_main] ⚠️  BTC-USDT-SWAP long: 持仓价值 95.00 USDT > 限制 5.0 USDT，跳过（疑似错误订单）
[account_main] 📊 ETH-USDT-SWAP long: 开仓=3200, 当前=3600, 价值=3.60U, 盈亏=+12.50%
[account_main] 🎯 触发止盈条件: 12.50% >= 12.00%
```

---

## 🛡️ 安全保护层级

### 第一层：最大持仓价值限制
- **目的：** 防止错误开单
- **效果：** 异常大单不会触发止盈止损
- **通知：** Telegram警告

### 第二层：止盈止损
- **目的：** 保护正常利润/控制亏损
- **效果：** 自动设置OKX止盈止损订单
- **通知：** Telegram成功/失败通知

### 第三层：防重复执行
- **目的：** 防止多次触发
- **效果：** 每个持仓只执行一次
- **记录：** `*_tpsl_execution.jsonl`

---

## 💡 配置建议

### 计算公式

```
最大持仓价值 = 账户资金 × 杠杆倍数 × 安全系数
安全系数建议：1.2 - 1.5
```

### 示例配置

| 账户资金 | 杠杆倍数 | 安全系数 | 建议限制 |
|---------|---------|---------|---------|
| 100 USDT | 1% | 1.5 | **2 USDT** |
| 300 USDT | 1.5% | 1.5 | **7 USDT** |
| 500 USDT | 2% | 1.5 | **15 USDT** |
| 1000 USDT | 3% | 1.5 | **45 USDT** |

**原则：**
- 保守账户：安全系数 1.2
- 正常账户：安全系数 1.5
- 激进账户：安全系数 2.0

---

## 🔧 不同账户配置

### account_main（保守）

```json
{"max_position_value_usdt": 5.0}
```

### account_fangfang12（正常）

```json
{"max_position_value_usdt": 10.0}
```

### account_poit_main（激进）

```json
{"max_position_value_usdt": 20.0}
```

---

## 🧪 测试验证

### 模拟场景1：正常订单

```
持仓：0.00005 BTC × 95000 = 4.75 USDT
限制：5.0 USDT
结果：✅ 通过检查，执行止盈止损
```

### 模拟场景2：异常订单

```
持仓：0.001 BTC × 95000 = 95.00 USDT
限制：5.0 USDT
结果：❌ 超过限制，跳过止盈止损，发送警告
```

### 手动测试

```bash
# 查看当前配置
cat data/okx_tpsl_settings/account_main_tpsl.jsonl | jq '.max_position_value_usdt'

# 修改限制（例如改为10 USDT）
cd data/okx_tpsl_settings
cat account_main_tpsl.jsonl | jq '.max_position_value_usdt = 10' > temp.json
mv temp.json account_main_tpsl.jsonl

# 重启监控服务
pm2 restart okx-tpsl-monitor

# 查看日志
pm2 logs okx-tpsl-monitor --lines 50 | grep "最大单笔限制"
```

---

## 📊 监控和统计

### 查看被跳过的订单

```bash
# 查看日志中的异常订单
pm2 logs okx-tpsl-monitor --lines 200 | grep "疑似错误订单"

# 统计异常次数
pm2 logs okx-tpsl-monitor --nostream --lines 1000 | grep -c "持仓价值.*> 限制"
```

### 执行记录

被跳过的异常订单**不会**写入execution文件，因为它们没有执行止盈止损。

---

## ⚠️ 注意事项

### 1. 不是拒绝开仓
- ✅ 这个功能**不会阻止开仓**
- ✅ 只是**跳过止盈止损**
- ✅ 需要**手动处理异常订单**

### 2. 需要手动干预
- 收到警告后，请：
  1. 登录OKX检查持仓
  2. 确认是否为错误订单
  3. 手动平仓或调整

### 3. 配置生效时间
- 修改配置文件后**立即生效**
- 无需重启监控服务
- 下次检查时读取新配置

### 4. 价格波动影响
- 持仓价值随价格波动
- 可能之前正常，现在异常
- 建议定期检查和调整限制

---

## 🔄 与其他功能的关系

### 开仓保护（未实现）
- 当前：无法阻止错误开仓
- 如需实现：需要在开仓API中添加检查

### 止盈止损
- 当前：只影响止盈止损触发
- 异常订单仍然存在，只是不会自动止盈止损

### Telegram通知
- 异常订单：发送警告
- 正常订单：发送止盈止损通知

---

## 📚 相关文档

- **主文档**: `OKX_TPSL_MONITOR_SYSTEM.md`
- **Telegram配置**: `TELEGRAM_NOTIFICATION_GUIDE.md`
- **监控脚本**: `source_code/okx_tpsl_monitor.py`

---

## 🎉 总结

✅ **自动保护** - 异常大单自动跳过  
✅ **Telegram警告** - 立即通知管理员  
✅ **灵活配置** - 每个账户独立设置  
✅ **简单高效** - 一个字段搞定  

**配置建议：**
```
最大持仓价值 = 账户资金 × 杠杆 × 1.5
```

**最后更新：** 2026-02-17  
**版本：** 1.0
