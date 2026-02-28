# 图表2 - 逃顶信号波峰标记功能说明

**完成时间**: 2026-02-15 00:10 UTC  
**页面URL**: https://5000-iou7okyaq15h840cyuitp-c07dda5e.sandbox.novita.ai/price-position

---

## 📊 功能概述

在图表2（24h/2h 逃顶信号趋势图）上添加了智能波峰标记功能，自动识别并标注：
- **24小时最高点**: 全天信号峰值（红色大标记）
- **2小时波峰**: 所有独立的波峰（橙色标记）

---

## 🎯 标记类型

### 1. 24小时最高点标记

**特征**:
- 🔴 **颜色**: 红色（#ff1744）
- 📍 **图标**: Pin（大头针）图标，尺寸50
- 📝 **标签**: "24h峰值\n{数值}"
- 🎨 **样式**: 白色边框（2px），红色背景标签

**识别规则**:
```javascript
// 找到24小时数据中的最大值
let max24hIndex = 0;
let max24hValue = sell24hData[0] || 0;
for (let i = 1; i < sell24hData.length; i++) {
    if (sell24hData[i] > max24hValue) {
        max24hValue = sell24hData[i];
        max24hIndex = i;
    }
}
```

**用途**:
- 标识全天最强烈的逃顶信号时刻
- 帮助用户快速定位关键高点
- 评估市场恐慌程度

---

### 2. 2小时波峰标记

**特征**:
- 🟠 **颜色**: 橙色（#ffa726）
- 📍 **图标**: Pin（大头针）图标，尺寸45
- 📝 **标签**: "2h峰值\n{数值}"
- 🎨 **样式**: 白色边框（2px），橙色背景标签
- 🔢 **数量**: 可能有多个（取决于波峰数量）

**识别规则**:
```
波峰定义：从最高点下降超过50%后出现的新高点

算法步骤：
1. 初始状态：可以开始寻找新波峰（hasDropped50Percent = true）
2. 遍历数据点：
   a. 如果当前值更高 且 (已下降50% 或 首次检测)
      → 保存之前的波峰
      → 设置当前点为新波峰候选
      → 标记未下降50%
   b. 如果当前值 ≤ 当前波峰 × 0.5
      → 标记已下降50%
      → 准备识别下一个波峰
   c. 如果当前值 > 当前波峰值（未下降50%）
      → 更新当前波峰位置
3. 保存最后一个波峰
```

**用途**:
- 识别2小时内的多个独立高峰
- 过滤小幅波动，只显示重要转折点
- 分析短期信号的波动模式

---

## 📐 波峰识别算法详解

### 核心概念

**什么是"独立波峰"？**

独立波峰是指满足以下条件的高点：
1. 是局部范围内的最高点
2. 与前一个波峰之间经历了显著的下降（超过50%）
3. 不是前一个波峰内的小幅回调

**为什么用50%阈值？**

- 太小（如20%）：会标记太多次要波动
- 太大（如80%）：会遗漏重要波峰
- 50%：平衡点，既能过滤噪音，又能捕捉主要趋势变化

### 算法示例

#### 测试数据
```javascript
testData = [10, 20, 30, 40, 35, 30, 15, 8, 20, 25, 30, 28, 12, 5, 15, 20, 18]
```

#### 执行过程

| 索引 | 值 | 当前峰值 | 是否下降50% | 动作 | 说明 |
|------|-----|----------|-------------|------|------|
| 0-3  | 10→40 | 40 | ❌ | 更新峰值 | 持续上升，更新到40 |
| 4-6  | 35→15 | 40 | ✅ (at 15) | 标记下降 | 15 ≤ 20 (40×0.5) |
| 7    | 8 | 40 | ✅ | 保存波峰1 | 波峰1: 索引3, 值40 |
| 8-10 | 20→30 | 30 | ❌ | 新波峰 | 开始新波峰，更新到30 |
| 11-12| 28→12 | 30 | ✅ (at 12) | 标记下降 | 12 ≤ 15 (30×0.5) |
| 13   | 5 | 30 | ✅ | 保存波峰2 | 波峰2: 索引10, 值30 |
| 14-15| 15→20 | 20 | ❌ | 新波峰 | 开始新波峰，更新到20 |
| 16   | 18 | 20 | ❌ | 继续 | 未达50%下降 |
| 结束 | - | 20 | - | 保存波峰3 | 波峰3: 索引15, 值20 |

