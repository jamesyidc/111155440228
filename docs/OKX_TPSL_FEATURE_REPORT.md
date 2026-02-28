# OKX交易系统 - 统一止盈止损功能完成报告

## 📋 功能摘要

为OKX交易系统添加了统一的止盈止损百分比设置功能，支持：
1. **下单时设置**：在开仓时直接设置止盈止损百分比
2. **持仓批量设置**：为所有现有持仓统一设置止盈止损百分比

## 🎯 功能详情

### 1. 下单时设置止盈止损

#### 界面设计
在交易表单中添加了独立的止盈止损设置区域：

**位置**：快捷金额按钮下方，提交按钮上方

**包含字段**：
- ✅ **止盈百分比 (%)**: 输入盈利达到多少百分比时自动平仓
- ❌ **止损百分比 (%)**: 输入亏损达到多少百分比时自动平仓

**界面特点**：
- 蓝色渐变背景，醒目的视觉设计
- 两列网格布局，左止盈右止损
- 实时提示：显示"盈利/亏损达到X%时平仓"
- 底部说明：止盈止损基于开仓价格计算，可选填

#### 工作流程
```
1. 用户填写开仓金额和杠杆
2. 用户选填止盈/止损百分比（如: 止盈5%, 止损3%）
3. 点击下单按钮
4. 系统确认订单（包含止盈止损信息）
5. OKX执行下单
6. 下单成功后自动设置止盈止损
7. 返回结果（包含止盈止损设置状态）
```

#### 计算逻辑
```javascript
// 多单
止盈价 = 开仓价 × (1 + 止盈%)
止损价 = 开仓价 × (1 - 止损%)

// 空单
止盈价 = 开仓价 × (1 - 止盈%)
止损价 = 开仓价 × (1 + 止损%)
```

**示例**：
- **多单BTC**，开仓价 96000 USDT
  - 止盈5%：触发价 = 96000 × 1.05 = **100800 USDT**
  - 止损3%：触发价 = 96000 × 0.97 = **93120 USDT**

- **空单BTC**，开仓价 96000 USDT
  - 止盈5%：触发价 = 96000 × 0.95 = **91200 USDT**
  - 止损3%：触发价 = 96000 × 1.03 = **98880 USDT**

### 2. 持仓批量设置止盈止损

#### 界面设计
在持仓列表上方添加了批量设置区域：

**位置**：持仓标题下方，批量平仓按钮上方

**包含元素**：
- 📊 标题："批量设置止盈止损"
- 输入框：止盈百分比
- 输入框：止损百分比  
- 按钮："⚡ 应用到全部持仓"

**界面特点**：
- 蓝色渐变背景，与下单区域呼应
- 三列网格布局：止盈 | 止损 | 应用按钮
- 白色半透明输入框，视觉清晰
- 底部提示：将为所有当前持仓设置统一的止盈止损百分比

#### 工作流程
```
1. 用户查看当前持仓列表
2. 输入统一的止盈/止损百分比
3. 点击"应用到全部持仓"按钮
4. 系统获取所有持仓
5. 显示确认对话框（列出所有持仓和设置）
6. 用户确认
7. 批量为每个持仓设置止盈止损
8. 显示批量结果（成功/失败统计）
9. 自动刷新持仓列表
```

#### 批量设置逻辑
```python
for 每个持仓:
    1. 获取持仓的开仓均价
    2. 根据持仓方向（多/空）和百分比计算触发价
    3. 调用OKX止盈止损API
    4. 记录结果（成功/失败）
    5. 延迟200ms（避免请求过快）

显示结果:
    ✅ 成功: X 个
    ❌ 失败: X 个
    详细列表
```

## 💻 技术实现

### 前端修改

#### 1. HTML结构（source_code/templates/okx_trading.html）

**下单表单新增**：
```html
<!-- 止盈止损设置 -->
<div class="form-group" style="background: rgba(59, 130, 246, 0.1); ...">
    <label class="form-label">🎯 止盈止损设置（可选）</label>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
        <div>
            <label>✅ 止盈百分比 (%)</label>
            <input type="number" id="takeProfitPercent" placeholder="如: 5" step="0.1" min="0">
        </div>
        <div>
            <label>❌ 止损百分比 (%)</label>
            <input type="number" id="stopLossPercent" placeholder="如: 3" step="0.1" min="0">
        </div>
    </div>
</div>
```

**持仓区新增**：
```html
<!-- 批量设置止盈止损 -->
<div style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); ...">
    <div>批量设置止盈止损</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr auto; gap: 10px;">
        <input type="number" id="batchTakeProfit" placeholder="如: 5">
        <input type="number" id="batchStopLoss" placeholder="如: 3">
        <button onclick="batchSetTPSL()">⚡ 应用到全部持仓</button>
    </div>
</div>
```

#### 2. JavaScript函数

