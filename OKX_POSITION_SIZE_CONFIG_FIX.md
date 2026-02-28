# OKX自动策略仓位百分比配置修复

## 修复时间
**2026-02-18 01:45 UTC (09:45 北京时间)**

## 问题描述

用户反馈：触发67000策略时，开仓比例不对。
- 预期：使用配置的仓位百分比（如1.5%）
- 实际：代码中硬编码了0.015（1.5%），未从配置文件读取

## 根本原因

两个策略执行函数中的仓位百分比被硬编码：

1. **executeUpRatio0Strategy()** - 上涨占比0触发策略
   - 位置：`templates/okx_trading.html` 第7252行  
   - 问题：`totalEquity * 0.015` 硬编码1.5%

2. **executeAutoTrade()** - BTC价格触发策略  
   - 位置：`templates/okx_trading.html` 第7431行
   - 问题：`totalEquity * 0.015` 硬编码1.5%

## 修复方案

### 1. 修改代码从配置读取 `positionSize`

**修改前（硬编码）：**
```javascript
const maxOrderSize = 5;
const positionUSDT = Math.min(
    totalEquity * 0.015,  // 硬编码1.5%
    maxOrderSize
);
```

**修改后（从配置读取）：**
```javascript
const positionSizePercent = account.positionSize || 1.5; // 从配置读取，默认1.5%
const maxOrderSize = 5;
const positionUSDT = Math.min(
    totalEquity * (positionSizePercent / 100),  // 使用配置值
    maxOrderSize
);
console.log(`📊 每个币种开仓金额: ${positionUSDT.toFixed(2)} USDT (总权益${totalEquity.toFixed(2)} × ${positionSizePercent}%, 上限${maxOrderSize}U)`);
```

### 2. 更新配置文件结构

**新增 `positionSize` 字段：**

```json
{
  "enabled": false,
  "triggerPrice": 67000.0,
  "strategyType": "bottom_performers",
  "positionSize": 1.5,              // 新增：仓位百分比（%）
  "lastExecutedTime": "2026/2/18 01:41:31",
  "executedCount": 2,
  "lastUpdated": "2026-02-17 17:41:31"
}
```

## 修复效果

### 计算示例（基于用户账户）

**账户信息：**
- 总权益：198.64 USDT
- 可用余额：4.47 USDT  
- 持仓保证金：187.99 USDT

**配置 `positionSize = 1.5` 时：**
- 每币种开仓：198.64 × 1.5% = **2.98 USDT**
- 8个币种总计：2.98 × 8 = **23.84 USDT**
- 符合风险管理（总权益的12%）

**配置 `positionSize = 3.0` 时：**
- 每币种开仓：198.64 × 3% = **5.96 USDT** → 上限5 USDT
- 8个币种总计：5 × 8 = **40 USDT**

**配置 `positionSize = 0.5` 时：**
- 每币种开仓：198.64 × 0.5% = **0.99 USDT**
- 8个币种总计：0.99 × 8 = **7.92 USDT**

## 灵活性提升

修复后，用户可以：

1. **为不同账户配置不同的仓位百分比**  
   - 保守账户：`positionSize: 0.5` (0.5%)
   - 稳健账户：`positionSize: 1.5` (1.5%)
   - 激进账户：`positionSize: 3.0` (3.0%)

2. **支持仓位/杠杆配置库**  
   - 柔韧追踪：1-5%
   - 空单追踪：3%、5%、8%
   - 柔单轻跟：3-5%

3. **动态调整策略**  
   - 无需修改代码
   - 只需更新JSON配置文件
   - 实时生效

## 配置文件位置

```
data/okx_auto_strategy/
├── account_poit_main.json          # ✅ 已更新，包含positionSize
├── account_main.json               # ⚠️ 需要添加positionSize字段
├── account_fangfang12.json         # ⚠️ 需要添加positionSize字段
└── account_marks.json              # ⚠️ 需要添加positionSize字段
```

## 部署状态

- ✅ 代码已修复：`executeAutoTrade()` 和 `executeUpRatio0Strategy()` 
- ✅ 配置已更新：`account_poit_main.json` 添加 `positionSize: 1.5`
- ✅ Flask应用已重启
- ✅ PM2配置已保存

## 验证方法

1. **查看日志输出：**
   ```bash
   pm2 logs flask-app --lines 50 | grep "开仓金额\|positionSize"
   ```

2. **触发策略时查看Console：**
   ```
   📊 每个币种开仓金额: 2.98 USDT (总权益198.64 × 1.5%, 上限5U)
   ```

3. **检查实际下单金额是否符合预期**

## 未来建议

1. **前端UI配置**  
   - 在OKX交易页面添加仓位百分比配置输入框
   - 支持实时修改和保存

2. **预设模板**  
   - 提供多种风险等级模板（保守/稳健/激进）
   - 一键应用不同的仓位配置

3. **风险提示**  
   - 当仓位百分比过高时给出警告
   - 计算并显示最大可能亏损

## 相关文档

- `COIN_CHANGE_TRACKER_FIX.md` - 币种涨跌幅追踪修复
- `BASELINE_PRICE_FIX.md` - 基准价格修复  
- `CHART_RENDERING_FIX_REPORT.md` - 图表渲染修复

## 总结

✅ **问题已解决**：策略执行函数现在从配置文件读取 `positionSize`，支持灵活配置不同账户的仓位百分比。

✅ **兼容性**：如果配置文件中没有 `positionSize` 字段，使用默认值1.5%。

✅ **用户体验**：用户可以直接修改JSON配置文件调整仓位，无需改动代码。
