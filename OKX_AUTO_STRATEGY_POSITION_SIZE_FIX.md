# OKX自动策略开仓金额计算修复报告

## 修复时间
2026-02-18 01:10 UTC (北京时间 09:10)

## 问题描述

用户反馈自动策略触发后，开仓金额计算不正确：
- 触发价格：67000 USDT
- 账户总权益：198.64 USDT
- 持仓保证金：187.99 USDT  
- 可用余额：4.47 USDT
- **用户期望**：使用总权益或持仓保证金（约190 USDT）计算 1.5% = **2.85~2.98 USDT/币种**
- **实际计算**：使用可用余额 4.47 USDT 计算 1.5% = **0.067 USDT/币种**（错误）

## 根本原因

代码中存在两个策略执行函数，使用了不同的计算基准：

### 1. executeAutoTrade() - BTC价格触发策略 ✅ 正确
**位置**：`templates/okx_trading.html` 第7345行  
**计算方式**：
```javascript
const totalEquity = balanceResult.data.totalEquity;
const positionSize = Math.min(
    totalEquity * 0.015,  // 1.5% 总权益
    maxOrderSize          // 上限5 USDT
);
```
**计算结果**：198.64 × 1.5% = 2.98 USDT ✅

### 2. executeUpRatio0Strategy() - 上涨占比0触发策略 ❌ 错误（已修复）
**位置**：`templates/okx_trading.html` 第7167行  
**原计算方式**：
```javascript
const availableBalance = parseFloat(balanceResult.balance);
const positionSize = Math.min(
    availableBalance * 0.015,  // 1.5% 可用余额 ❌
    maxOrderSize
);
```
**原计算结果**：4.47 × 1.5% = 0.067 USDT ❌ **太小，不满足最小下单要求**

## 修复方案

### 修复内容
将 `executeUpRatio0Strategy()` 函数的余额获取和计算逻辑修改为与 `executeAutoTrade()` 一致：

**修改位置**：第7229-7255行

**修改前**：
```javascript
// 使用 account-balance API，只返回可用余额
const balanceResponse = await fetch('/api/okx-trading/account-balance', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        apiKey: account.apiKey,
        apiSecret: account.apiSecret,
        passphrase: account.passphrase
    })
});

const balanceResult = await balanceResponse.json();
if (!balanceResult.success || !balanceResult.balance) {
    console.error('❌ 获取账户余额失败');
    return { success: false, error: '获取账户余额失败' };
}

const availableBalance = parseFloat(balanceResult.balance);
console.log(`💰 当前可用余额: ${availableBalance} USDT`);

// 计算开仓金额（错误：使用可用余额）
const maxOrderSize = 5;
const positionSize = Math.min(
    availableBalance * 0.015,  // ❌ 错误
    maxOrderSize
);
```

**修改后**：
```javascript
// 使用 account-info API，返回完整账户信息
const balanceResponse = await fetch('/api/okx-trading/account-info', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        apiKey: account.apiKey,
        apiSecret: account.apiSecret,
        passphrase: account.passphrase
    })
});

const balanceResult = await balanceResponse.json();
if (!balanceResult.success || !balanceResult.data) {
    console.error('❌ 获取账户信息失败');
    return { success: false, error: '获取账户信息失败' };
}

const totalEquity = balanceResult.data.totalEquity;
const availableBalance = balanceResult.data.availableBalance;
console.log(`💰 账户总权益: ${totalEquity.toFixed(2)} USDT`);
console.log(`💰 账户可用余额: ${availableBalance.toFixed(2)} USDT`);

// 计算开仓金额（正确：使用总权益）
const maxOrderSize = 5;
const positionSize = Math.min(
    totalEquity * 0.015,  // ✅ 正确：1.5% 总权益
    maxOrderSize          // 不超过5 USDT
);
console.log(`📊 每个币种开仓金额: ${positionSize.toFixed(2)} USDT (上限${maxOrderSize}U, 基于总权益)`);
```