**submitOrder函数修改**：
```javascript
// 获取止盈止损百分比
const takeProfitPercent = document.getElementById('takeProfitPercent').value;
const stopLossPercent = document.getElementById('stopLossPercent').value;

// 添加到订单数据
if (takeProfitPercent && parseFloat(takeProfitPercent) > 0) {
    orderData.takeProfitPercent = parseFloat(takeProfitPercent);
}
if (stopLossPercent && parseFloat(stopLossPercent) > 0) {
    orderData.stopLossPercent = parseFloat(stopLossPercent);
}

// 确认信息包含止盈止损
if (takeProfitPercent || stopLossPercent) {
    tpslInfo = '\n⚡ 止盈止损设置:';
    if (takeProfitPercent) tpslInfo += `\n  ✅ 止盈: ${takeProfitPercent}%`;
    if (stopLossPercent) tpslInfo += `\n  ❌ 止损: ${stopLossPercent}%`;
}
```

**新增batchSetTPSL函数**：
```javascript
async function batchSetTPSL() {
    // 1. 验证输入
    // 2. 获取当前账户
    // 3. 获取所有持仓
    // 4. 显示确认对话框
    // 5. 批量设置止盈止损
    // 6. 显示结果
    // 7. 刷新持仓列表
}
```

### 后端修改

#### 1. 下单API修改（/api/okx-trading/place-order）

**新增逻辑**：
```python
# 获取止盈止损百分比
take_profit_percent = data.get('takeProfitPercent', None)
stop_loss_percent = data.get('stopLossPercent', None)

# 下单成功后设置止盈止损
if take_profit_percent or stop_loss_percent:
    # 1. 等待持仓建立（1秒）
    time.sleep(1)
    
    # 2. 计算止盈止损价格
    tp_px = current_price * (1 + tp_percent)  # 多单
    sl_px = current_price * (1 - sl_percent)  # 多单
    
    # 3. 调用OKX止盈止损API
    algo_params = {
        'instId': inst_id,
        'tdMode': 'isolated',
        'side': 'sell' if pos_side == 'long' else 'buy',
        'posSide': pos_side,
        'ordType': 'conditional',
        'sz': contracts_str,
        'reduceOnly': 'true',
        'tpTriggerPx': str(round(tp_px, 2)),
        'tpOrdPx': '-1',  # 市价
        'slTriggerPx': str(round(sl_px, 2)),
        'slOrdPx': '-1'   # 市价
    }
    
    # 4. 发送请求
    # 5. 记录结果
    # 6. 返回给前端
```

#### 2. 新增API端点（/api/okx-trading/set-tpsl）

**功能**: 为指定持仓设置止盈止损

**请求参数**：
```json
{
    "apiKey": "...",
    "apiSecret": "...",
    "passphrase": "...",
    "instId": "BTC-USDT-SWAP",
    "posSide": "long",
    "takeProfitPercent": 5,
    "stopLossPercent": 3
}
```

**处理流程**：
1. 验证API凭证
2. 获取持仓信息（获取开仓均价）
3. 计算止盈止损价格
4. 调用OKX条件单API
5. 记录日志
6. 返回结果

**响应格式**：
```json
{
    "success": true,
    "message": "止盈止损设置成功",
    "data": {
        "avgPx": 96000,
        "tpPrice": 100800,
        "slPrice": 93120
    }
}
```

## 🎨 用户界面

### 颜色方案
- **主色调**: 蓝色渐变 `linear-gradient(135deg, #3b82f6, #2563eb)`
- **止盈**: 绿色 `#4ade80` ✅
- **止损**: 红色 `#f87171` ❌
- **背景**: 半透明蓝色 `rgba(59, 130, 246, 0.1)`
- **边框**: 蓝色半透明 `rgba(59, 130, 246, 0.3)`

### 交互反馈
- **输入框**: 支持小数输入，步进0.1
- **确认对话框**: 显示详细的持仓列表和止盈止损设置
- **结果反馈**: 显示成功/失败统计和详细列表
- **自动刷新**: 设置成功后自动刷新持仓列表

## ✅ 功能验证

### 下单时设置止盈止损
```
测试场景：
1. 选择BTC-USDT交易对
2. 输入开仓金额：10 USDT
3. 选择杠杆：10x
4. 输入止盈：5%
5. 输入止损：3%
6. 点击下单

预期结果：
✅ 下单成功
✅ 止盈止损自动设置
✅ 确认信息包含止盈止损详情
✅ 返回结果显示设置状态
```

### 持仓批量设置
```
测试场景：
1. 已有多个持仓（如6个币种）
2. 输入批量止盈：5%
3. 输入批量止损：3%
4. 点击"应用到全部持仓"

预期结果：
✅ 显示确认对话框（列出所有持仓）
✅ 批量设置完成
✅ 显示详细结果（成功X个，失败X个）
✅ 持仓列表自动刷新
```

## 📊 数据流程

### 下单流程
```
用户输入
   ↓
前端验证
   ↓
submitOrder函数
   ↓
POST /api/okx-trading/place-order
   ↓
OKX下单API
   ↓
下单成功
   ↓
计算止盈止损价格
   ↓
OKX条件单API (设置止盈止损)
   ↓
返回结果（包含止盈止损状态）
   ↓
前端显示结果
```

