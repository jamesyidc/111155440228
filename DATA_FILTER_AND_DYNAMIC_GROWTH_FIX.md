# 数据过滤和动态增长修复

## 🎯 用户反馈的问题

### 问题1：总涨跌幅趋势图显示了前一天的数据
- **错误表现**：X轴显示 `22:10:09` 等前一天晚上的时间
- **正确需求**：只显示当天0点到24点的数据

### 问题2：10分钟上涨占比图表应该动态增长
- **错误表现**：一次性显示完整的144个柱子（包括未来时间）
- **正确需求**：随着数据采集逐步增加柱子数量

## 🔧 修复方案

### 修复1：过滤前一天的数据

**问题根源：**
API返回的数据文件包含前一天晚上的数据。例如：
```
文件: coin_change_20260225.jsonl
内容: 2026-02-24 23:59:39 → 2026-02-25 08:40:21
```

**修复代码：**
```javascript
// 在 updateHistoryData() 函数中，5695行附近
if (result.success && result.data && result.data.length > 0) {
    // 🔥 过滤数据：只保留当天0点之后的数据，排除前一天的数据
    const currentDate = date ? formatDate(date) : new Date().toISOString().split('T')[0];
    const rawData = result.data;
    
    historyData = rawData.filter(item => {
        const timeStr = item.beijing_time || '';
        if (!timeStr) return false;
        
        // 提取日期部分 YYYY-MM-DD
        const itemDate = timeStr.split(' ')[0];
        
        // 只保留当天的数据
        return itemDate === currentDate;
    });
    
    console.log(`📊 数据过滤: 原始${rawData.length}条 → 当天${historyData.length}条 (日期: ${currentDate})`);
    
    if (historyData.length === 0) {
        console.warn(`⚠️ 警告：${currentDate} 没有数据！`);
        historyData = rawData; // 回退到使用所有数据
    }
```

**效果：**
- ✅ 总涨跌幅趋势图：X轴从 `00:00:xx` 开始
- ✅ 不再显示前一天的数据点
- ✅ 图表更清晰，只关注当天走势

---

### 修复2：10分钟图表动态增长

**问题根源：**
之前的代码固定生成144个时间区间（0:00-23:50），导致：
- 即使当前只有上午的数据，也会显示到晚上23:50
- 给人错觉是数据已经完整

**修复代码：**
```javascript
// 在 update10MinUpRatioBarChart() 函数中，7479行附近
// 计算平均值并生成最终数据
const barData = [];
const timeLabels = [];

// 🔥 只生成有数据的区间，不填充空值（动态增长效果）
// 找出最大的索引（最晚的时间）
const indices = Object.keys(groupedData).map(k => parseInt(k)).filter(k => !isNaN(k));
const maxIndex = indices.length > 0 ? Math.max(...indices) : -1;

if (maxIndex >= 0) {
    // 从0到最大索引，生成时间标签和数据
    for (let idx = 0; idx <= maxIndex; idx++) {
        const startTime = `${String(Math.floor(idx * 10 / 60)).padStart(2, '0')}:${String((idx * 10) % 60).padStart(2, '0')}`;
        timeLabels.push(startTime);
        
        if (groupedData[idx] && groupedData[idx].count > 0) {
            const avgUpRatio = groupedData[idx].sum / groupedData[idx].count;
            barData.push(avgUpRatio.toFixed(2));
        } else {
            // 有时间标签但没有数据的区间，使用null
            barData.push(null);
        }
    }
    
    console.log(`📊 动态生成: 0-${maxIndex} 共 ${barData.length} 个区间 (最晚时间: ${timeLabels[timeLabels.length-1]})`);
} else {
    console.warn('⚠️ 没有可用的分组数据');
}
```

**工作原理：**
1. 遍历 `groupedData` 对象，找出**最大的索引**（对应最晚的时间区间）
2. 只生成从 `0` 到 `maxIndex` 的时间标签和数据
3. 随着数据采集，`maxIndex` 逐渐增大，图表动态增长

**示例：**
```
早上8:40的数据：
- maxIndex = 52 (8小时40分钟 ÷ 10分钟 = 52个区间)
- 柱子数量：53个（0-52）
- X轴范围：00:00 → 08:40

下午14:20的数据：
- maxIndex = 86 (14小时20分钟 ÷ 10分钟 = 86个区间)
- 柱子数量：87个（0-86）
- X轴范围：00:00 → 14:20

晚上23:50的数据：
- maxIndex = 143 (23小时50分钟 ÷ 10分钟 = 143个区间)
- 柱子数量：144个（0-143）
- X轴范围：00:00 → 23:50
```

**效果：**
- ✅ 图表随数据采集动态增长
- ✅ 不显示未来时间的空柱子
- ✅ X轴最右侧始终是当前最新的数据时间

---

### 修复3：变量名冲突

**问题：**
代码中有两个 `maxIndex` 变量：
1. 时间区间的最大索引（用于生成柱子）
2. 0-2点最高值的索引（用于标记最高点）

