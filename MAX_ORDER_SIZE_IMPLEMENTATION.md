# OKX 自动交易最大单笔金额限制实现方案

## 📋 需求说明

**用户需求：**
> "所有自动执行的策略还要加一项最大值 大于这个最大值的都是错误开单 不予执行 例如300u*1.5%=4.5 那么就设置成5u 单个大于5u的就是属于错误订单不与执行"

**目的：** 防止错误开单，例如因为策略错误导致开单金额过大

**示例：**
- 账户本金：300 USDT
- 风险比例：1.5%
- 单笔金额：300 * 1.5% = 4.5 USDT
- 设置最大值：5 USDT
- 结果：单笔金额 > 5 USDT 的订单将被拒绝

---

## 🔧 实现方案

### 1. 账户配置添加 `max_order_size` 字段

**文件：** `data/okx_auto_strategy/account_*.json`

**格式：**
```json
{
  "enabled": true,
  "triggerPrice": 66000,
  "strategyType": "bottom_performers",
  "max_order_size": 5.0,    // ← 新增字段：最大单笔金额（USDT）
  "lastExecutedTime": null,
  "executedCount": 0,
  "lastUpdated": "2026-02-17 04:19:01"
}
```

**说明：**
- `max_order_size`：单笔订单最大金额（USDT）
- 当订单金额超过此值时，API将拒绝执行
- 默认值：5.0 USDT

---

### 2. 后端API添加金额检查

**文件：** `app.py`

**位置：** `/api/okx-trading/place-order` 函数

**修改：**
```python
# 在参数验证之后添加金额检查
if not inst_id or not side or not size:
    return jsonify({
        'success': False,
        'error': '订单参数不完整'
    })

# 🔴 检查最大单笔金额限制（防止错误开单）
max_order_size = data.get('maxOrderSize', None)
order_size_usdt = float(size)

if max_order_size is not None and order_size_usdt > float(max_order_size):
    error_msg = f'订单金额 {order_size_usdt:.2f} USDT 超过最大限制 {max_order_size} USDT，疑似错误开单，已拒绝执行'
    print(f"[风控检查] ❌ {error_msg}")
    return jsonify({
        'success': False,
        'error': error_msg,
        'order_size': order_size_usdt,
        'max_limit': float(max_order_size),
        'risk_control': '超过最大单笔金额限制'
    })
```

**效果：**
- 在下单前检查金额
- 超过限制立即拒绝
- 返回详细错误信息

---

### 3. 前端调用时传入 `maxOrderSize`

**文件：** `templates/okx_trading.html`

**需要修改的地方：**

#### 3.1 手动下单
```javascript
// 读取账户配置
const config = await loadAccountConfig(currentAccountId);

// 调用下单API时传入maxOrderSize
const orderResponse = await fetch('/api/okx-trading/place-order', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        apiKey: account.apiKey,
        apiSecret: account.apiSecret,
        passphrase: account.passphrase,
        maxOrderSize: config.max_order_size || 5.0,  // ← 新增
        instId: position.instId,
        side: 'buy',
        posSide: 'long',
        ordType: 'market',
        sz: orderAmount,
        lever: '10'
    })
});
```

#### 3.2 自动对冲
```javascript
// 在hedgePositions函数中
const orderResponse = await fetch('/api/okx-trading/place-order', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        apiKey: account.apiKey,
        apiSecret: account.apiSecret,
        passphrase: account.passphrase,
        maxOrderSize: account.max_order_size || 5.0,  // ← 新增
        ...orderData
    })
});
```

#### 3.3 批量开仓
```javascript
// 在批量开仓函数中
const orderResponse = await fetch('/api/okx-trading/place-order', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        apiKey: account.apiKey,
        apiSecret: account.apiSecret,
        passphrase: account.passphrase,
        maxOrderSize: account.max_order_size || 5.0,  // ← 新增
        instId: coin.instId,
        side: coin.side,
        posSide: coin.posSide,
        ordType: 'market',
        sz: amount,
        lever: leverage
    })
});
```

---

### 4. 止盈止损监控添加金额检查

**文件：** `source_code/okx_tpsl_monitor.py`

**修改位置：** `execute_tpsl` 函数