### 批量设置流程
```
用户输入百分比
   ↓
点击应用按钮
   ↓
batchSetTPSL函数
   ↓
获取所有持仓
   ↓
显示确认对话框
   ↓
用户确认
   ↓
for 每个持仓:
    POST /api/okx-trading/set-tpsl
    ↓
    获取开仓均价
    ↓
    计算触发价
    ↓
    调用OKX API
   ↓
统计结果
   ↓
显示结果对话框
   ↓
刷新持仓列表
```

## 🔧 技术细节

### OKX API调用

**条件单API**: `/api/v5/trade/order-algo`

**参数说明**：
- `instId`: 交易对
- `tdMode`: 交易模式（isolated=逐仓）
- `side`: 买卖方向（sell平多，buy平空）
- `posSide`: 持仓方向（long/short）
- `ordType`: 订单类型（conditional=条件单）
- `sz`: 数量（持仓张数）
- `reduceOnly`: 只减仓（true）
- `tpTriggerPx`: 止盈触发价
- `tpOrdPx`: 止盈委托价（-1=市价）
- `slTriggerPx`: 止损触发价
- `slOrdPx`: 止损委托价（-1=市价）

### 价格计算精度
- 百分比支持小数（如5.5%）
- 价格四舍五入到2位小数
- 合约张数向下取整到整数

### 错误处理
- API凭证验证
- 输入参数验证
- 持仓存在性验证
- 网络请求超时处理
- 批量操作失败容错

## 📝 使用说明

### 下单时设置

1. **选择交易对**：点击左侧列表选择币种
2. **填写开仓金额**：输入USDT金额
3. **选择杠杆倍数**：3x/5x/10x/20x
4. **设置止盈止损**（可选）：
   - 止盈：如输入5，表示盈利5%时自动平仓
   - 止损：如输入3，表示亏损3%时自动平仓
5. **提交订单**：点击下单按钮
6. **确认信息**：查看确认对话框中的止盈止损设置
7. **查看结果**：下单结果会显示止盈止损设置状态

### 持仓批量设置

1. **查看持仓**：确认右侧有现有持仓
2. **输入百分比**：
   - 止盈：如5（表示5%）
   - 止损：如3（表示3%）
3. **点击应用**：点击"应用到全部持仓"按钮
4. **确认设置**：查看确认对话框中的持仓列表和设置
5. **等待完成**：批量设置需要一定时间（每个持仓约200ms）
6. **查看结果**：显示成功/失败统计和详细结果
7. **验证结果**：持仓列表自动刷新

## 🎯 优势特点

### 1. 统一管理
- ✅ 所有持仓使用相同的止盈止损策略
- ✅ 新开仓位可以立即设置
- ✅ 批量修改现有持仓

### 2. 风险控制
- ✅ 自动止损，控制最大亏损
- ✅ 自动止盈，锁定利润
- ✅ 百分比设置，直观易懂

### 3. 操作便捷
- ✅ 界面直观，一目了然
- ✅ 批量操作，节省时间
- ✅ 实时反馈，结果清晰

### 4. 灵活配置
- ✅ 可以只设置止盈
- ✅ 可以只设置止损
- ✅ 可以两者都设置
- ✅ 支持小数百分比

## 🔄 后续优化建议

### 功能增强
1. **保存策略**：保存常用的止盈止损比例
2. **分别设置**：多单和空单使用不同的比例
3. **条件触发**：基于其他指标触发止盈止损
4. **移动止损**：价格上涨时自动上移止损线

### 界面优化
1. **实时预览**：输入时实时显示触发价格
2. **历史记录**：显示最近使用的止盈止损比例
3. **快捷设置**：预设常用比例（如3%/5%/10%）
4. **分组设置**：按币种分组设置不同比例

## 📚 相关文件

### 前端文件
- `source_code/templates/okx_trading.html`
  - 新增：下单表单止盈止损设置区域
  - 新增：持仓批量设置区域
  - 修改：submitOrder函数（支持止盈止损参数）
  - 新增：batchSetTPSL函数（批量设置）

### 后端文件
- `source_code/app_new.py`
  - 修改：/api/okx-trading/place-order（下单后设置止盈止损）
  - 新增：/api/okx-trading/set-tpsl（设置止盈止损API）

## 🎉 完成状态

- ✅ 下单表单UI完成
- ✅ 持仓批量设置UI完成
- ✅ 前端JavaScript逻辑完成
- ✅ 下单API修改完成
- ✅ 止盈止损API开发完成
- ✅ 价格计算逻辑完成
- ✅ 错误处理完成
- ✅ 日志记录完成
- ✅ Flask重启完成

## 📅 完成时间

2026-02-01 16:03:00

---

**访问链接**: https://5000-ikmpd2up5chrwx4jjjkih-5634da27.sandbox.novita.ai/okx-trading

**功能状态**: ✅ 已上线  
**测试状态**: 待测试  
**文档状态**: ✅ 已完成

OKX交易系统现已支持统一的止盈止损百分比设置功能！