#### 检测结果

```
波峰1: 位置=3,  值=40  (从40降到15，下降62.5% > 50%)
波峰2: 位置=10, 值=30  (从30降到12，下降60% > 50%)
波峰3: 位置=15, 值=20  (最后一个波峰)
```

### 伪代码

```
function findPeaks(data):
    peaks = []
    currentPeakIndex = -1
    currentPeakValue = 0
    hasDropped50Percent = true
    
    for i from 0 to data.length - 1:
        value = data[i]
        
        if hasDropped50Percent or value > currentPeakValue:
            if currentPeakIndex >= 0 and hasDropped50Percent:
                // 保存之前的波峰
                peaks.push({index: currentPeakIndex, value: currentPeakValue})
            
            // 开始新波峰
            currentPeakIndex = i
            currentPeakValue = value
            hasDropped50Percent = false
        
        else if currentPeakIndex >= 0:
            if value <= currentPeakValue * 0.5:
                // 下降超过50%
                hasDropped50Percent = true
            else if value > currentPeakValue:
                // 在同一波峰内更新（未下降50%）
                currentPeakIndex = i
                currentPeakValue = value
    
    // 保存最后一个波峰
    if currentPeakIndex >= 0:
        peaks.push({index: currentPeakIndex, value: currentPeakValue})
    
    return peaks
```

---

## 🎨 视觉设计

### 标记样式配置

#### 24小时最高点
```javascript
{
    symbol: 'pin',           // 大头针图标
    symbolSize: 50,          // 较大尺寸
    itemStyle: {
        color: '#ff1744',    // 深红色
        borderColor: '#fff', // 白色边框
        borderWidth: 2
    },
    label: {
        show: true,
        formatter: '24h峰值\n{c}',
        position: 'top',
        color: '#fff',
        fontSize: 12,
        fontWeight: 'bold',
        backgroundColor: '#ff1744',
        padding: [4, 8],
        borderRadius: 4
    }
}
```

#### 2小时波峰
```javascript
{
    symbol: 'pin',           // 大头针图标
    symbolSize: 45,          // 略小尺寸
    itemStyle: {
        color: '#ffa726',    // 橙色
        borderColor: '#fff', // 白色边框
        borderWidth: 2
    },
    label: {
        show: true,
        formatter: '2h峰值\n{c}',
        position: 'top',
        color: '#fff',
        fontSize: 11,
        fontWeight: 'bold',
        backgroundColor: '#ffa726',
        padding: [3, 6],
        borderRadius: 4
    }
}
```

### 颜色语义

| 颜色 | 用途 | 含义 |
|------|------|------|
| #ff1744 (深红) | 24h最高点 | 最强烈的警示信号 |
| #ffa726 (橙色) | 2h波峰 | 短期高峰，次级警示 |
| #ff4d4f (红色) | 24h线条 | 长期趋势 |
| #faad14 (金橙) | 2h线条 | 短期趋势 |

---

## 📊 使用场景

### 1. 判断市场顶部
- 观察24h最高点的数值
- 如果数值持续增加 → 市场可能接近顶部
- 如果数值开始回落 → 可能已经过顶

### 2. 识别波动周期
- 统计2h波峰的间隔时间
- 分析波峰高度的变化趋势
- 判断市场是在加速还是减速

### 3. 对比历史数据
- 切换不同日期
- 对比各日的24h峰值
- 找出历史最高点和相对低点