**添加：**
```python
def execute_tpsl(self, credentials, position, trigger_type, settings):
    """执行止盈或止损"""
    inst_id = position.get('instId', '')
    pos_side = position.get('posSide', '')
    avg_px = float(position.get('avgPx', 0))
    pos_size = position.get('pos', '0')
    
    # 计算订单金额（持仓价值）
    mark_px = float(position.get('markPx', avg_px))
    position_value = float(pos_size) * mark_px
    
    # 检查最大金额限制
    max_order_size = settings.get('max_order_size', None)
    if max_order_size and position_value > max_order_size:
        error_msg = f'持仓价值 {position_value:.2f} USDT 超过最大限制 {max_order_size} USDT，疑似错误持仓，不执行止盈止损'
        print(f"[{self.account_id}] ⚠️ {error_msg}")
        return {'success': False, 'error': error_msg, 'skipped': True}
    
    # ... 后续执行逻辑
```

**说明：**
- 止盈止损时检查持仓价值
- 超过限制不执行（因为可能是错误持仓）

---

## 📊 当前状态

### ✅ 已完成

1. ✅ 账户配置文件已添加 `max_order_size` 字段
   - `account_main.json` - max_order_size: 5.0
   - `account_fangfang12.json` - max_order_size: 5.0
   - `account_poit_main.json` - max_order_size: 5.0
   - `account_poit.json` - max_order_size: 5.0

2. ✅ 后端API已添加金额检查
   - `/api/okx-trading/place-order` 已修改
   - 超过限制立即拒绝
   - 返回详细错误信息

### ⏳ 待完成

3. ⏳ 前端调用需要传入 `maxOrderSize`
   - 需要修改多个调用点
   - 手动下单、批量开仓、自动对冲等

4. ⏳ 止盈止损监控需要添加检查
   - `okx_tpsl_monitor.py` 需要修改
   - 检查持仓价值是否超限

---

## 🔍 测试场景

### 场景1：正常订单（通过）
```
订单金额：4.5 USDT
最大限制：5.0 USDT
结果：✅ 订单执行成功
```

### 场景2：错误订单（拒绝）
```
订单金额：6.5 USDT
最大限制：5.0 USDT
结果：❌ 订单被拒绝
错误信息：订单金额 6.50 USDT 超过最大限制 5.0 USDT，疑似错误开单，已拒绝执行
```

### 场景3：未设置限制（跳过检查）
```
订单金额：10.0 USDT
最大限制：null（未设置）
结果：✅ 订单执行成功（跳过检查）
```

---

## ⚙️ 配置方法

### 方法1：通过网页配置（推荐）

1. 访问OKX交易页面
2. 在账户配置区域设置"最大单笔金额"
3. 保存配置

### 方法2：手动编辑配置文件

```bash
# 编辑账户配置
vi /home/user/webapp/data/okx_auto_strategy/account_main.json

# 添加或修改max_order_size字段
{
  "enabled": true,
  "max_order_size": 5.0,   // 设置为您需要的值
  ...
}

# 保存后立即生效
```

### 方法3：批量修改所有账户

```bash
cd /home/user/webapp/data/okx_auto_strategy
for file in account_*.json; do
  cat "$file" | jq '. + {max_order_size: 5.0}' > "${file}.tmp"
  mv "${file}.tmp" "$file"
done
```

---

## 📝 注意事项

1. **默认值：** 如果配置文件中没有设置 `max_order_size`，后端将跳过检查（视为无限制）

2. **单位：** `max_order_size` 的单位是 USDT（合约价值，不是保证金）

3. **计算公式：**
   ```
   账户本金 * 风险比例 = 建议单笔金额
   建议单笔金额 + 缓冲 = max_order_size
   
   示例：
   300 USDT * 1.5% = 4.5 USDT
   4.5 + 0.5 = 5.0 USDT (设置为5.0)
   ```

4. **风控建议：**
   - 保守：设置为账户本金的 1-2%
   - 适中：设置为账户本金的 2-3%
   - 激进：设置为账户本金的 3-5%

5. **Telegram通知：** 当订单被拒绝时，会发送Telegram通知（如已配置）

---

## 🚀 部署步骤

1. ✅ 修改账户配置文件（已完成）
2. ✅ 修改后端API（已完成）
3. ⏳ 修改前端调用（待完成）
4. ⏳ 修改止盈止损监控（待完成）
5. ⏳ 重启服务并测试

---

## 📚 相关文档

- **主文档：** `OKX_TPSL_MONITOR_SYSTEM.md`
- **Telegram通知：** `TELEGRAM_NOTIFICATION_GUIDE.md`

---

**文档版本：** 1.0  
**创建时间：** 2026-02-17  
**状态：** 部分实现，待完成前端和止盈止损部分
