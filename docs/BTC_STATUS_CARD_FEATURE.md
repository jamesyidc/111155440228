# BTC 当日涨跌幅状态框功能

## 功能概述

在 27 币涨跌幅追踪系统中新增了 **BTC 当日涨跌幅状态框**，用于直观展示 BTC 的当前涨跌幅和市场状态。

## 功能特点

### 1. 实时显示
- 显示 BTC 当前涨跌幅（百分比）
- 根据涨跌幅自动分类市场状态
- 与最新数据同步更新

### 2. 六级状态分类

根据 BTC 涨跌幅自动分类为 6 个状态：

| 状态 | 涨跌幅范围 | 颜色标识 | 说明 |
|------|-----------|---------|------|
| **主跌** | 跌幅 > 3% | 红色 (red-600) | 市场深度下跌，风险极高 |
| **大幅下跌** | -3% ~ -1.5% | 橙色 (orange-600) | 市场显著下跌，需警惕 |
| **小幅震荡偏空** | -1.5% ~ 0% | 黄色 (yellow-600) | 市场小幅震荡，偏空头 |
| **小幅震荡偏多** | 0% ~ 1.5% | 蓝色 (blue-600) | 市场小幅震荡，偏多头 |
| **大幅上涨** | 1.5% ~ 3% | 绿色 (green-600) | 市场显著上涨，动能良好 |
| **主升** | 涨幅 > 3% | 翠绿色 (emerald-600) | 市场强势上涨，动能强劲 |

### 3. 视觉设计

- **卡片背景**：根据状态使用对应的浅色背景（如 `bg-blue-50`）
- **边框颜色**：使用 2px 粗边框，颜色与状态匹配
- **数值显示**：大号字体（text-3xl）显示涨跌幅，带正负号
- **状态文字**：清晰的状态标签（text-lg）
- **动画效果**：平滑过渡（transition-all duration-300）

### 4. 状态说明

卡片右侧包含完整的状态分类标准说明，方便用户理解：
- 6 个状态分类及其对应的涨跌幅范围
- 每个状态使用圆形色块标识
- 紧凑的网格布局，易于快速参考

## 技术实现

### 前端 HTML 结构

```html
<!-- BTC 当日涨跌幅状态框 -->
<div class="mb-6">
    <div class="bg-white rounded-lg shadow-lg p-6">
        <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-bold flex items-center">
                <i class="fab fa-bitcoin text-orange-500 mr-2"></i>
                BTC 当日涨跌幅状态
            </h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- BTC 涨跌幅 -->
            <div id="btcChangeCard" class="p-4 rounded-lg border-2 transition-all duration-300">
                <div class="text-sm text-gray-600 mb-1">BTC 当前涨跌幅</div>
                <div id="btcChange" class="text-3xl font-bold mb-2">--</div>
                <div id="btcStatus" class="text-lg font-semibold">--</div>
            </div>
            
            <!-- 状态说明 -->
            <div class="col-span-1 md:col-span-1 lg:col-span-2 bg-gray-50 p-4 rounded-lg">
                <!-- 状态分类标准 -->
            </div>
        </div>
    </div>
</div>
```

### JavaScript 更新函数

```javascript
// 更新BTC当日涨跌幅状态
function updateBTCStatus(changes) {
    // 查找BTC数据
    let btcChange = null;
    for (const [symbol, data] of Object.entries(changes)) {
        if (symbol.includes('BTC')) {
            btcChange = data.change_pct || 0;
            break;
        }
    }
    
    if (btcChange === null) {
        document.getElementById('btcChange').textContent = '--';
        document.getElementById('btcStatus').textContent = '暂无数据';
        return;
    }
    
    // 更新涨跌幅显示
    const btcChangeEl = document.getElementById('btcChange');
    btcChangeEl.textContent = `${btcChange > 0 ? '+' : ''}${btcChange.toFixed(2)}%`;
    
    // 根据涨跌幅确定状态和样式
    let status = '';
    let bgColor = '';
    let textColor = '';
    let borderColor = '';
    
    if (btcChange < -3) {
        status = '主跌';
        bgColor = 'bg-red-50';
        textColor = 'text-red-600';
        borderColor = 'border-red-600';
    } else if (btcChange >= -3 && btcChange < -1.5) {
        status = '大幅下跌';
        bgColor = 'bg-orange-50';
        textColor = 'text-orange-600';
        borderColor = 'border-orange-500';
    } else if (btcChange >= -1.5 && btcChange < 0) {
        status = '小幅震荡偏空';
        bgColor = 'bg-yellow-50';
        textColor = 'text-yellow-600';
        borderColor = 'border-yellow-400';
    } else if (btcChange >= 0 && btcChange < 1.5) {
        status = '小幅震荡偏多';
        bgColor = 'bg-blue-50';
        textColor = 'text-blue-600';
        borderColor = 'border-blue-400';
    } else if (btcChange >= 1.5 && btcChange < 3) {
        status = '大幅上涨';
        bgColor = 'bg-green-50';
        textColor = 'text-green-600';
        borderColor = 'border-green-500';
    } else {
        status = '主升';
        bgColor = 'bg-emerald-50';
        textColor = 'text-emerald-600';
        borderColor = 'border-emerald-600';
    }
    
    // 更新状态显示
    document.getElementById('btcStatus').textContent = status;
    document.getElementById('btcStatus').className = `text-lg font-semibold ${textColor}`;
    btcChangeEl.className = `text-3xl font-bold mb-2 ${textColor}`;
    
    // 更新卡片样式
    const btcCard = document.getElementById('btcChangeCard');
    btcCard.className = `p-4 rounded-lg border-2 transition-all duration-300 ${bgColor} ${borderColor}`;
}
```