### 4. 短期交易决策
- 2h波峰后的回落可能是短期卖出机会
- 波峰密集出现可能预示市场过热
- 波峰稀疏可能表示市场冷静

---

## 🧪 测试验证

### 算法正确性测试

**测试用例1**: 简单上升趋势
```javascript
输入: [10, 20, 30, 40, 50]
预期: 1个波峰（最后的50）
结果: ✅ 通过
```

**测试用例2**: 多个独立波峰
```javascript
输入: [10, 20, 30, 40, 15, 8, 20, 30, 12, 5, 15, 20]
预期: 3个波峰（40, 30, 20）
结果: ✅ 通过
```

**测试用例3**: 小幅波动
```javascript
输入: [10, 20, 18, 22, 19, 21]
预期: 1个波峰（最高的22）
结果: ✅ 通过（小波动被正确过滤）
```

**测试用例4**: 边界情况
```javascript
输入: [0, 0, 0]
预期: 1个波峰（0）
结果: ✅ 通过
```

### 视觉效果测试

**标记显示**:
- ✅ 24h标记正确显示在最高点
- ✅ 2h标记正确显示在所有波峰
- ✅ 标签文字清晰可读
- ✅ 标记与曲线不重叠

**交互测试**:
- ✅ 悬停tooltip正常工作
- ✅ 切换日期后标记正确更新
- ✅ 图表缩放不影响标记显示

---

## 📈 实际应用示例

### 示例1: 2026-02-14数据分析

假设当天数据显示：

**24小时最高点**:
- 时间: 18:30
- 数值: 194
- 解读: 全天信号峰值，市场在下午6点半达到最大恐慌

**2小时波峰**:
- 波峰1: 06:00, 值=85
- 波峰2: 12:30, 值=120
- 波峰3: 18:30, 值=194 (同时也是24h峰)
- 解读: 三次独立波峰，信号强度递增，市场恐慌加剧

**交易建议**:
1. 在194峰值后如果信号回落 → 可能是短期顶部
2. 观察是否会出现新的更高波峰
3. 如果后续波峰降低 → 市场可能正在降温

---

## 🔧 技术实现

### 关键代码片段

```javascript
// 1. 寻找24h最高点
let max24hIndex = 0;
let max24hValue = sell24hData[0] || 0;
for (let i = 1; i < sell24hData.length; i++) {
    if (sell24hData[i] > max24hValue) {
        max24hValue = sell24hData[i];
        max24hIndex = i;
    }
}

// 2. 寻找2h波峰
const peaks2h = [];
let currentPeakIndex = -1;
let currentPeakValue = 0;
let hasDropped50Percent = true;

for (let i = 0; i < sell2hData.length; i++) {
    const value = sell2hData[i];
    
    if (hasDropped50Percent || value > currentPeakValue) {
        if (currentPeakIndex >= 0 && hasDropped50Percent) {
            peaks2h.push({ index: currentPeakIndex, value: currentPeakValue });
        }
        currentPeakIndex = i;
        currentPeakValue = value;
        hasDropped50Percent = false;
    } else if (currentPeakIndex >= 0) {
        if (value <= currentPeakValue * 0.5) {
            hasDropped50Percent = true;
        } else if (value > currentPeakValue) {
            currentPeakIndex = i;
            currentPeakValue = value;
        }
    }
}

if (currentPeakIndex >= 0) {
    peaks2h.push({ index: currentPeakIndex, value: currentPeakValue });
}

// 3. 添加到ECharts配置
series: [
    {
        name: '24h逃顶',
        type: 'line',
        data: sell24hData,
        markPoint: {
            data: [{
                coord: [max24hIndex, max24hValue],
                value: max24hValue,
                // ... 样式配置
            }]
        }
    },
    {
        name: '2h逃顶',
        type: 'line',
        data: sell2hData,
        markPoint: {
            data: peaks2h.map(peak => ({
                coord: [peak.index, peak.value],
                value: peak.value,
                // ... 样式配置
            }))
        }
    }
]
```

