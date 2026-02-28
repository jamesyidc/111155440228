# Panic页面1小时爆仓图表阈值线功能报告

## 实现日期
2026-02-06

## 需求描述

用户要求在panic页面的"1小时爆仓金额曲线图"中添加三条虚线标记重要阈值：
1. **5000万美元** - 警戒线
2. **1亿美元（10000万）** - 危险线
3. **1.5亿美元（15000万）** - 极度危险线

这些阈值线可以帮助用户快速识别市场爆仓情况的严重程度。

## 实现效果

### 阈值线配置

#### 1. 5000万阈值线 ⚠️
- **颜色**: `#fbbf24`（黄色）
- **样式**: 虚线，线宽2px
- **标签**: "⚠️ 5000万"
- **含义**: 警戒水平，市场开始出现明显波动

#### 2. 1亿阈值线 🔥
- **颜色**: `#f97316`（橙色）
- **样式**: 虚线，线宽2px
- **标签**: "🔥 1亿"
- **含义**: 危险水平，市场剧烈波动

#### 3. 1.5亿阈值线 💥
- **颜色**: `#ef4444`（红色）
- **样式**: 虚线，线宽2px
- **标签**: "💥 1.5亿"
- **含义**: 极度危险水平，市场恐慌性抛售

#### 4. 平均值线（保留原有）
- **颜色**: `#6b7280`（灰色）
- **样式**: 虚线，线宽1px
- **标签**: "平均: {value}万"
- **含义**: 当前24小时数据的平均值

### 视觉设计

#### 标签样式
```javascript
label: {
    position: 'end',           // 标签在线的末端
    fontSize: 11,              // 字体大小
    color: '#fff',             // 白色文字
    backgroundColor: 'rgba(0, 0, 0, 0.6)',  // 半透明黑色背景
    padding: [4, 8],           // 内边距
    borderRadius: 3            // 圆角
}
```

#### 颜色渐变
- 🟡 黄色（5000万）→ 🟠 橙色（1亿）→ 🔴 红色（1.5亿）
- 从警戒到危险再到极度危险，颜色逐渐加深
- 与Emoji图标颜色语义一致

### 核心代码

```javascript
markLine: {
    silent: true,
    symbol: 'none',
    label: {
        position: 'end',
        fontSize: 11,
        color: '#fff',
        backgroundColor: 'rgba(0, 0, 0, 0.6)',
        padding: [4, 8],
        borderRadius: 3
    },
    lineStyle: {
        type: 'dashed',
        width: 2
    },
    data: [
        { 
            yAxis: avgAmount,
            label: {
                formatter: '平均: {c}万'
            },
            lineStyle: {
                color: '#6b7280',
                width: 1
            }
        },
        { 
            yAxis: 5000,
            label: {
                formatter: '⚠️ 5000万',
                color: '#fbbf24'
            },
            lineStyle: {
                color: '#fbbf24',
                width: 2
            }
        },
        { 
            yAxis: 10000,
            label: {
                formatter: '🔥 1亿',
                color: '#f97316'
            },
            lineStyle: {
                color: '#f97316',
                width: 2
            }
        },
        { 
            yAxis: 15000,
            label: {
                formatter: '💥 1.5亿',
                color: '#ef4444'
            },
            lineStyle: {
                color: '#ef4444',
                width: 2
            }
        }
    ]
}
```

## 应用场景

### 场景1: 正常市场（<5000万）
```
当前1H爆仓: 2000万美元
图表显示: 数据线在所有阈值线下方
状态: ✅ 市场平静
```

### 场景2: 警戒水平（5000万-1亿）
```
当前1H爆仓: 7500万美元
图表显示: 数据线穿过黄色⚠️警戒线，但未达橙色危险线
状态: ⚠️ 市场波动加剧，需要关注
```

### 场景3: 危险水平（1亿-1.5亿）
```
当前1H爆仓: 1.2亿美元
图表显示: 数据线穿过橙色🔥危险线，接近红色极度危险线
状态: 🔥 市场剧烈波动，高度警惕
```

### 场景4: 极度危险（>1.5亿）
```
当前1H爆仓: 2亿美元
图表显示: 数据线突破红色💥极度危险线
状态: 💥 市场恐慌性抛售，极度危险
关联: 可能触发事件9"超强爆仓之后的主跌"
```

## 与重大事件系统的关联

### 事件3: 强空头爆仓
- **触发条件**: 1H爆仓 >= 3000万
- **图表显示**: 接近或超过5000万警戒线时可能触发

### 事件4: 弱空头爆仓
- **触发条件**: 1H爆仓 >= 3000万（但未持续新高）
- **图表显示**: 在5000万以下波动

### 事件9: 超强爆仓之后的主跌
- **触发条件**: 1H爆仓 >= **1.5亿美元（15000万）**
- **图表显示**: 突破红色💥极度危险线时触发
- **阈值对应**: 1.5亿阈值线直接对应事件9触发条件！

## 用户体验提升

### ✅ 快速识别
- 一眼看出当前爆仓水平相对于关键阈值的位置
- 无需计算，直观判断市场危险程度

### ✅ 历史对比
- 可以看到历史数据中何时触达各个阈值
- 分析市场波动的频率和强度

### ✅ 趋势预警
- 当数据线接近阈值时提前预警
- 帮助用户提前做好应对准备

### ✅ 决策支持
- 结合阈值线和实时数据做交易决策
- 例如：接近1.5亿时考虑开空单（事件9策略）