### 调用时机

在 `updateLatestData()` 函数中，更新详细表格后调用：

```javascript
// 更新详细表格（使用最新的或缓存的RSI数据）
const rsiValuesToUse = (data.rsi_values && Object.keys(data.rsi_values).length > 0) 
    ? data.rsi_values 
    : lastRSIData.rsi_values;
updateDetailTable(data.changes, rsiValuesToUse);

// 更新BTC当日涨跌幅状态
updateBTCStatus(data.changes);
```

## 使用场景

### 1. 快速判断市场状态
通过 BTC 的涨跌幅和状态标签，快速了解当前市场的整体趋势。

### 2. 辅助交易决策
- **主跌**：考虑减仓或观望
- **大幅下跌**：谨慎操作，等待止跌信号
- **小幅震荡偏空**：短期调整，观察支撑位
- **小幅震荡偏多**：小幅上涨，可适度跟进
- **大幅上涨**：动能良好，可持有或加仓
- **主升**：强势上涨，注意获利回吐风险

### 3. 结合其他指标
- 与 **27币涨跌幅之和** 结合，判断市场整体强弱
- 与 **RSI之和** 结合，判断超买超卖状态
- 与 **上涨占比** 结合，判断市场共振情况

## 示例数据

### 当前数据示例
```
BTC当前价: 67669.9
基准价: 67349.9
涨跌幅: +0.48%
状态: 小幅震荡偏多 (蓝色)
```

### 不同状态示例

1. **主跌示例**
   - 涨跌幅: -5.2%
   - 状态: 主跌 (红色)
   - 说明: 市场深度下跌，风险极高

2. **大幅下跌示例**
   - 涨跌幅: -2.3%
   - 状态: 大幅下跌 (橙色)
   - 说明: 市场显著下跌，需警惕

3. **小幅震荡偏空示例**
   - 涨跌幅: -0.8%
   - 状态: 小幅震荡偏空 (黄色)
   - 说明: 市场小幅震荡，偏空头

4. **小幅震荡偏多示例**
   - 涨跌幅: +0.48%
   - 状态: 小幅震荡偏多 (蓝色)
   - 说明: 市场小幅震荡，偏多头

5. **大幅上涨示例**
   - 涨跌幅: +2.1%
   - 状态: 大幅上涨 (绿色)
   - 说明: 市场显著上涨，动能良好

6. **主升示例**
   - 涨跌幅: +5.8%
   - 状态: 主升 (翠绿色)
   - 说明: 市场强势上涨，动能强劲

## 更新日志

### V2.2 (2026-02-18)
- ✅ 新增 BTC 当日涨跌幅状态框
- ✅ 实现六级状态分类系统
- ✅ 添加状态说明和视觉标识
- ✅ 实时更新 BTC 状态
- ✅ 添加 `updateBTCStatus()` 函数

## 文件修改

- **templates/coin_change_tracker.html**
  - 新增 BTC 状态框 HTML 结构
  - 新增 `updateBTCStatus()` 函数
  - 在 `updateLatestData()` 中调用状态更新

## 访问地址

https://9002-ixuizzbk8b8iyhwfxb9rl-5634da27.sandbox.novita.ai/coin-change-tracker

## 后续优化建议

1. **历史数据对比**
   - 添加 24 小时前的 BTC 涨跌幅对比
   - 显示日内最高/最低涨跌幅

2. **状态持续时间**
   - 记录每个状态持续的时间
   - 提供状态切换历史

3. **关联分析**
   - BTC 状态与 27 币涨跌幅之和的相关性
   - BTC 状态与 RSI 之和的相关性

4. **预警功能**
   - 进入"主跌"或"主升"状态时触发预警
   - 状态快速切换时提醒用户

5. **多币种支持**
   - 扩展到 ETH、BNB 等主流币种
   - 显示多个币种的状态对比

## 维护说明

- 状态阈值设置在 `updateBTCStatus()` 函数中
- 如需调整阈值，修改对应的条件判断即可
- 颜色配置使用 Tailwind CSS 类，统一视觉风格
- 每分钟自动更新一次（与最新数据同步）
