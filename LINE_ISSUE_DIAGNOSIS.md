# 27币涨跌幅之和线条问题 - 深度诊断与修复

## 问题现象
用户反馈：**刷新页面时，线条会出现一瞬间，然后马上消失**

这个现象说明：
1. ✅ 初始化时（initCharts）配置正确，线条短暂显示
2. ❌ 数据更新时（updateHistoryData）配置有问题，导致线条消失

## 修复历程

### 第一次尝试（提交 310c839）
**修复内容**：添加 `lineStyle` 配置
```javascript
lineStyle: {
    color: '#3B82F6',
    width: 2
}
```
**结果**：❌ 未完全解决

### 第二次尝试（提交 65982bd） - 本次修复
**问题分析**：
1. series[0]（27币涨跌幅之和）没有设置 `z` 属性（默认为0）
2. series[1]（RSI之和）设置了 `z: 10`
3. 可能导致RSI线条或其他scatter系列覆盖了27币线条

**增强配置**：
```javascript
{
    name: '27币涨跌幅之和',
    type: 'line',
    yAxisIndex: 0,
    smooth: true,
    data: cleanedChanges,
    lineStyle: {
        color: '#3B82F6',
        width: 2
    },
    itemStyle: {              // ✅ 新增
        color: '#3B82F6'
    },
    showSymbol: false,        // ✅ 新增 - 不显示数据点
    z: 5,                     // ✅ 新增 - 设置层级
    emphasis: {               // ✅ 新增 - 高亮效果
        focus: 'series'
    },
    areaStyle: { ... }
}
```

**关键改进**：
1. **z: 5** - 确保线条层级在默认层（0）之上，但在RSI线条（z=10）之下
2. **itemStyle** - 明确设置数据点颜色
3. **showSymbol: false** - 只显示线条，不显示数据点符号，减少渲染
4. **emphasis** - 鼠标悬停时高亮整个系列

**统一配置位置**：
1. `initCharts()` - 第4753-4775行
2. `updateHistoryData()` - 第6774-6805行  
3. 空数据处理 - 第8099-8130行

## ECharts层叠顺序说明

### z属性的作用
- **默认值**：0
- **作用范围**：同一坐标系内的series
- **层叠规则**：数值越大越在上层

### 本项目的z设置
```
默认层（z=0）：坐标轴、网格线等
├─ series[0]: 27币涨跌幅之和 (z=5) ← 本次修复
├─ series[1]: RSI之和 (z=10)
├─ 市场情绪scatter (zlevel=15)
└─ 交易标记scatter (zlevel=20)
```

## 验证步骤

### 1. 强制刷新页面
```
Windows/Linux: Ctrl + Shift + R
Mac: Cmd + Shift + R
```

### 2. 检查浏览器Console
应该看到：
```
✅ trendChart.setOption 执行成功
📊 series[0]数据检查: {name: "27币涨跌幅之和", dataLength: 770, ...}
```

### 3. 检查线条显示
- ✅ 蓝色线条清晰可见
- ✅ 线条下方有蓝色渐变填充
- ✅ 线条持续显示，不消失
- ✅ 与RSI灰色虚线同时显示

### 4. 检查页面版本
标题应显示：**27币涨跌幅追踪系统 v3.6.1**

## 技术细节

### ECharts series完整配置
```javascript
{
    // 基础配置
    name: 'xxx',
    type: 'line',
    yAxisIndex: 0,
    smooth: true,
    data: [],
    
    // 样式配置
    lineStyle: { color: '#xxx', width: 2 },
    itemStyle: { color: '#xxx' },
    areaStyle: { ... },
    
    // 显示配置
    showSymbol: false,
    z: 5,
    emphasis: { focus: 'series' },
    
    // 标记配置
    markPoint: { ... },
    markLine: { ... }
}
```

### notMerge参数说明
```javascript
chart.setOption(option, notMerge);
// notMerge=false (默认) - 合并模式，保留旧配置
// notMerge=true - 替换模式，完全替换配置
```

**本项目使用**：`notMerge=false`，确保配置合并

## 可能的其他问题

如果线条仍然不显示，可能是：

### 1. 浏览器缓存
**症状**：看到的是旧版本HTML  
**解决**：硬刷新（Ctrl+Shift+R）或清除浏览器缓存

### 2. 数据问题
**症状**：`cleanedChanges` 数组为空或全为null  
**检查**：Console中查看 `📊 changes数组生成完成: {length: xxx, ...}`

### 3. Y轴范围问题
**症状**：数据超出Y轴范围  
**检查**：数据的min/max值是否在合理范围内

### 4. CSS遮挡
**症状**：其他元素覆盖了canvas  
**检查**：使用浏览器开发者工具检查元素层级

## 调试工具

### Debug页面
访问：`https://9002-id51ob5t89zrt4phphxq8-5634da27.sandbox.novita.ai/static/debug_line.html`

这是一个简化的测试页面，只包含核心的line配置，用于隔离问题。

### Console调试命令
```javascript
// 获取series配置
const series = trendChart.getOption().series;
console.log('Series[0]:', series[0]);

// 获取数据
const data = trendChart.getOption().series[0].data;
console.log('Data length:', data.length);
console.log('Sample data:', data.slice(0, 5));
```

## 部署信息

### 最新提交
- **提交哈希**：65982bd
- **分支**：main
- **提交时间**：2026-02-28
- **版本号**：v3.6.1

### 部署URL
- **主站**：https://9002-id51ob5t89zrt4phphxq8-5634da27.sandbox.novita.ai
- **追踪器**：https://9002-id51ob5t89zrt4phphxq8-5634da27.sandbox.novita.ai/coin-change-tracker
- **Debug页面**：https://9002-id51ob5t89zrt4phphxq8-5634da27.sandbox.novita.ai/static/debug_line.html

### 系统状态
```
✅ Flask应用 - 端口9002，正常运行
✅ PM2服务 - 26个进程全部online
✅ 数据采集 - coin-change-tracker正常
```

## 下一步计划

如果本次修复仍未解决问题，建议：

1. **使用Debug页面验证**
   - 确认简化版本是否正常显示
   - 排除是否是其他代码干扰

2. **检查浏览器兼容性**
   - 尝试使用Chrome/Edge最新版本
   - 检查是否是特定浏览器的渲染问题

3. **逐步排查**
   - 暂时移除scatter系列，看line是否显示
   - 逐个添加series，定位具体冲突点

4. **联系ECharts社区**
   - 如果确认是ECharts bug，提交issue
   - 提供完整的复现代码

---

**修复状态**：✅ 已部署（提交 65982bd）  
**等待验证**：⏳ 用户硬刷新页面后验证  
**优先级**：P0  
**修复日期**：2026-02-28