## 技术实现细节

### ECharts markLine配置
- `silent: true` - 不响应鼠标事件
- `symbol: 'none'` - 不显示线条端点图标
- `lineStyle.type: 'dashed'` - 虚线样式
- `lineStyle.width: 2` - 线宽2px（平均线为1px）

### 颜色选择理由
- **黄色 #fbbf24**: 警告色，Tailwind的amber-400
- **橙色 #f97316**: 危险色，Tailwind的orange-500
- **红色 #ef4444**: 极度危险色，Tailwind的red-500
- 颜色递进符合用户认知习惯

### 标签定位
- `position: 'end'` - 标签在Y轴右侧
- 避免遮挡数据曲线
- 方便用户阅读

## 测试验证

### 访问页面
https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/panic

### 验证要点
1. ✅ 页面正常加载
2. ✅ 图表显示四条横向虚线
3. ✅ 标签文字清晰可读
4. ✅ 颜色区分明显
5. ✅ 不影响原有的最大值标记点

### 浏览器Console测试
```javascript
// 检查markLine数据
const chart = echarts.getInstanceByDom(document.getElementById('liquidationChart'));
const option = chart.getOption();
console.log('markLine数据:', option.series[0].markLine.data);
// 应该看到4个对象：平均值、5000、10000、15000
```

## 与现有功能的兼容性

### ✅ 保留原有功能
- **平均值线**: 继续显示，样式调整为更细的灰色线
- **最大值标记点**: 红色pin图标标记24小时内最大值
- **Tooltip**: 鼠标悬停显示详细信息
- **数据分页**: 24小时数据分页显示

### ✅ 增强视觉效果
- 多条阈值线不会相互遮挡
- 标签背景避免与线条混淆
- 颜色层次清晰，易于区分

## 数据示例

### 当前市场状态（2026-02-06）
根据最新数据：
```
1小时爆仓金额: 3132.13万美元
阈值对比:
- 5000万警戒线: ❌ 未达到（62.6%）
- 1亿危险线: ❌ 未达到（31.3%）
- 1.5亿极度危险线: ❌ 未达到（20.9%）
状态: ✅ 市场相对平静
```

### 历史高点参考
根据用户提供的截图（2月6日数据）：
```
历史最高点: 约4200万美元
阈值对比:
- 5000万警戒线: ❌ 未达到（84%）
- 1亿危险线: ❌ 未达到（42%）
- 1.5亿极度危险线: ❌ 未达到（28%）
说明: 即使在高点时期，也未达到5000万警戒线
```

## Git 提交记录

```
commit 675d8b0
feat: 为panic页面1小时爆仓图表添加阈值线

- 添加5000万阈值线（黄色虚线，⚠️标识）
- 添加1亿阈值线（橙色虚线，🔥标识）
- 添加1.5亿阈值线（红色虚线，💥标识）
- 优化标签样式，带背景和圆角
- 增加线条宽度为2，提升可见性

Files changed: 1 file
- templates/panic_new.html (+49 insertions, -4 deletions)
```

## 访问地址

- **Panic页面**: https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/panic
- **1小时爆仓API**: https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/api/panic/hour1-curve
- **最新数据API**: https://5000-iehbqwjte74vmohs308jg-d0b9e1e2.sandbox.novita.ai/api/panic/latest

## 后续优化建议

### 1. 动态阈值调整
允许用户自定义阈值：
```javascript
// 在页面添加设置面板
const thresholds = {
    warning: localStorage.getItem('threshold_warning') || 5000,
    danger: localStorage.getItem('threshold_danger') || 10000,
    critical: localStorage.getItem('threshold_critical') || 15000
};
```

### 2. 阈值突破提醒
当数据突破阈值时发送通知：
```javascript
if (currentAmount >= 15000 && !notified) {
    showNotification('💥 1小时爆仓金额突破1.5亿！', 'critical');
    notified = true;
}
```

### 3. 阈值区间着色
为不同区间设置背景色：
```javascript
visualMap: {
    show: false,
    pieces: [
        {gte: 15000, color: '#ef4444'},  // >1.5亿：红色
        {gte: 10000, lte: 15000, color: '#f97316'},  // 1-1.5亿：橙色
        {gte: 5000, lte: 10000, color: '#fbbf24'},  // 5000万-1亿：黄色
        {lt: 5000, color: '#10b981'}  // <5000万：绿色
    ]
}
```

### 4. 统计信息
显示触达各阈值的频率：
```javascript
const stats = {
    above5000: data.filter(d => d.hour_1_amount >= 5000).length,
    above10000: data.filter(d => d.hour_1_amount >= 10000).length,
    above15000: data.filter(d => d.hour_1_amount >= 15000).length
};
console.log(`24小时内：突破5000万 ${stats.above5000}次，1亿 ${stats.above10000}次，1.5亿 ${stats.above15000}次`);
```

## 结论

✅ **功能已实现**:
- 三条阈值虚线清晰可见
- 颜色和标签符合预期
- 与现有功能完美兼容

✅ **用户价值**:
- 快速判断市场状态
- 直观的视觉参考
- 辅助交易决策

✅ **技术质量**:
- 代码简洁高效
- ECharts配置标准
- 易于维护和扩展

---

**文档版本**: 1.0  
**创建日期**: 2026-02-06  
**最后更新**: 2026-02-06 18:30  
**作者**: Claude  