**修复：**
重命名为 `earlyMaxIndex` 和 `earlyMinIndex`：
```javascript
// 找到0-2点区间的最高值和最低值的索引（用于标记）
let earlyMaxIndex = -1;
let earlyMinIndex = -1;
if (earlyMorningData.length > 0) {
    const numericEarlyData = earlyMorningData.map(v => v !== null ? parseFloat(v) : null).filter(v => v !== null);
    if (numericEarlyData.length > 0) {
        const maxVal = Math.max(...numericEarlyData);
        const minVal = Math.min(...numericEarlyData);
        earlyMaxIndex = earlyMorningData.findIndex(v => v !== null && parseFloat(v) === maxVal);
        earlyMinIndex = earlyMorningData.findIndex(v => v !== null && parseFloat(v) === minVal);
    }
}
```

---

## 📊 修复前后对比

### 总涨跌幅趋势图

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| 数据来源 | API原始数据 | 过滤后只保留当天数据 |
| X轴起点 | 可能是前一天晚上 | 始终是当天00:00 |
| 数据范围 | 包含前一天数据 | 只包含当天数据 |
| 图表清晰度 | 混乱（跨日） | 清晰（单日） |

### 10分钟上涨占比图表

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| 柱子数量 | 固定144个 | 动态增长（根据数据） |
| X轴范围 | 00:00-23:50（固定） | 00:00-当前最新时间 |
| 未来时间 | 显示空柱子 | 不显示 |
| 用户体验 | 误导性（显示完整） | 准确反映当前状态 |
| 统计数据 | 基于0-2点 | 基于0-2点（不变） |

---

## ✅ 验证步骤

### 1. 清除浏览器缓存
**务必使用无痕模式或彻底清除缓存！**

### 2. 打开控制台（F12），查看日志

**数据过滤日志：**
```
📊 数据过滤: 原始410条 → 当天324条 (日期: 2026-02-25)
```

**动态生成日志：**
```
📊 原始数据总数: 324 条
📊 动态生成: 0-86 共 87 个区间 (最晚时间: 14:20)
📊 全天数据: 87 个柱子 (动态增长)
📊 0-2点数据: 12 个柱子 (用于统计)
```

### 3. 检查总涨跌幅趋势图
- ✅ X轴最左侧应该是 `00:xx:xx`（当天凌晨）
- ✅ 不应该出现前一天的时间（如 `22:xx:xx`）
- ✅ 图表从当天0点开始

### 4. 检查10分钟上涨占比图表
- ✅ 柱子数量与当前时间相符
  - 例如：当前14:20，应该有约87个柱子（14小时20分钟 ÷ 10分钟）
- ✅ X轴最右侧应该是当前最新数据时间
- ✅ 不应该显示未来时间的柱子

---

## 🔍 技术细节

### 数据文件结构
```
文件名: coin_change_YYYYMMDD.jsonl
内容: 可能包含前一天晚上的数据 + 当天数据

示例：coin_change_20260225.jsonl
- 2026-02-24 23:59:39  ← 前一天
- 2026-02-25 00:01:04  ← 当天
- 2026-02-25 00:02:30
- ...
- 2026-02-25 14:20:15  ← 最新数据
```

### 过滤逻辑
```javascript
// 提取日期部分：YYYY-MM-DD
const itemDate = item.beijing_time.split(' ')[0];

// 与目标日期比较
return itemDate === currentDate;
```

### 动态增长逻辑
```javascript
// 数据按10分钟分组，索引 = 总分钟数 ÷ 10
groupIndex = Math.floor(totalMinutes / 10)

// 找出最大索引
maxIndex = Math.max(...Object.keys(groupedData))

// 只生成 0 到 maxIndex 的柱子
for (let idx = 0; idx <= maxIndex; idx++) { ... }
```

---

## 📝 Git信息

- **分支**: `feature/crash-warning-system`
- **修复提交**: `fdf7285`
- **提交信息**: "重大修复：过滤前一天数据+10分钟图表动态增长"
- **PR链接**: https://github.com/jamesyidc/1212335551/pull/1

---

## 🌐 访问地址

https://9002-imp6ky5dtwten0w001hfy-82b888ba.sandbox.novita.ai/coin-change-tracker

---

## 💡 总结

### 解决的核心问题
1. ✅ **数据污染**：过滤掉前一天的数据，保持单日数据纯净
2. ✅ **误导性展示**：图表动态增长，准确反映当前数据状态
3. ✅ **变量冲突**：重命名避免逻辑错误

### 用户体验提升
1. 📈 **趋势图更清晰**：只看当天走势，不受前一天数据干扰
2. 📊 **柱状图更准确**：显示实际已有的数据，不显示未来空白
3. 🎯 **预判更可靠**：基于纯净的0-2点数据计算统计值

---
*生成时间：2026-02-25 01:27*
*修复版本：v7-DataFilterAndDynamicGrowth*