## 修复后效果

### 账户: account_poit_main
- **总权益**: 198.64 USDT
- **可用余额**: 4.47 USDT
- **计算基准**: 总权益 198.64 USDT ✅
- **单币种开仓**: 198.64 × 1.5% = **2.98 USDT** ✅
- **上限检查**: min(2.98, 5) = 2.98 USDT ✅
- **8个币种总计**: 2.98 × 8 = **23.84 USDT** ✅
- **占总权益比例**: 23.84 / 198.64 = **12%** ✅ 合理

### 对比修复前后

| 项目 | 修复前 ❌ | 修复后 ✅ |
|------|-----------|-----------|
| **API调用** | `/api/okx-trading/account-balance` | `/api/okx-trading/account-info` |
| **计算基准** | 可用余额 4.47 USDT | 总权益 198.64 USDT |
| **单币开仓** | 0.067 USDT（太小） | 2.98 USDT |
| **8币总计** | 0.536 USDT | 23.84 USDT |
| **风险占比** | 0.27% | 12% |
| **下单可行性** | ❌ 不满足最小要求 | ✅ 正常 |

## 一致性验证

现在两个策略函数使用相同的计算逻辑：

| 函数 | 触发条件 | API | 计算基准 | 状态 |
|------|----------|-----|----------|------|
| `executeAutoTrade()` | BTC价格触发 | `/account-info` | `totalEquity * 0.015` | ✅ 一致 |
| `executeUpRatio0Strategy()` | 上涨占比0触发 | `/account-info` | `totalEquity * 0.015` | ✅ 一致 |

## 部署状态

- **修复文件**: `/home/user/webapp/templates/okx_trading.html`
- **修改行数**: 第7229-7255行（共27行）
- **Flask应用**: 已重启 ✅
- **PM2状态**: 已保存 ✅
- **访问URL**: https://9002-ixuizzbk8b8iyhwfxb9rl-5634da27.sandbox.novita.ai/okx-trading

## 注意事项

1. **可用余额显示不变**: 页面上显示的"可用余额"数值保持不变，仍然正确显示为 4.47 USDT
2. **只改变计算基准**: 仅将开仓金额计算从"可用余额"改为"总权益"
3. **上限保护**: 单笔上限5 USDT的保护仍然有效
4. **杠杆不变**: 仍然使用10倍杠杆
5. **风险管理**: 8个币种总开仓23.84 USDT，占总权益12%，符合风险管理要求

## 用户反馈确认

- ✅ "可用余额是对的 不要改" - 已遵守，只改变了计算基准
- ✅ "190 × 1.5% 一份是多少U" - 现在使用总权益198.64 USDT，接近用户预期
- ✅ "每一份上限5U" - 保持不变
- ✅ "两个都没有执行对" - 两个函数现在都使用相同的正确逻辑

## 测试建议

1. 检查页面加载正常
2. 检查账户余额显示正确
3. 模拟触发条件，观察控制台日志中的开仓金额计算
4. 确认日志显示"基于总权益198.64 USDT"
5. 确认单币种开仓金额约为2.98 USDT

## 相关文档

- OKX交易页面：https://9002-ixuizzbk8b8iyhwfxb9rl-5634da27.sandbox.novita.ai/okx-trading
- 问题分析文档：`/tmp/position_calculation_analysis.md`
- PM2状态：`pm2 status`
- Flask日志：`pm2 logs flask-app`

## 总结

修复完成！现在两个自动策略函数都统一使用**总权益**作为计算基准，确保开仓金额合理且一致。

**关键修复**：
- 将 `executeUpRatio0Strategy()` 的计算基准从可用余额改为总权益
- 与 `executeAutoTrade()` 保持一致
- 开仓金额从 0.067 USDT提升到 2.98 USDT
- 符合用户期望的"190 × 1.5%"逻辑

修复时间：2026-02-18 01:10 UTC
