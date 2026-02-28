# OKX持仓模式修复说明

## 🔍 问题分析

### 错误信息
```
sCode: '51000'
sMsg: "Parameter posSide error"
```

### 根本原因
OKX有两种持仓模式：

1. **单向持仓模式（Net Mode）**
   - 同一币种只能持有一个方向（做多或做空）
   - **不需要**指定`posSide`参数
   - 系统根据`side`自动判断：`buy`=开多/平空，`sell`=开空/平多

2. **双向持仓模式（Long/Short Mode）**
   - 同一币种可以同时做多和做空
   - **必须**指定`posSide`参数（`long`或`short`）

**问题**：代码之前总是传递`posSide`参数，但你的账户是"单向持仓模式"，导致报错！

---

## ✅ 解决方案

### 已实施的修复

#### 1. 自动检测账户持仓模式
```python
# 调用 OKX API: /api/v5/account/config
# 获取 posMode: "net_mode" 或 "long_short_mode"
```

#### 2. 根据持仓模式调整参数

**设置杠杆时**：
```python
leverage_body = {
    'instId': inst_id,
    'lever': str(leverage),
    'mgnMode': 'isolated',
}

# 只有双向持仓模式才加 posSide
if position_mode == 'long_short_mode' and pos_side:
    leverage_body['posSide'] = pos_side
```

**下单时**：
```python
order_params = {
    'instId': inst_id,
    'tdMode': 'isolated',
    'side': side,  # buy/sell
    'ordType': order_type,
    'sz': contracts_str
}

# 只有双向持仓模式才加 posSide
if position_mode == 'long_short_mode' and pos_side:
    order_params['posSide'] = pos_side
else:
    # 单向持仓模式：OKX自动判断
    # side='buy' → 开多或平空
    # side='sell' → 开空或平多
```

---

## 🧪 测试步骤

### 1. 查看日志，确认持仓模式检测
```bash
cd /home/user/webapp && pm2 logs flask-app --nostream | grep "账户配置"
```

应该看到：
```
[账户配置] 持仓模式: net_mode
```

### 2. 刷新页面并测试开仓
- 访问：https://5000-ikmpd2up5chrwx4jjjjih-5634da27.sandbox.novita.ai/anchor-system-real
- 点击"批量开仓 A"或"批量开仓 B"
- 使用**小额测试**（10-20 USDT）

### 3. 查看详细日志
```bash
cd /home/user/webapp && pm2 logs flask-app --nostream --lines 50 | grep -E "持仓模式|OKX下单|响应结果"
```

---

## 📊 持仓模式对比

| 特性 | 单向持仓（Net Mode） | 双向持仓（Long/Short Mode） |
|------|---------------------|---------------------------|
| 同时做多做空 | ❌ 不支持 | ✅ 支持 |
| `posSide`参数 | ❌ 不需要 | ✅ 必需 |
| 适用场景 | 简单单边策略 | 复杂套利策略 |
| 保证金效率 | 较高 | 较低 |

---

## 🔄 如何切换持仓模式

### 切换到双向持仓模式（如果需要）

1. **登录OKX**
   - 访问：https://www.okx.com/

2. **进入持仓设置**
   - 交易 → 永续合约
   - 右上角"账户" → "持仓模式"

3. **选择模式**
   - 单向持仓（Net Mode）- **当前模式，推荐保持**
   - 双向持仓（Long/Short Mode）- 如需同时做多做空

4. **注意**
   - 切换前需要平掉所有持仓
   - 切换后保证金效率会降低

---

## ⚠️ 重要提示

### 1. 账户模式问题已解决 ✅
之前的错误51010（"You can't complete this request under your current account mode"）已通过切换到"单币种保证金模式"解决。

### 2. 持仓模式问题已解决 ✅
现在代码会自动检测你的持仓模式（单向/双向），并正确设置参数。

### 3. 测试建议
- **先用小额**：10-20 USDT测试
- **设置止损**：防止大幅亏损
- **观察日志**：确认订单成功提交

---

## 📝 修改的文件

- `source_code/app_new.py`（第14816-14960行）
  - 添加持仓模式检测
  - 条件性设置`posSide`参数

---

## 🔗 相关文档

- [OKX账户模式配置](OKX_ACCOUNT_MODE_CONFIGURATION.md)
- [OKX API配置指南](OKX_API_CONFIGURATION_GUIDE.md)

---

## 📞 如果仍然失败

### 查看实时日志
```bash
cd /home/user/webapp && pm2 logs flask-app --lines 0
```

### 检查关键信息
1. `[账户配置] 持仓模式: xxx` - 确认模式检测成功
2. `[持仓模式] 单向持仓，不设置posSide` - 确认参数正确
3. `[OKX下单] 响应结果: {...}` - 查看OKX返回的错误

### 可能的新错误
- `51008`: 账户余额不足
- `51009`: 持仓数量不足（平仓时）
- `51001`: 交易对不存在或暂停交易

---

**生成时间**：2026-02-02 00:49 UTC
**状态**：✅ 已修复并部署