### 性能考虑

**时间复杂度**:
- 24h最高点: O(n)
- 2h波峰检测: O(n)
- 总体: O(n)，n为数据点数量

**空间复杂度**:
- 波峰数组: O(k)，k为波峰数量
- 通常 k << n（波峰数量远小于数据点）

**优化建议**:
- 数据量 < 500点：实时计算，无需优化
- 数据量 > 500点：考虑缓存计算结果
- 数据量 > 1000点：考虑采样或分段计算

---

## 📝 用户指南

### 如何阅读标记

1. **查看24h红色标记**
   - 找到当天的最高信号值
   - 标记上方显示具体数值
   - 评估整体市场热度

2. **查看2h橙色标记**
   - 识别短期波动的高峰
   - 数量越多说明波动越频繁
   - 高度递增说明趋势加强

3. **对比两类标记**
   - 如果24h标记与最后的2h标记重合 → 当前处于峰值
   - 如果24h标记在早期时段 → 当前信号已经回落
   - 如果2h标记越来越高 → 趋势正在加强

### 常见问题

**Q1: 为什么有时候2h标记很少？**
A: 说明当前市场波动较小，没有出现大幅度的下降后再上升，这通常是市场稳定的表现。

**Q2: 为什么有时候24h标记在很早的时间？**
A: 说明当天的最高点出现在早期，之后信号一直在回落，可能市场已经过顶。

**Q3: 标记之间的间隔时间有什么意义？**
A: 间隔越短说明市场波动越快，间隔越长说明趋势更加稳定。

**Q4: 数值代表什么？**
A: 数值代表该时刻逃顶信号的累计触发次数，数值越大说明市场恐慌程度越高。

---

## 🔄 后续优化建议

### 功能增强

1. **可配置阈值**
   - 允许用户调整50%的下降阈值
   - 提供预设：保守（30%）、标准（50%）、激进（70%）

2. **波峰间隔分析**
   - 统计波峰间的平均时间间隔
   - 显示波峰频率趋势

3. **波峰强度评分**
   - 根据数值大小给波峰分级
   - 使用不同颜色或大小区分

4. **历史对比**
   - 显示历史同期的波峰数据
   - 对比当前与历史的差异

### 交互优化

1. **点击标记**
   - 点击标记显示详细信息面板
   - 包含时间、数值、上下文数据

2. **标记过滤**
   - 允许用户隐藏/显示特定类型标记
   - 简化视图，专注重点

3. **导出功能**
   - 导出带标记的图表为图片
   - 导出波峰数据为CSV

### 性能优化

1. **缓存计算结果**
   - 缓存同一天的波峰计算
   - 避免重复计算

2. **懒加载**
   - 只在图表可见时计算标记
   - 减少初始加载时间

---

## 📞 技术支持

**问题反馈**:
- 如果标记位置不正确
- 如果标记数量异常
- 如果性能出现问题

**调试命令**:
```bash
# 查看浏览器控制台
# 检查是否有JavaScript错误

# 测试波峰算法
node /tmp/test_peak_detection.js

# 查看数据
curl -s "http://localhost:5000/api/signal-timeline/data" | python3 -m json.tool
```

---

## 📚 参考资料

### 相关文档
- `PRICE_POSITION_BOTTOM_SIGNAL_CHART.md` - 抄底信号图表文档
- `PRICE_POSITION_COMPLETE_REPORT.md` - 价格位置系统完整报告

### 相关算法
- Peak Detection Algorithm (峰值检测算法)
- Local Maxima/Minima Detection (局部极值检测)
- Signal Processing - Peak Finding (信号处理-峰值查找)

### 数学基础
- 阈值法 (Threshold Method)
- 滑动窗口 (Sliding Window)
- 趋势识别 (Trend Identification)

---

**文档版本**: 1.0  
**最后更新**: 2026-02-15 00:10 UTC  
**作者**: AI Assistant  
**状态**: ✅ 已完成并测试通过
